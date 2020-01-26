#!/bin/bash
TARGET="android-64"
SYSROOT=""
LOCALDIR="$(pwd)"
export ANDROID_SDK_ROOT=~/Android/Sdk
export ANDROID_NDK_ROOT=$LOCALDIR/src/android-ndk-r19c
export HOST_TAG=linux-x86_64
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
export PATH=$PATH:$ANDROID_SDK_ROOT/tools
export PATH=$PATH:$ANDROID_NDK:$ANDROID_NDK_ROOT/build
export ANDROID_NDK_PLATFORM=android-24
export ANDROID_NDK_TOOLCHAIN_VERSION=4.9
export JAVA_HOME=/usr/lib/jvm/java-8-oracle
export TOOLCHAIN_PREFIX=$ANDROID_NDK_ROOT/toolchains/x86_64-4.9/prebuilt/linux-x86_64/x86_64-linux-android/bin

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
git clone https://github.com/aulla/sqlite3-android sqlite3
cd sqlite3
make
cd ..
fi

if [ ! -e "bzip2" ] ; then   
git clone git://sourceware.org/git/bzip2.git bzip
cd bzip
export TOOLCHAIN=$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/$HOST_TAG
make -f Makefile-libbz2_so CC=$TOOLCHAIN/bin/aarch64-linux-android24-clang AR=$TOOLCHAIN/bin/aarch64-linux-android-ar RANLIB=$TOOLCHAIN/bin/aarch64-linux-android-ranlib
cd ..

fi

cd ..
cd ..
cd ..

fi

python3 ./build-pineboo-binaries.py --target $TARGET $SYSROOT --verbose
#python3 ./build-demo.py --target $TARGET $SYSROOT --verbose
