from collections import OrderedDict
import sys
import subprocess
import os


def getValidUserInput(options, max_acceptable_value, error_message):
    user_input = input("\n%s (by number): "%(error_message))
    # This loop will run until the user has entered a valid selection. At that point the function will return the name of the board chosen.
    while 1:
        if(user_input.isdigit()):
            user_input_int = int(user_input)
            if(user_input_int < 1 or user_input_int > max_acceptable_value):
                user_input = input("\n%s (please enter a valid number): "%(error_message))
            else:
                return options[user_input_int-1]
        else:
            user_input = input("\n%s (please enter a number): "%(error_message))


def getBoardChoice(boards):
    print("\n-----CHOOSE A BOARD-----\n")
    
    for idx, board in enumerate(boards, start=1):
        print("%s) %s" %(idx, board))
    
    return getValidUserInput(boards, len(boards), "Select your board")


def getVendorChoice(boards_dict):
    print("\n-----CHOOSE A VENDOR-----\n")

    # vendors in a list of touples. The first item in each touple is the vendor and the second item is a list of boards corresponding to that vendor
    vendors = list(boards_dict.items())
    for idx, vendor in enumerate(vendors, start=1):
        print("%s) %s" %(idx, vendor[0]))
    
    return getValidUserInput(vendors, len(vendors), "Select your vendor")


def boardChoiceMenu(boards_dict):
    vendor = getVendorChoice(boards_dict)
    vendor_name = vendor[0]
    boards = vendor[1]
    board = getBoardChoice(boards)
    
    print("\n-----YOUR BOARD CHOICE-----\n")
    print("Your choice was the %s %s"%(vendor_name, board))
    return (vendor_name, board)


def setLibraryDefaults(vendor_name, board):
    board_default_properties = "../vendors/" + vendor_name + "/" + board + "/KConfig"

    subprocess.run(["py","merge_config.py", "KConfig", ".config", board_default_properties])


def enableLibraries():
    subprocess.run(["guiconfig"])


def getOutputDirectory():
    print("\n-----Choosing output folder name-----\n")
    output_dir = input("What would you like the output folder to be called: ")
    return output_dir


def cloneFreeRTOSRepository(output_dir_name):
    print("\n-----Cloning FreeRTOS Repository-----\n")
    sys.stdout.flush()

    # change directories so that the freertos repo is cloned outside the scope of this repo
    os.chdir("../..")
    subprocess.run(["git", "clone", "https://github.com/ethan-tucker/amazon-freertos.git", "--recurse-submodules", output_dir_name])
    os.chdir("sourceFetcher/source")

def updateBoardChosen(vendor, board, output_dir_name):
    os.chdir("../../" + output_dir_name + "/amazon-freertos/tools/configuration")
    with open("boardChoice.csv", "w") as board_chosen_file:
        board_chosen_file.write(vendor + "," + board)


def callConfigurationScript():
    subprocess.run(["py", "configure.py"])


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