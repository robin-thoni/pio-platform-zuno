from os.path import join
import os
from SCons.Script import AlwaysBuild, Builder, Command, Default, DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-z_uno")
TOOLCHAIN_DIR = platform.get_package_dir("toolchain-z_uno")
CC_DIR = join(TOOLCHAIN_DIR, 'gcc/bin')
CC_PREFIX = 'arm-none-eabi-'

libraries = [ f.path for f in os.scandir(join(FRAMEWORK_DIR, "libraries")) if f.is_dir() ]
cores_libraries = [ f.path for f in os.scandir(join(FRAMEWORK_DIR, "cores")) if f.is_dir() ]

# A full list with the available variables
# http://www.scons.org/doc/production/HTML/scons-user.html#app-variables
env.Replace(
    AR=join(CC_DIR, f'{CC_PREFIX}ar'),
    AS=join(CC_DIR, f'{CC_PREFIX}gcc'),
    CC=join(CC_DIR, f'{CC_PREFIX}gcc'),
    CXX=join(CC_DIR, f'{CC_PREFIX}g++'),
    OBJCOPY=join(CC_DIR, f'{CC_PREFIX}objcopy'),
    RANLIB=join(CC_DIR, f'{CC_PREFIX}ranlib'),

    UPLOADER=join(TOOLCHAIN_DIR, 'zme_make/zme_make'),
    UPLOADCMD="$UPLOADER bin_upload $SOURCES -d /dev/ttyUSB0"
)

COMMON_FLAGS = [
        '-mthumb',
        '-Os',
        '-fdata-sections',
        '-ffunction-sections',
        '-fno-rtti',
        '-fno-exceptions',
        '-mcpu=cortex-m4',
    ]

INCLUDE_FLAGS = [
        "-I", join("$BUILD_DIR", "zuno_preproc"),
        "-I", join(FRAMEWORK_DIR, "cores"),
    ] + [
        l for x in cores_libraries for l in ('-I', x)
    ] + [
        "-I", join(FRAMEWORK_DIR, "libraries"),
    ] + [
        l for x in libraries for l in ('-I', x)
    ] + [
        "-I", join(TOOLCHAIN_DIR, "gcc/lib/gcc/arm-none-eabi/7.2.1/include"),
        # "-I", join(TOOLCHAIN_DIR, "inc"),
    ]

env.Append(
    # ARFLAGS=["..."],

    # ASFLAGS=["flag1", "flag2", "flagN"],
    # CCFLAGS=["flag1", "flag2", "flagN"],
    CCFLAGS=[
        '-x', 'c++',
    ] + COMMON_FLAGS + INCLUDE_FLAGS,
    CXXFLAGS=COMMON_FLAGS + INCLUDE_FLAGS,
    LINKFLAGS=[
        '-mthumb',
        '-Os',
        '-mcpu=cortex-m4',
        '-T', join(FRAMEWORK_DIR, "cores/ZUNO_LNK.ld"),
        '--specs=nano.specs',
        '-Wl,--gc-sections',
    ],

    # CPPDEFINES=["DEFINE_1", "DEFINE=2", "DEFINE_N"],

    # LIBS=["additional", "libs", "here"],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"]),
            suffix=".bin"
        ),
        ElfToHex=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "$SOURCES",
                "$TARGET"]),
            suffix=".bin"
        )
    )
)

libs = []

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkZUno"),
    join(FRAMEWORK_DIR, "cores"),
    ["+<*>", "-<.git%s>" % os.sep, "-<.svn%s>" % os.sep, "-<Crtx>", "-<emlib>", "+<emlib/em_gpio.c>", "+<emlib/em_usart.c>", "+<emlib/em_cmu.c>", "+<emlib/system_zgm13.c>"]
))

env.Prepend(LIBS=libs)

# print(env.Dump())



# The source code of "platformio-build-tool" is here
# https://github.com/platformio/platformio-core/blob/develop/platformio/builder/tools/platformio.py

#
# Target: Build executable and linkable firmware
#
target_elf = env.BuildProgram()

#
# Target: Build the .bin file
#
target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware.bin"), target_elf)
target_hex = env.ElfToHex(join("$BUILD_DIR", "firmware.hex"), target_elf)

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_hex, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#
Default(target_bin)
