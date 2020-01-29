#!/bin/bash
TARGET="ios"
SYSROOT=""
FILE_SQLLITE="sqlite-autoconf-3280000"
IPHONE_SDKVERSION="12.1" #`xcodebuild -showsdks | grep iphoneos | egrep "[[:digit:]]+\.[[:digit:]]+" -o | tail -1`
XCODE_ROOT="~/Downloads/Xcode.app/Contents/Developer" #`xcode-select -print-path`
SRC_DIR_SQLLITE="sqlite3"

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
#./configure --host=arm-apple-darwin --enable-static --enable-dynamic-extensions
./configure --host=arm-apple-darwin CXXFLAGS="—Os -DSQLITE_ENABLE_UNLOCK_NOTIFY=1 -arch arm64 -std=c++14 -stdlib=libc++" CC="clang" CXX="clang++" LD="ld" AR="ar" --disable-shared --enable-static --enable-dynamic-extensions

make
cd ..
cd ..
fi

cd ..
cd ..
cd ..

fi

python3 ./build-pineboo-binaries.py --target $TARGET $SYSROOT --verbose
