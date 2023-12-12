import sys
from utils.input_parser import DATParser
from utils.AMMMGlobals import AMMMException
# from InstanceGeneratorP2.ValidateConfig import ValidateConfig
from generator import InstanceGenerator


def run():
    try:
        config_file = "config/config.dat"
        print("Instance Generator")
        print("-----------------------")
        print("Reading Config file %s..." % config_file)
        config = DATParser.parse(config_file)
        # ValidateConfig.validate(config)
        print("Creating Instances...")
        generator = InstanceGenerator(config)
        generator.generate()
        print("Done")
        return 0
    except AMMMException as e:
        print("Exception: %s", e)
        return 1


if __name__ == '__main__':
    sys.exit(run())

