cd ~/ai-ethicist/ai_economist/training/rllib/


echo "Amoral?"
select yn in "Yes_layout" "Yes_rand" "No"; do
  case $yn in
    Yes_layout ) python training_script.py --run-dir envs/amoral/layout/ > envs/amoral/layout/logfile.txt 2>&1&;;
    Yes_rand ) python training_script.py --run-dir envs/amoral/random/ > envs/amoral/random/logfile.txt 2>&1&;;
    No ) exit;;
  esac
  break;
done

echo "Virtue Ethics?"
select yn in "Yes_layout" "Yes_rand" "No"; do
  case $yn in
    Yes_layout ) python training_script.py --run-dir envs/virtue_ethics/layout/ >envs/virtue_ethics/layout/logfile.txt 2>&1&;;
    Yes_rand ) python training_script.py --run-dir envs/virtue_ethics/random/ > envs/virtue_ethics/random/logfile.txt 2>&1&;;
    No ) exit;;
  esac
  break;
done

echo "utilitarian?"
select yn in "Yes_layout" "Yes_rand" "No"; do
  case $yn in
    Yes_layout ) python training_script.py --run-dir envs/utilitarian/layout/ > envs/utilitarian/layout/logfile.txt 2>&1&;;
    Yes_rand ) python training_script.py --run-dir envs/utilitarian/random/ > envs/utilitarian/random/logfile.txt 2>&1&;;
    No ) exit;;
  esac
  break;
done

echo "default?"
select yn in "Yes" "No"; do
  case $yn in
    Yes ) python training_script.py --run-dir envs/og/phase1/ > envs/og/phase1/logfile.txt 2>&1&;;
    No ) exit;;
  esac
  break;
done