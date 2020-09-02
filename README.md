## Overview
This script allows FreeRTOS customers to enable/disable libraries before
cloning the FreeRTOS source code. This allows for smaller download sizes
that are more catered to the users needs.

## Dependencies
For this tool to run properly you must first install python3 and
kconfiglib.
### Installing python3
Installing python3 can be done here: https://www.python.org/downloads/.
You can verify your download by opening terminal and running 
"python3 --version".
### Installing kconfiglib
The kconfiglib README.md can be found here:
https://github.com/ulfalizer/Kconfiglib. To install kconfiglib run the
command "pip(3) install kconfiglib". The command depends on the current
version of pip that is currently available on your machine

## Cloning the installer script
Navigate to the directory where you want the repo to be located. This
script should be cloned like so: 
"git clone https://github.com/ethan-tucker/sourceCodeFetcher.git". This
will clone the repo into whatever folder you have created without creating
an additional file layer.

## Script Functionality
1. First the script will ask the user to choose a board. This is to set
the defaults based on which libraries are typically supported for that
board.
2. The user will be asked to enable/disable libraries. After choosing
the set of libraries they want to have enabled the user should save and
exit the GUI.
3. The user will be prompted to enter the name of the directory they want
the code to be clone into.
4. The code will be cloned in the directory named by the user. The code is
pulled from the this repo: https://github.com/ethan-tucker/amazon-freertos/tree/master.
The current configuration script lives in the EthanDev branch.
5. After the code is cloned, the FreeRTOS repository will be slightly
modified to represent the board chosen by the user.
6. The configuration script will then be run. This script can be viewed here:
https://github.com/ethan-tucker/amazon-freertos/blob/EthanDev/tools/configuration/configure.py