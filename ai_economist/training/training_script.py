# Copyright (c) 2021, salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause

"""
Example training script for the grid world and continuous versions of Tag.
Note: This training script only runs on a GPU machine.
You will also need to install WarpDrive (https://github.com/salesforce/warp-drive)
using `pip install rl-warp-drive`, and Pytorch(https://pytorch.org/)
"""

import argparse
import os
from re import S

import GPUtil

from ai_economist.foundation.scenarios import simple_wood_and_stone

try:
    num_gpus_available = len(GPUtil.getAvailable())
    assert num_gpus_available > 0, "This training script needs a GPU to run!"
    print(f"Inside training_script.py: {num_gpus_available} GPUs are available.")
    import torch
    import yaml
    from warp_drive.training.trainer import Trainer
    from warp_drive.utils.env_registrar import EnvironmentRegistrar
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "This training script requires the 'WarpDrive' package, please run "
        "'pip install rl-warp-drive' first."
    ) from None
except ValueError:
    raise ValueError("This training script needs a GPU to run!") from None

from ai_economist.foundation.env_wrapper import FoundationEnvWrapper
from ai_economist.foundation.base.base_env import scenario_registry as s


pytorch_cuda_nit_success = torch.cuda.FloatTensor(8)
MORAL_ECONOMY = "moral_economy"
SIMPLE_WOOD_AND_STONE = "simple_wood_and_stone"
# Usage:
# >> python ai_economist/training/training_script.py --env simple_wood_and_stone


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--env", "-e", type=str, help="Environment to train.")

    args = parser.parse_args()

    # Read the run configurations specific to each environment.
    # Note: The run config yamls are located at warp_drive/training/run_configs
    # ---------------------------------------------------------------------------
    assert args.env in [MORAL_ECONOMY, SIMPLE_WOOD_AND_STONE], (
        f"Currently, the only environment supported "
        f"is {MORAL_ECONOMY}, {SIMPLE_WOOD_AND_STONE}"
    )

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "run_configs",
        f"{args.env}.yaml",
    )
    with open(config_path, "r", encoding="utf8") as f:
        run_config = yaml.safe_load(f)

    num_envs = run_config["trainer"]["num_envs"]

    # Create a wrapped environment object via the EnvWrapper
    # Ensure that use_cuda is set to True (in order to run on the GPU)
    # ----------------------------------------------------------------
    if run_config["name"] == MORAL_ECONOMY:
        env_registry = EnvironmentRegistrar()
        this_file_dir = os.path.dirname(os.path.abspath(__file__))
        MoralUniform = s.get('moral_uniform/simple_wood_and_stone')
        env_registry.add_cuda_env_src_path(
            MoralUniform.name,
            os.path.join(
                this_file_dir, "../foundation/scenarios/covid19/covid19_build.cu"
            ),
        )
        env_wrapper = FoundationEnvWrapper(
            MoralUniform(**run_config["env"]),
            num_envs=num_envs,
            use_cuda=True,
            customized_env_registrar=env_registry,
        )
    elif run_config["name"] == SIMPLE_WOOD_AND_STONE:
        env_registry = EnvironmentRegistrar()
        this_file_dir = os.path.dirname(os.path.abspath(__file__))
        
        uniform = s.get('uniform/simple_wood_and_stone')
        env_registry.add_cuda_env_src_path(
            uniform.name,
            os.path.join(
                this_file_dir, "../foundation/scenarios/covid19/covid19_build.cu"
            ),
        )
        env_wrapper = FoundationEnvWrapper(
            uniform(**run_config["env"]),
            num_envs=num_envs,
            use_cuda=True,
            customized_env_registrar=env_registry,
        )
    else:
        raise NotImplementedError

    # The policy_tag_to_agent_id_map dictionary maps
    # policy model names to agent ids.
    # ----------------------------------------------------
    policy_tag_to_agent_id_map = {
        "a": [str(agent_id) for agent_id in range(env_wrapper.env.n_agents)],
        "p": ["p"],
    }

    # Flag indicating whether separate obs, actions and rewards placeholders
    # have to be created for each policy.
    # Set "create_separate_placeholders_for_each_policy" to True here
    # since the agents and planner have different observation
    # and action spaces.
    separate_placeholder_per_policy = True

    # Flag indicating the observation dimension corresponding to
    # 'num_agents'.
    # Note: WarpDrive assumes that all the observation are shaped
    # (num_agents, *feature_dim), i.e., the observation dimension
    # corresponding to 'num_agents' is the first one. Instead, if the
    # observation dimension corresponding to num_agents is the last one,
    # we will need to permute the axes to align with WarpDrive's assumption
    obs_dim_corresponding_to_num_agents = "last"

    # Trainer object
    # --------------
    trainer = Trainer(
        env_wrapper=env_wrapper,
        config=run_config,
        policy_tag_to_agent_id_map=policy_tag_to_agent_id_map,
        create_separate_placeholders_for_each_policy=separate_placeholder_per_policy,
        obs_dim_corresponding_to_num_agents=obs_dim_corresponding_to_num_agents,
    )

    # Perform training
    # ----------------
    trainer.train()
    trainer.graceful_close()
