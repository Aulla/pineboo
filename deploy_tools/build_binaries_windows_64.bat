
set TARGET=win-64
set SYSROOT=
set SQLITE_VER=sqlite-autoconf-3280000

if exist .\sysroots\%TARGET% (
	set SYSROOT=--no-sysroot   
) else
(
if not exist .\sysroots (
md sysroots
)

if not exist .\sysroots\extra_libs (
md sysroots\extra_libs
)

if not exist .\sysroots\extra_libs\%TARGET% (
md sysroots/extra_libs/$TARGET
)

cd sysroots\extra_libs\$TARGET
md sqlite3
md sqlite3\%SQLITE_VER%
cp src\%SQLITE_VER%\* sqlite3\%SQLITE_VER% /E

cd sqlite3\%SQLITE_VER%
cl sqlite3.c -link -dll -out:sqlite3.dll

cd ..
cd ..



cd ..
cd ..
cd ..
)
    
python build-pineboo-binaries.py --target %TARGET% %SYSROOT% --verbose




