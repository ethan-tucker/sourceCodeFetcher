from collections import OrderedDict
import sys
import subprocess
import os
import glob


# This script is a porion of the configure.py located in the amazon-freertos/tools/configuration directory.
# It has been abstracted to allow users to disable/enable libraries before cloning the source code in the hopes
# that this will allow their downloads to be smaller by not downloading libararies that they don't need.


# getValidUserInput: Validates that the numbered selected the user makes is:
#   1) a number
#   2) within a valid range (based on the number of total options)
# This is used by both the getBoardChoice function and the getVenderChoice function
def getValidUserInput(options, max_acceptable_value, error_message):
    user_input = input("\n%s (by number): "%(error_message))
    # This loop will run until the user has entered a valid selection. At that point the function will return the name of the board chosen.
    while 1:
        # Confirms that the user entered a digit
        if(user_input.isdigit()):
            user_input_int = int(user_input)
            # Given the user entered a digit, make sure that the number is within an acceptable range
            if(user_input_int < 1 or user_input_int > max_acceptable_value):
                user_input = input("\n%s (please enter a valid number): "%(error_message))
            else:
                return options[user_input_int-1]
        else:
            user_input = input("\n%s (please enter a number): "%(error_message))


# getBoardChoice: Prints all of the possible boards options that the user can select from. It then calls
# getValidUserInput to makes sure that they made a valid selection.
def getBoardChoice(boards):
    print("\n-----CHOOSE A BOARD-----\n")
    
    for idx, board in enumerate(boards, start=1):
        print("%s) %s" %(idx, board))
    
    return getValidUserInput(boards, len(boards), "Select your board")


# getVendorChoice: This function prints all of the possible vendor options that the user can select from. It then calls
# getValidUserInput to makes sure that they made a valid selection.
def getVendorChoice(boards_dict):
    print("\n-----CHOOSE A VENDOR-----\n")

    # vendors in a list of touples. The first item in each touple is the vendor and the second item is a list of boards corresponding to that vendor
    vendors = list(boards_dict.items())
    for idx, vendor in enumerate(vendors, start=1):
        print("%s) %s" %(idx, vendor[0]))
    
    return getValidUserInput(vendors, len(vendors), "Select your vendor")


# boardChoiceMenu: calls getVendorChoice followed by getBoardChoice and echos the user choice to the terminal
def boardChoiceMenu(boards_dict):
    vendor = getVendorChoice(boards_dict)
    vendor_name = vendor[0]
    boards = vendor[1]
    board = getBoardChoice(boards)
    
    print("\n-----YOUR BOARD CHOICE-----\n")
    print("Your choice was the %s %s"%(vendor_name, board))
    return (vendor_name, board)


# setLibraryDefaults: Runs merge_config on the default configuration located in KConfig with the defaults for the
# board the user chose located at '"../vendors/" + vendor_name + "/" + board + "/KConfig"'. This merged configuration
# is what is inevitably shown to the user in the GUI.
def setLibraryDefaults(vendor_name, board):
    board_default_properties = "../vendors/" + vendor_name + "/" + board + "/KConfig"
    subprocess.run(["py","merge_config.py", "KConfig", ".config", board_default_properties])


# enableLibraries: Calls guiconfig which is what takes the Kconfig fill and presents the user with a GUI with the
# possible configuration options
def enableLibraries():
    subprocess.run(["guiconfig"])


# getOutputDirectory: Asks the user to name the directory that the FreeRTOS source code will end up cloning in to. 
def getOutputDirectory():
    print("\n-----Choosing output folder name-----\n")
    output_dir = input("What would you like the output folder to be called: ")
    return output_dir


