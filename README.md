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