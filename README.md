# Agbot Farm Simulation (Agbot-Sim)
Used in experiments for **"Examining Audio Communication Mechanisms for Supervising Fleets of Agricultural Robots"** publication (@RO-MAN 2022)

Agbot fleet farm simulation built on the [Multi-Agent Gridworld Environment](https://github.com/ArnaudFickinger/gym-multigrid)

Requirements:
- Python 3.5+
- OpenAI Gym
- NumPy
- Matplotlib

more info will be filled out in readme soon...

Contact akamboj2@illinois.edu for any questions
## Overview:
farm_speech.py: contains an interface with functions that outputs or inputs audio. It uses packages, beepy, chime and speech_recognition.

auto_farm_process.py: contains the main function that uses a the Controller class, to instatiate multiple processes (one for each robot) and run the simulation.

gym_multigrid/ : modified version of [Multi-Agent Gridworld Environment](https://github.com/ArnaudFickinger/gym-multigrid)

earcons/ spearcons/: the earcons and spearcons were prechosen and saved to help speed up the runtime

## Setup

Create conda environment with dependencies:
```
conda env create -f environment.yml
```
Activate environemnt
```
conda activate speech
```
```
sh pip_setup.sh
```
## Running the script
```
python auto_farm_process.py --level 3 --sound word
```
The --level flag allows a user to use different environments. See bottom of gym_multigrid/envs/farm_env.py for configuration. We use --level 3 in our experiments, and currently only levels 1-3 are implmented.

The --sound flag changes how the robot is communicating with the human. It can be set to 'sound' (earcon), 'word' (phrase) and 'full' (sentences). We vary this across our experiments.

The --interface flag set to 'gui' allows the user to communicate with the robots through a GUI instead of audio input. Helpful for testing and debugging the simulation without audio. We always used the default 'not-gui' in our experiments

