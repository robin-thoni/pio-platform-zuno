from os.path import join
import os
from SCons.Script import AlwaysBuild, Builder, Command, Default, DefaultEnvironment


env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-zuno2")
TOOLCHAIN_DIR = platform.get_package_dir("toolchain-gccarmnoneeabi")
ZME_DIR = platform.get_package_dir("toolchain-zme_make")
LIBCLANG_DIR = platform.get_package_dir("toolchain-libclang")

ADDITIONAL_SOURCES_DIRS = [
    "$PROJECT_SRC_DIR/esphome",
    join(FRAMEWORK_DIR, "cores"),
    # '$PROJECT_LIBDEPS_DIR',
]

env.Append(
    TOOLCHAIN_DIR=TOOLCHAIN_DIR,
    ADDITIONAL_SOURCES_DIRS=ADDITIONAL_SOURCES_DIRS,
    ADDITIONAL_SOURCES_DIRS_ARG="-S " + " -S ".join(ADDITIONAL_SOURCES_DIRS),
    GCC_BIN_DIR=join(TOOLCHAIN_DIR, "bin"),
    LIBCLANG_DIR=LIBCLANG_DIR,
    ZME_DIR=ZME_DIR,
    ZME_MAKE=join("$ZME_DIR", "zme_make"),
    BUILDERS=dict(
        ZmeMakeBuild=Builder(
            action="$ZME_MAKE build $SOURCE $ADDITIONAL_SOURCES_DIRS_ARG -B $BUILD_DIR -T $GCC_BIN_DIR -lcl $LIBCLANG_DIR"
        ),
    ),
)

build = env.ZmeMakeBuild(
    join("$BUILD_DIR", "main/main_ino_signed.bin"), join("$PROJECT_SRC_DIR", "main.cpp")
)


upload = env.Alias(
    "upload",
    build,
    "$ZME_MAKE upload $PROJECT_SRC_DIR/main.cpp -B $BUILD_DIR -d /dev/ttyUSB3",
)
AlwaysBuild(upload)

Default(build)

# print(env.Dump())
