
set TARGET=win-32
set SYSROOT=
set SQLITEVER=sqlite-amalgamation-3250200-32

if exist sysroots\%TARGET% (
	%SYSROOT%=--no-sysroot   
) else (
if not exist sysroots (
md sysroots
)git p

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
lib /DEF:sqlite3.def /OUT:sqlite3.lib /MACHINE:x86

cd ..
cd ..



cd ..
cd ..
cd ..
)
    
python build-pineboo-binaries.py --target %TARGET% %SYSROOT% --verbose




