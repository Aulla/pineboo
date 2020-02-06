
set TARGET=win-64
set SYSROOT=
set SQLITEVER=sqlite-autoconf-3280000

if exist sysroots\%TARGET% (
	%SYSROOT%=--no-sysroot   
) else (
if not exist sysroots (
md sysroots
)

if not exist sysroots\extra_libs (
md sysroots\extra_libs
)

if not exist sysroots\extra_libs\%TARGET% (
md sysroots\extra_libs\%TARGET%
)

cd sysroots\extra_libs\%TARGET%
md sqlite3
md sqlite3\%SQLITEVER%
xcopy ..\..\..\src\%SQLITEVER%\*.* sqlite3\%SQLITEVER% /E

cd sqlite3\%SQLITEVER%
cl sqlite3.c -link -dll -out:sqlite3.dll
lib sqlite3.obj

cd ..
cd ..



cd ..
cd ..
cd ..
)
    
python build-pineboo-binaries.py --target %TARGET% %SYSROOT% --verbose




