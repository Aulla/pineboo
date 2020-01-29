#!/bin/bash
TARGET="ios"
SYSROOT=""
FILE_SQLLITE="sqlite-autoconf-3280000"
SRC_DIR_SQLLITE="sqlite3"

XCODE_BIN_PATH="/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/"
CXXFLAGS="—Os -DSQLITE_ENABLE_UNLOCK_NOTIFY=1 -arch arm64 -std=c++14 -stdlib=libc++ -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS9.3.sdk"
CC="$XCODE_BIN_PATH/clang"
CXX="$XCODE_BIN_PATH/clang++"
LD="$XCODE_BIN_PATH/ld" 
AR="$XCODE_BIN_PATH/ar"

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
if [ ! -e sqlite3 ] ; then
if [ ! -f $FILE_SQLLITE.tar.gz ]; then
wget https://www.sqlite.org/2019/$FILE_SQLLITE.tar.gz
fi

mkdir $SRC_DIR_SQLLITE
tar -xvzf $FILE_SQLLITE.tar.gz -C ./sqlite3 > /dev/null
cd $SRC_DIR_SQLLITE
cd $FILE_SQLLITE
./configure --host=arm-apple-darwin --enable-static --enable-dynamic-extensions
make
cd ..
cd ..
fi

cd ..
cd ..
cd ..

fi
python3 ./build-pineboo-binaries.py --target $TARGET $SYSROOT --verbose