# cloneFreeRTOSRepository: changes directories outside the scope of this scripts directory and clones the FreeRTOS
# source code.
def cloneFreeRTOSRepository(output_dir_name):
    print("\n-----Cloning FreeRTOS Repository-----\n")
    sys.stdout.flush()

    # change directories so that the freertos repo is cloned outside the scope of this repo
    os.chdir("../..")
    subprocess.run(["git", "clone", "https://github.com/ethan-tucker/amazon-freertos.git", "--recurse-submodules", output_dir_name])
    os.chdir("sourceFetcher/source")


# updateBoardChosen: Now that the user has chosen a board and cloned the repo the repository must be modified slightly
# to represent the board that the user has chosen. This function updates the ".config" and "boardChoice.csv" to 
# indicate the board choice that the user has made.
def updateBoardChosen(vendor, board, output_dir_name):
    os.chdir("../../" + output_dir_name + "/amazon-freertos/tools/configuration")

    command = ["py","merge_config.py", "KConfig", ".config"]

    config_files = findAllKConfigFiles(vendor, board)
    for file in config_files:
        command.append(file)
    
    # merg_config.py runs merge config with all of the configruation files associated with the chosen board. This created a heirarchy of defaults in which
    # the values assigned int the board configuration files take precedence over those set in the library files (these are included in the file "KConfig").
    # The output of this process is the .config file. This is the intermediate step. When the genconfig command is run it uses this .config file to generate 
    # a new KConfig.h file.
    print("\n-----MERGING CONFIGURATIONS FOR YOUR BOARD-----\n")
    sys.stdout.flush()
    subprocess.run(command)
    print()
    
    with open("boardChoice.csv", "w") as board_chosen_file:
        board_chosen_file.write(vendor + "," + board)


# callConfigurationScript: This calls the original configuration script allowing the user to configure the FreeRTOS code as well
# as provision AWS resources and build and run their demo of choice.
def callConfigurationScript():
    subprocess.run(["py", "configure.py"])


# findAllKConfigFiles: Globs the boards directory tree for Kconfig files. Globbing for files matching a pattern allows for 
# future files to be added without the code needing to be changed. It also doesn't break if certain boards do not have all 
# of the configuration files (for example some boards wont have ota_agent_config.h).
def findAllKConfigFiles(vendor, board):
    board_properties = "../../vendors/" + vendor + "/boards/" + board + "/*Kconfig"
    library_configs = "../../vendors/" + vendor + "/boards/" + board + "/aws_demos/config_files/*Kconfig"
    KconfigFilenamesList = glob.glob(board_properties) + glob.glob(library_configs)

    return KconfigFilenamesList
    

def main():
    # I used an ordered dict here so that it was easy to use/index as well as easy to add new vendor board combos.
    boards_dict = OrderedDict(
             [("cypress", ["CY8CKIT_064S0S2_4343W","CYW943907AEVAL1F","CYW954907AEVAL1F"]), 
              ("espressif", ["esp32"]), 
              ("infineon", ["xmc4800_iotkit","xmc4800_plus_optiga_trust_x"]), 
              ("marvell", ["mw300_rd"]), 
              ("mediatek", ["mt7697hx-dev-kit"]), 
              ("microchip", ["curiosity_pic32mzef","ecc608a_plus_winsim"]),
              ("nordic", ["nrf52840-dk"]), 
              ("nuvoton", ["numaker_iot_m487_wifi"]), 
              ("nxp", ["lpc54018iotmodule"]), 
              ("pc", ["linux","windows"]), 
              ("renesas", ["rx65n-rsk"]), 
              ("st", ["stm32l475_discovery"]), 
              ("ti", ["cc3220_launchpad"]), 
              ("xilinx", ["microzed"])])

    board_chosen = boardChoiceMenu(boards_dict)
    vendor = board_chosen[0]
    board = board_chosen[1]
    setLibraryDefaults(vendor, board)

    enableLibraries()

    output_dir_name = getOutputDirectory()

    cloneFreeRTOSRepository(output_dir_name)

    updateBoardChosen(vendor, board, output_dir_name)
    
    callConfigurationScript()


if __name__=="__main__": 
    main() 