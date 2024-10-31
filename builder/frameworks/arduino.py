from os.path import join
from SCons.Script import DefaultEnvironment, SConscript, COMMAND_LINE_TARGETS

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

# print(board)

# print(COMMAND_LINE_TARGETS, env.get("PROGNAME"))

# FRAMEWORK_DIR = platform.get_package_dir("framework-z_uno")

# print(FRAMEWORK_DIR)