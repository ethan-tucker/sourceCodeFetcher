import unittest
from unittest import mock
import sys
import filecmp
import fetchSource
from contextlib import contextmanager
from io import StringIO
from collections import OrderedDict
import os


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


boards_dict = OrderedDict(
        [("cypress", ["CY8CKIT_064S0S2_4343W", "CYW943907AEVAL1F",
                        "CYW954907AEVAL1F"]),
            ("espressif", ["esp32"]),
            ("infineon", ["xmc4800_iotkit",
                            "xmc4800_plus_optiga_trust_x"]),
            ("marvell", ["mw300_rd"]),
            ("mediatek", ["mt7697hx-dev-kit"]),
            ("microchip", ["curiosity_pic32mzef",
                            "ecc608a_plus_winsim"]),
            ("nordic", ["nrf52840-dk"]),
            ("nuvoton", ["numaker_iot_m487_wifi"]),
            ("nxp", ["lpc54018iotmodule"]),
            ("pc", ["linux", "windows"]),
            ("renesas", ["rx65n-rsk"]),
            ("st", ["stm32l475_discovery"]),
            ("ti", ["cc3220_launchpad"]),
            ("xilinx", ["microzed"])])


class TestFetchSource(unittest.TestCase):
    @mock.patch('fetchSource.input', create=True)
    # validate that I can enter in incorrect values and then a correct
    # value and the correct value will be returned
    def test_validateUserInput(self, mocked_input):
        mocked_input.side_effect = ['0', '5', 'e', '2']

        res = fetchSource.getValidUserInput(["Option 1", "Option 2",
                                            "Option 3"], 3, "Choose an option")

        self.assertEqual(res, 'Option 2')

    @mock.patch('fetchSource.input', create=True)
    def test_boardChoiceMenu(self, mocked_input):
        mocked_input.side_effect = ['0', '15', 'e', '2', '0', '5', 'e', '1']

        actual_output_filepath = "testOutputActual/boardChoiceMenu1"
        expected_output_filepath = "testOutputExpected/boardChoiceMenu1"
        with captured_output() as (out, err),\
             open(actual_output_filepath, 'w') as realOutput:

            res = fetchSource.boardChoiceMenu(boards_dict)
            output = out.getvalue().strip()
            realOutput.write(output)

        self.assertTrue(filecmp.cmp(actual_output_filepath,
                                    expected_output_filepath), 'files diffed')

        self.assertEqual(res, ("espressif", "esp32"))

    def test_setLibraryDefaults(self):
        actual_output_filepath = ".config"
        expected_output_filepath = "testOutputExpected/setLibraryDefaults"

        fetchSource.setLibraryDefaults("espressif", "esp32")

        self.assertTrue(filecmp.cmp(actual_output_filepath,
                        expected_output_filepath), 'files diffed')

    def test_setLibraryDefaults2(self):
        actual_output_filepath = ".config"
        expected_output_filepath = "testOutputExpected/setLibraryDefaults2"

        fetchSource.setLibraryDefaults("nuvoton", "numaker_iot_m487_wifi")

        self.assertTrue(filecmp.cmp(actual_output_filepath,
                        expected_output_filepath), 'files diffed')

    def test_findAllKConfigFiles(self):
        # This test will only pass if the afr_KConfig repo has been cloned
        output_dir_name = "afr_Kconfig"
        os.chdir("../../" + output_dir_name +
                 "/amazon-freertos/tools/configuration")

        expected_list = ["../../vendors/espressif/boards/esp32\\Kconfig",
                         "../../vendors/espressif/boards/esp32/aws_demos" +
                         "/config_files\\FreeRTOSIP_Kconfig",
                         "../../vendors/espressif/boards/esp32/aws_demos" +
                         "/config_files\\mqtt_Kconfig",
                         "../../vendors/espressif/boards/esp32/aws_demos" +
                         "/config_files\\ota_Kconfig"]

        KConfig_list = fetchSource.findAllKConfigFiles("espressif", "esp32")
        os.chdir("../../../../sourceFetcher/source")

        self.assertEquals(expected_list, KConfig_list)

    def test_findAllKConfigFiles2(self):
        # This test will only pass if the afr_KConfig repo has been cloned
        output_dir_name = "afr_Kconfig"
        os.chdir("../../" + output_dir_name +
                 "/amazon-freertos/tools/configuration")

        expected_list = ["../../vendors/nuvoton/boards/numaker_iot_m487_wifi" +
                         "\\Kconfig",
                         "../../vendors/nuvoton/boards/numaker_iot_m487_wifi" +
                         "/aws_demos/config_files\\FreeRTOSIP_Kconfig",
                         "../../vendors/nuvoton/boards/numaker_iot_m487_wifi" +
                         "/aws_demos/config_files\\mqtt_Kconfig"]

        KConfig_list = fetchSource.findAllKConfigFiles("nuvoton",
                                                       "numaker_iot_m487_wifi")
        os.chdir("../../../../sourceFetcher/source")

        self.assertEquals(expected_list, KConfig_list)

    def test_findAllKConfigFiles3(self):
        # This test will only pass if the afr_KConfig repo has been cloned
        output_dir_name = "afr_Kconfig"
        os.chdir("../../" + output_dir_name +
                 "/amazon-freertos/tools/configuration")

        expected_list = []

        KConfig_list = fetchSource.findAllKConfigFiles("vendor", "board")
        os.chdir("../../../../sourceFetcher/source")

        self.assertEquals(expected_list, KConfig_list)

    def test_updatedBoardChosen(self):
        fetchSource.updateBoardChosen("espressif", "esp32", "afr_Kconfig")
        os.chdir("../../../../sourceFetcher/source")
        expected_board_choice_filepath = "testOutputExpected/boardChoice1"
        expected_board_config_filepath = "testOutputExpected/updateBoardChosen"

        actual_board_choice_filepath = ("../../afr_Kconfig/amazon-freertos" +
                                        "/tools/configuration/boardChoice.csv")
        actual_board_config_filepath = ("../../afr_Kconfig/amazon-freertos" +
                                        "/tools/configuration/.config")

        self.assertTrue(filecmp.cmp(expected_board_choice_filepath,
                        actual_board_choice_filepath))

        self.assertTrue(filecmp.cmp(expected_board_config_filepath,
                        actual_board_config_filepath))

    def test_updatedBoardChosen2(self):
        fetchSource.updateBoardChosen("nuvoton", "numaker_iot_m487_wifi",
                                      "afr_Kconfig")
        os.chdir("../../../../sourceFetcher/source")
        expected_board_choice_filepath = "testOutputExpected/boardChoice2"
        expected_board_config_filepath = ("testOutputExpected/" +
                                          "updateBoardChosen2")

        actual_board_choice_filepath = ("../../afr_Kconfig/amazon-freertos" +
                                        "/tools/configuration/boardChoice.csv")
        actual_board_config_filepath = ("../../afr_Kconfig/amazon-freertos" +
                                        "/tools/configuration/.config")

        self.assertTrue(filecmp.cmp(expected_board_choice_filepath,
                        actual_board_choice_filepath))

        self.assertTrue(filecmp.cmp(expected_board_config_filepath,
                        actual_board_config_filepath))
                        

    def test_enableLibraries(self):

        # Choose a consistent board so that the test does not depend on the 
        # current state of the .config file
        fetchSource.setLibraryDefaults("espressif", "esp32")

        expected_output_filepath = "testOutputExpected/enableLibrariesOutput1"
        fetchSource.enableLibraries()

        self.assertTrue(filecmp.cmp(expected_output_filepath, ".config"))

    def test_enableLibraries2(self):

        # Choose a consistent board so that the test does not depend on the 
        # current state of the .config file
        fetchSource.setLibraryDefaults("nuvoton", "numaker_iot_m487_wifi")

        expected_output_filepath = "testOutputExpected/enableLibrariesOutput2"
        fetchSource.enableLibraries()

        self.assertTrue(filecmp.cmp(expected_output_filepath, ".config"))

    @mock.patch('fetchSource.input', create=True)
    def test_getOutputDir(self, mocked_input):
        testing_input = 'testing'
        mocked_input.side_effect = [testing_input]
        output_dir = fetchSource.getOutputDirectory()

        self.assertEqual(testing_input, output_dir)

if __name__ == '__main__':
    unittest.main()
