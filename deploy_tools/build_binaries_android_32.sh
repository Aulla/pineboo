#!/bin/bash
TARGET="android-32"
SYSROOT=""
LOCALDIR="$(pwd)"
export ANDROID_SDK_ROOT=~/Android/Sdk
export ANDROID_NDK_ROOT=$LOCALDIR/src/android-ndk-r19c
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
export PATH=$PATH:$ANDROID_SDK_ROOT/tools
export PATH=$PATH:$ANDROID_NDK:$ANDROID_NDK_ROOT/build
export ANDROID_NDK_PLATFORM=android-24
export ANDROID_NDK_TOOLCHAIN_VERSION=4.9
export JAVA_HOME=/usr/lib/jvm/java-8-oracle
export TOOLCHAIN_PREFIX=$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/arm-linux-androideabi/bin

if [ -e "sysroots/$TARGET" ]; then
SYSROOT="--no-sysroot"
else

if [ ! -e "sysroots" ]; then
mkdir sysroots
fi


if [ ! -e "sysroots/extra_libs" ]; then
mkdir sysroots/extra_libs
fi

if [ ! -e "sysroots/extra_libs/$TARGET" ]; then
mkdir sysroots/extra_libs/$TARGET
fi

cd sysroots/extra_libs/$TARGET
if [ ! -e "sqlite3" ] ; then
git clone https://github.com/stockrt/sqlite3-android sqlite3
cd sqlite3
make
cd ..
fi

if [ ! -e "bzip2" ] ; then
git clone https://github.com/dmcrystax/cosp-android-bzip2 bzip
cd bzip
build.sh $ANDROID_NDK_ROOT --prefix=./lib
cd ..   
fi

cd ..
cd ..
cd ..

fi

python3 ./build-pineboo-binaries.py --target $TARGET $SYSROOT --verbose
#python3 ./build-demo.py --target $TARGET $SYSROOT --verbose
