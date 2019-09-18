
set TARGET=win-32
set SYSROOT= 

if exist .\sysroots\%TARGET% (
	set SYSROOT=--no-sysroot   
	echo OMITIENDO SYSROOT. 
) else
(
echo Creando SYSROOT.
)
    
python build-pineboo-binaries.py --target %TARGET% %SYSROOT% --verbose




