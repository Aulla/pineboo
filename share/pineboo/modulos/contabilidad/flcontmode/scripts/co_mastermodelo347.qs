/***************************************************************************
                 co_mastermodelo347.qs  -  description
                             -------------------
    begin                : mie jun 1 2005
    copyright            : (C) 2005 by InfoSiAL S.L.
    email                : mail@infosial.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

/** @file */

/** @class_declaration interna */
////////////////////////////////////////////////////////////////////////////
//// DECLARACION ///////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////
//// INTERNA /////////////////////////////////////////////////////
class interna {
	var ctx:Object;
	function interna( context ) { this.ctx = context; }
	function init() { this.ctx.interna_init(); }
}
//// INTERNA /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_declaration oficial */
//////////////////////////////////////////////////////////////////
//// OFICIAL /////////////////////////////////////////////////////
class oficial extends interna {
	function oficial( context ) { interna( context ); }
	function lanzar() {
		return this.ctx.oficial_lanzar();
	}
	function presTelematica() {
		return this.ctx.oficial_presTelematica();
	}
	function presTelematica2007() {
		return this.ctx.oficial_presTelematica2007();
	}
	function presTelematica2008() {
		return this.ctx.oficial_presTelematica2008();
	}
	function errorAcumuladoControl(acumuladoControl:Number, nombreDato:String):Boolean {
		return this.ctx.oficial_errorAcumuladoControl(acumuladoControl, nombreDato);
	}
}
//// OFICIAL /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_declaration boe2011 */
//////////////////////////////////////////////////////////////////
//// OFICIAL /////////////////////////////////////////////////////
class boe2011 extends oficial {
    function boe2011( context ) { oficial( context ); }
    function presTelematica() {
        return this.ctx.boe2011_presTelematica();
    }
    function presTelematica2011() {
        return this.ctx.boe2011_presTelematica2011();
    }
    function nombreFichero():String {
        return this.ctx.boe2011_nombreFichero();
    }
    
    function soporteModelo():String{
        return this.ctx.boe2011_soporteModelo();
    }
    function tiporeg1(curMod:FLSlqCursor):String {
        return this.ctx.boe2011_tiporeg1(curMod);
    }
    function tiporeg2d(curMod:FLSlqCursor,curMod2d:FlsqlCursor):String {
        return this.ctx.boe2011_tiporeg2d(curMod,curMod2d);
    }
    function tiporeg2i(curMod:FLSlqCursor,curMod2i:FlsqlCursor):String {
        return this.ctx.boe2011_tiporeg2i(curMod,curMod2i);
    }
}
//// OFICIAL /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_declaration head */
/////////////////////////////////////////////////////////////////
//// DESARROLLO /////////////////////////////////////////////////
class head extends boe2011 {
	function head( context ) { boe2011 ( context ); }
}
//// DESARROLLO /////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_declaration ifaceCtx */
/////////////////////////////////////////////////////////////////
//// INTERFACE  /////////////////////////////////////////////////
class ifaceCtx extends head {
	function ifaceCtx( context ) { head( context ); }
}

const iface = new ifaceCtx( this );
//// INTERFACE  /////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition interna */
////////////////////////////////////////////////////////////////////////////
//// DEFINICION ////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////
//// INTERNA /////////////////////////////////////////////////////
function interna_init()
{
	connect (this.child("toolButtonPrint"), "clicked()", this, "iface.lanzar()");
	connect (this.child("toolButtonAeat"), "clicked()", this, "iface.presTelematica()");
}
//// INTERNA /////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition oficial */
//////////////////////////////////////////////////////////////////
//// OFICIAL /////////////////////////////////////////////////////
function oficial_lanzar()
{
	var util:FLUtil = new FLUtil;
	var cursor:FLSqlCursor = this.cursor();

	var dialogo = new Dialog;
	dialogo.caption = util.translate("scripts", "Imprimir modelo 347");
	dialogo.okButtonText = util.translate("scripts", "Aceptar");
	dialogo.cancelButtonText = util.translate("scripts", "Cancelar");

	var chkDR = new CheckBox;
	chkDR.text = util.translate("scripts", "Declaraci�n recapitulativa");
	chkDR.checked = true;
	dialogo.add(chkDR);

	var chkInmuebles = new CheckBox;
	chkInmuebles.text = util.translate("scripts", "Relaci�n de Inmuebles");
	chkInmuebles.checked = true;
	dialogo.add(chkInmuebles);

	var chkDeclarados = new CheckBox;
	chkDeclarados.text = util.translate("scripts", "Relaci�n de Declarados");
	chkDeclarados.checked = true;
	dialogo.add(chkDeclarados);

	if (!dialogo.exec())
		return;

	var nombreInforme:String;
	if (chkDR.checked) {
		nombreInforme = cursor.action();
		flcontmode.iface.pub_lanzar(cursor, nombreInforme, nombreInforme + ".idmodelo = " + cursor.valueBuffer( "idmodelo" ) );
	}
	if (chkInmuebles.checked) {
		nombreInforme = "co_modelo347_in";
		flcontmode.iface.pub_lanzar(cursor, nombreInforme, "co_modelo347.idmodelo = " + cursor.valueBuffer( "idmodelo" ) );
	}
	if (chkDeclarados.checked) {
		nombreInforme = "co_modelo347_de";
		flcontmode.iface.pub_lanzar(cursor, nombreInforme, "co_modelo347.idmodelo = " + cursor.valueBuffer( "idmodelo" ) );
	}
}

/** \D Genera un fichero para realizar la presentaci�n telem�tica del modelo
\end */
function oficial_presTelematica()
{
	var util:FLUtil = new FLUtil();
	var cursor:FLSqlCursor = this.cursor();

	var codEjercicio:String;
	codEjercicio = util.sqlSelect("ejercicios", "fechainicio", "codejercicio = '" + cursor.valueBuffer("codejercicio") + "'");
	codEjercicio = codEjercicio.toString().left(4); 

	switch (codEjercicio) {
		case "2005":
		case "2006":
		case "2007": {
			this.iface.presTelematica2007();
			break;
		}
		default: {
			this.iface.presTelematica2008();
			break;
		}
	}
}

function oficial_presTelematica2007()
{
	var util:FLUtil = new FLUtil();
	// Tipo de soporte
	var tipoSoporte:String;
	var presTelematica:String = util.translate("scripts", "Transmisi�n telem�tica");
	var disquete:String = util.translate("scripts", "Disquete");
	var cintaMagnetica:String = util.translate("scripts", "Cinta magn�tica");
	var soportes:Array = [presTelematica, disquete, cintaMagnetica];
	var opcion:String = Input.getItem(util.translate("scripts", "Indique el tipo de soporte"), soportes, presTelematica, false);
	if (!opcion)
		return;
	switch (opcion) {
		case presTelematica:
			tipoSoporte = "T";
			break;
		case disquete:
			tipoSoporte = "D";
			break;
		case cintaMagnetica:
			tipoSoporte = "C";
			break;
	}
	
	var cursor:FLSqlCursor = this.cursor();
	if (!cursor.isValid())
		return;
	
	var nombreFichero:String = FileDialog.getSaveFileName("*.*");
	if (!nombreFichero)
		return;
		
	var file:Object = new File(nombreFichero);
	file.open(File.WriteOnly);

	var nombreDato:String;
	var contenido:String = "";
	var contenido1:String = "";
	var contenido2:String = "";
	var contenido3:String = "";
	var file:Object = new File(nombreFichero);
	file.open(File.WriteOnly);

	// 	Registro de tipo 1
	nombreDato = util.translate("scripts", "Tipo de registro");
	if ((contenido1.length + 1) !=  1) {
		return this.iface.errorAcumuladoControl(1, nombreDato);
	}
	contenido1 += "1";

	nombreDato = util.translate("scripts", "Modelo");
	if ((contenido1.length + 1) !=  2) {
		return this.iface.errorAcumuladoControl(2, nombreDato);
	}
	contenido1 += "347";
	
	nombreDato = util.translate("scripts", "Ejercicio");
	if ((contenido1.length + 1) !=  5) {
		return this.iface.errorAcumuladoControl(5, nombreDato);
	}
	var ejercicio:String;
	temp = util.sqlSelect("ejercicios", "fechainicio", "codejercicio = '" + cursor.valueBuffer("codejercicio") + "'");
	ejercicio = temp.toString().left(4); 
	contenido1 += ejercicio; 
	
	nombreDato = util.translate("scripts", "NIF del declarante");
	if ((contenido1.length + 1) !=  9) {
		return this.iface.errorAcumuladoControl(9, nombreDato);
	}
	temp = cursor.valueBuffer("cifnif");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del declarante"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
	nombreDato = util.translate("scripts", "Apellidos o raz�n social");
	if ((contenido1.length + 1) !=  18) {
		return this.iface.errorAcumuladoControl(18, nombreDato);
	}
	temp = cursor.valueBuffer("apellidosnombrers");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Apellidos o raz�n social"), 40))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 40); 
	
	nombreDato = util.translate("scripts", "Tipo de soporte");
	if ((contenido1.length + 1) !=  58) {
		return this.iface.errorAcumuladoControl(58, nombreDato);
	}
	contenido1 += tipoSoporte;
	
	nombreDato = util.translate("scripts", "Tel�fono contacto");
	if ((contenido1.length + 1) !=  59) {
		return this.iface.errorAcumuladoControl(59, nombreDato);
	}
	temp = cursor.valueBuffer("telefono");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Tel�fono contacto"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
	nombreDato = util.translate("scripts", "Persona de contacto");
	if ((contenido1.length + 1) !=  68) {
		return this.iface.errorAcumuladoControl(68, nombreDato);
	}
	temp = cursor.valueBuffer("contacto");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Persona de contacto"), 40))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 40); 
	
	nombreDato = util.translate("scripts", "N� justificante de la declaraci�n");
	if ((contenido1.length + 1) !=  108) {
		return this.iface.errorAcumuladoControl(108, nombreDato);
	}
	temp = cursor.valueBuffer("justificante");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N� Justificante de la declaraci�n"), 13))
		return false;
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 13); 
	
	nombreDato = util.translate("scripts", "Declaraci�n complementaria");
	if ((contenido1.length + 1) !=  121) {
		return this.iface.errorAcumuladoControl(121, nombreDato);
	}
	if (cursor.valueBuffer("complementaria"))
		temp = "C";
	else
		temp = " ";
	contenido1 += temp; 
	
	nombreDato = util.translate("scripts", "Declaraci�n sustitutiva");
	if ((contenido1.length + 1) !=  122) {
		return this.iface.errorAcumuladoControl(122, nombreDato);
	}
	if (cursor.valueBuffer("sustitutiva"))
		temp = "S";
	else
		temp = " ";
	contenido1 += temp; 
	
	nombreDato = util.translate("scripts", "N� justificante de la declaraci�n anterior");
	if ((contenido1.length + 1) !=  123) {
		return this.iface.errorAcumuladoControl(123, nombreDato);
	}
	temp = cursor.valueBuffer("jusanterior");
	if (cursor.valueBuffer("complementaria") || cursor.valueBuffer("sustitutiva")) {
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N� Justificante de la declaraci�n anterior"), 13))
			return false;
	} else {
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "N� Justificante de la declaraci�n anterior"), 13))
			return false;
	}
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 13); 
	
	nombreDato = util.translate("scripts", "N� total de personas y entidades");
	if ((contenido1.length + 1) !=  136) {
		return this.iface.errorAcumuladoControl(136, nombreDato);
	}
	temp = cursor.valueBuffer("totalentidades");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N� total de personas y entidades"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 9); 
	
	nombreDato = util.translate("scripts", "Importe de las operaciones");
	if ((contenido1.length + 1) !=  145) {
		return this.iface.errorAcumuladoControl(145, nombreDato);
	}
	temp = cursor.valueBuffer("importetotal");
	contenido1 += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
	nombreDato = util.translate("scripts", "N� total de inmuebles");
	if ((contenido1.length + 1) !=  160) {
		return this.iface.errorAcumuladoControl(160, nombreDato);
	}
	temp = cursor.valueBuffer("totalinmuebles");
	if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "N� total de inmuebles"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 9); 
	
	nombreDato = util.translate("scripts", "Importe arrendamientos");
	if ((contenido1.length + 1) !=  169) {
		return this.iface.errorAcumuladoControl(169, nombreDato);
	}
	temp = cursor.valueBuffer("totalarrendamiento");
	contenido1 += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
	nombreDato = util.translate("scripts", "Relleno de blancos hasta 250 caracteres");
	if ((contenido1.length + 1) !=  184) {
		return this.iface.errorAcumuladoControl(184, nombreDato);
	}
	temp = " ";
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 67); 
	
	// Fin de registro tipo 1

	contenido += contenido1;
	contenido += "\r\n";
	
	//Registros tipo 2 (Declarados)
	var qryMod300Tipo2:FLSqlQuery = new FLSqlQuery();
	qryMod300Tipo2.setTablesList("co_modelo347_tipo2d");
	qryMod300Tipo2.setSelect("nifdeclarado, nifreplegal, apellidosnombrers, codprovincia, codpais, clavecodigo, importe, seguro, arrendlocal");
	qryMod300Tipo2.setFrom("co_modelo347_tipo2d");
	qryMod300Tipo2.setWhere("idmodelo = " + cursor.valueBuffer("idmodelo"));
	if (!qryMod300Tipo2.exec()) {
		MessageBox.critical(util.translate("scripts", "Hubo un error al acceder a los datos de registros de declarados.\nEl fichero no se ha podido generar correctamente"), MessageBox.Ok, MessageBox.NoButton);
		return;
	}
	while (qryMod300Tipo2.next()) {
		var declarado:String = "";

		nombreDato = util.translate("scripts", "Tipo de registro");
		if ((declarado.length + 1) !=  1) {
			return this.iface.errorAcumuladoControl(1, nombreDato);
		}
		declarado += "2";

		nombreDato = util.translate("scripts", "Modelo");
		if ((declarado.length + 1) !=  2) {
			return this.iface.errorAcumuladoControl(2, nombreDato);
		}
		declarado += "347";
		
		nombreDato = util.translate("scripts", "Ejercicio");
		if ((declarado.length + 1) !=  5) {
			return this.iface.errorAcumuladoControl(5, nombreDato);
		}
		declarado += ejercicio; 
		
		nombreDato = util.translate("scripts", "NIF del declarante");
		if ((declarado.length + 1) !=  9) {
			return this.iface.errorAcumuladoControl(9, nombreDato);
		}
		temp = cursor.valueBuffer("cifnif");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del declarante"), 9))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
		nombreDato = util.translate("scripts", "NIF del declarado");
		if ((declarado.length + 1) !=  18) {
			return this.iface.errorAcumuladoControl(18, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifdeclarado");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF declarado"), 9))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "NIF del representante legal");
		if ((declarado.length + 1) !=  27) {
			return this.iface.errorAcumuladoControl(27, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifreplegal");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "NIF del representante legal"), 9))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del declarado");
		if ((declarado.length + 1) !=  36) {
			return this.iface.errorAcumuladoControl(36, nombreDato);
		}
		temp = qryMod300Tipo2.value("apellidosnombrers");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del declarado"), 40))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 40); 
	
		nombreDato = util.translate("scripts", "Tipo de hoja");
		if ((declarado.length + 1) !=  76) {
			return this.iface.errorAcumuladoControl(76, nombreDato);
		}
		declarado += "D"; 
		
		nombreDato = util.translate("scripts", "Provincia");
		if ((declarado.length + 1) !=  77) {
			return this.iface.errorAcumuladoControl(77, nombreDato);
		}
		temp = qryMod300Tipo2.value("codprovincia");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Provincia"), 2))
			return false;
		declarado += flfactppal.iface.pub_cerosIzquierda(temp, 2);
		
		nombreDato = util.translate("scripts", "Pa�s");
		if ((declarado.length + 1) !=  79) {
			return this.iface.errorAcumuladoControl(79, nombreDato);
		}
		temp = qryMod300Tipo2.value("codpais");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Pa�s"), 3))
			return false;
		declarado += flfactppal.iface.pub_cerosIzquierda(temp, 3);
	
		nombreDato = util.translate("scripts", "Clave c�digo");
		if ((declarado.length + 1) !=  82) {
			return this.iface.errorAcumuladoControl(82, nombreDato);
		}
		temp = qryMod300Tipo2.value("clavecodigo");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Clave c�digo"), 1))
			return false;
		declarado += temp; 
	
		nombreDato = util.translate("scripts", "Importe operaciones");
		if ((declarado.length + 1) !=  83) {
			return this.iface.errorAcumuladoControl(83, nombreDato);
		}
		temp = qryMod300Tipo2.value("importe");
		declarado += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
		nombreDato = util.translate("scripts", "Operaci�n seguro");
		if ((declarado.length + 1) !=  98) {
			return this.iface.errorAcumuladoControl(98, nombreDato);
		}
		if (qryMod300Tipo2.value("seguro"))
			temp = "X";
		else
			temp = " ";
		declarado += temp; 
		
		nombreDato = util.translate("scripts", "Arrendamiento de local");
		if ((declarado.length + 1) !=  99) {
			return this.iface.errorAcumuladoControl(99, nombreDato);
		}
		if (qryMod300Tipo2.value("arrendlocal"))
			temp = "X";
		else
			temp = " ";
		declarado += temp; 
		
		nombreDato = util.translate("scripts", "Relleno de blancos hasta 250 caracteres");
		if ((declarado.length + 1) !=  100) {
			return this.iface.errorAcumuladoControl(100, nombreDato);
		}
		temp = " ";
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 151); 
	
		// Fin de registro tipo 2
		declarado += "\r\n";
		contenido2 += declarado;
	}
	contenido += contenido2;
	
	//Registros tipo 2 (Inmuebles)
	var qryMod300Tipo2:FLSqlQuery = new FLSqlQuery();
	qryMod300Tipo2.setTablesList("co_modelo347_tipo2i");
	qryMod300Tipo2.setSelect("nifarrendatario, nifreplegal, apellidosnombrers, importe, refcatastral, codprovincia, municipio, codtipovia, nombrevia, numero, escalera, piso, puerta");
	qryMod300Tipo2.setFrom("co_modelo347_tipo2i");
	qryMod300Tipo2.setWhere("idmodelo = " + cursor.valueBuffer("idmodelo"));
	if (!qryMod300Tipo2.exec()) {
		MessageBox.critical(util.translate("scripts", "Hubo un error al acceder a los datos de registros de inmuebles.\nEl fichero no se ha podido generar correctamente"), MessageBox.Ok, MessageBox.NoButton);
		return;
	}
	while (qryMod300Tipo2.next()) {
		var inmueble:String = "";

		nombreDato = util.translate("scripts", "Tipo de registro");
		if ((inmueble.length + 1) !=  1) {
			return this.iface.errorAcumuladoControl(1, nombreDato);
		}
		inmueble += "2";

		nombreDato = util.translate("scripts", "Modelo");
		if ((inmueble.length + 1) !=  2) {
			return this.iface.errorAcumuladoControl(2, nombreDato);
		}
		inmueble += "347";
		
		nombreDato = util.translate("scripts", "Ejercicio");
		if ((inmueble.length + 1) !=  5) {
			return this.iface.errorAcumuladoControl(5, nombreDato);
		}
		inmueble += ejercicio; 
		
		nombreDato = util.translate("scripts", "NIF del declarante");
		if ((inmueble.length + 1) !=  9) {
			return this.iface.errorAcumuladoControl(9, nombreDato);
		}
		temp = cursor.valueBuffer("cifnif");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del declarante"), 9))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
		nombreDato = util.translate("scripts", "NIF del arrendatario");
		if ((inmueble.length + 1) !=  18) {
			return this.iface.errorAcumuladoControl(18, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifarrendatario");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del arrendatario"), 9))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "NIF del representante legal");
		if ((inmueble.length + 1) !=  27) {
			return this.iface.errorAcumuladoControl(27, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifreplegal");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "NIF del representante legal"), 9))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del arrendatario");
		if ((inmueble.length + 1) !=  36) {
			return this.iface.errorAcumuladoControl(36, nombreDato);
		}
		temp = qryMod300Tipo2.value("apellidosnombrers");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del arrendatario"), 40))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 40);
	
		nombreDato = util.translate("scripts", "Tipo de hoja");
		if ((inmueble.length + 1) !=  76) {
			return this.iface.errorAcumuladoControl(76, nombreDato);
		}
		inmueble += "I"; 

		nombreDato = util.translate("scripts", "21 espacios en blanco");
		if ((inmueble.length + 1) !=  77) {
			return this.iface.errorAcumuladoControl(77, nombreDato);
		}
		temp = " ";
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 23); 
		
		nombreDato = util.translate("scripts", "Importe operaciones");
		if ((inmueble.length + 1) !=  100) {
			return this.iface.errorAcumuladoControl(100, nombreDato);
		}
		temp = qryMod300Tipo2.value("importe");
		inmueble += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
		nombreDato = util.translate("scripts", "Referencia catastral");
		if ((inmueble.length + 1) !=  115) {
			return this.iface.errorAcumuladoControl(115, nombreDato);
		}
		temp = qryMod300Tipo2.value("refcatastral");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Referencia catastral"), 25))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 25); 
		
		nombreDato = util.translate("scripts", "Provincia");
		if ((inmueble.length + 1) !=  140) {
			return this.iface.errorAcumuladoControl(140, nombreDato);
		}
		temp = qryMod300Tipo2.value("codprovincia");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Provincia"), 2))
			return false;
		inmueble += flfactppal.iface.pub_cerosIzquierda(temp, 2); 
		
		nombreDato = util.translate("scripts", "Municipio");
		if ((inmueble.length + 1) !=  142) {
			return this.iface.errorAcumuladoControl(142, nombreDato);
		}
		temp = qryMod300Tipo2.value("municipio");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Municipio"), 24))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 24); 
	
		nombreDato = util.translate("scripts", "Tipo de v�a");
		if ((inmueble.length + 1) !=  166) {
			return this.iface.errorAcumuladoControl(166, nombreDato);
		}
		temp = qryMod300Tipo2.value("codtipovia");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Tipo de v�a"), 2))
			return false;
		inmueble += temp;
		
		nombreDato = util.translate("scripts", "Nombre de la v�a");
		if ((inmueble.length + 1) !=  168) {
			return this.iface.errorAcumuladoControl(168, nombreDato);
		}
		temp = qryMod300Tipo2.value("nombrevia");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Nombre de la v�a"), 20))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 20);
		
		nombreDato = util.translate("scripts", "N�mero del inmueble");
		if ((inmueble.length + 1) !=  188) {
			return this.iface.errorAcumuladoControl(188, nombreDato);
		}
		temp = qryMod300Tipo2.value("numero");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N�mero del inmueble"), 5))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 5); 
		
		nombreDato = util.translate("scripts", "Escalera del inmueble");
		if ((inmueble.length + 1) !=  193) {
			return this.iface.errorAcumuladoControl(193, nombreDato);
		}
		temp = qryMod300Tipo2.value("escalera");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Escalera del inmueble"), 2))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 2); 
		
		nombreDato = util.translate("scripts", "Piso del inmueble");
		if ((inmueble.length + 1) !=  195) {
			return this.iface.errorAcumuladoControl(195, nombreDato);
		}
		temp = qryMod300Tipo2.value("piso");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Piso del inmueble"), 2))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 2); 
		
		nombreDato = util.translate("scripts", "Puerta del inmueble");
		if ((inmueble.length + 1) !=  197) {
			return this.iface.errorAcumuladoControl(197, nombreDato);
		}
		temp = qryMod300Tipo2.value("puerta");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Puerta del inmueble"), 2))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 2); 
		
		nombreDato = util.translate("scripts", "Relleno de blancos hasta 250 caracteres");
		if ((inmueble.length + 1) !=  199) {
			return this.iface.errorAcumuladoControl(199, nombreDato);
		}
		temp = " ";
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 52); 
	
		// Fin de registro tipo 2 (Inmueble)

		inmueble += "\r\n";
		contenido3 += inmueble;
	}
	contenido += contenido3;

	file.write(contenido);
	file.close();

	MessageBox.information(util.translate("scripts", "Generado fichero en :\n\n" + nombreFichero + "\n\n"), MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton);
}

function oficial_presTelematica2008()
{
	var util:FLUtil = new FLUtil();
	// Tipo de soporte
	var tipoSoporte:String;
	var presTelematica:String = util.translate("scripts", "Transmisi�n telem�tica");
	var disquete:String = util.translate("scripts", "Disquete");
	var cintaMagnetica:String = util.translate("scripts", "Cinta magn�tica");
	var soportes:Array = [presTelematica, disquete, cintaMagnetica];
	var opcion:String = Input.getItem(util.translate("scripts", "Indique el tipo de soporte"), soportes, presTelematica, false);
	if (!opcion)
		return;
	switch (opcion) {
		case presTelematica:
			tipoSoporte = "T";
			break;
		case disquete:
			tipoSoporte = "D";
			break;
		case cintaMagnetica:
			tipoSoporte = "C";
			break;
	}
	
	var cursor:FLSqlCursor = this.cursor();
	if (!cursor.isValid())
		return;
	
	var nombreFichero:String = FileDialog.getSaveFileName("*.*");
	if (!nombreFichero)
		return;
		
	var file:Object = new File(nombreFichero);
	file.open(File.WriteOnly);

	var nombreDato:String;
	var contenido:String = "";
	var contenido1:String = "";
	var contenido2:String = "";
	var contenido3:String = "";
	var file:Object = new File(nombreFichero);
	file.open(File.WriteOnly);

	// 	Registro de tipo 1
	nombreDato = util.translate("scripts", "Tipo de registro");
	if ((contenido1.length + 1) !=  1) {
		return this.iface.errorAcumuladoControl(1, nombreDato);
	}
	contenido1 += "1";

	nombreDato = util.translate("scripts", "Modelo");
	if ((contenido1.length + 1) !=  2) {
		return this.iface.errorAcumuladoControl(2, nombreDato);
	}
	contenido1 += "347";
	
	nombreDato = util.translate("scripts", "Ejercicio");
	if ((contenido1.length + 1) !=  5) {
		return this.iface.errorAcumuladoControl(5, nombreDato);
	}
	var ejercicio:String;
	temp = util.sqlSelect("ejercicios", "fechainicio", "codejercicio = '" + cursor.valueBuffer("codejercicio") + "'");
	ejercicio = temp.toString().left(4); 
	contenido1 += ejercicio; 
	
	nombreDato = util.translate("scripts", "NIF del declarante");
	if ((contenido1.length + 1) !=  9) {
		return this.iface.errorAcumuladoControl(9, nombreDato);
	}
	temp = cursor.valueBuffer("cifnif");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del declarante"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
	nombreDato = util.translate("scripts", "Apellidos o raz�n social");
	if ((contenido1.length + 1) !=  18) {
		return this.iface.errorAcumuladoControl(18, nombreDato);
	}
	temp = cursor.valueBuffer("apellidosnombrers");
	temp = flcontmode.iface.pub_formatoAlfabetico347(temp);
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Apellidos o raz�n social"), 40))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 40); 
	
	nombreDato = util.translate("scripts", "Tipo de soporte");
	if ((contenido1.length + 1) !=  58) {
		return this.iface.errorAcumuladoControl(58, nombreDato);
	}
	contenido1 += tipoSoporte;
	
	nombreDato = util.translate("scripts", "Tel�fono contacto");
	if ((contenido1.length + 1) !=  59) {
		return this.iface.errorAcumuladoControl(59, nombreDato);
	}
	temp = cursor.valueBuffer("telefono");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Tel�fono contacto"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
	nombreDato = util.translate("scripts", "Persona de contacto");
	if ((contenido1.length + 1) !=  68) {
		return this.iface.errorAcumuladoControl(68, nombreDato);
	}
	temp = cursor.valueBuffer("contacto");
	temp = flcontmode.iface.pub_formatearTexto(temp);
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Persona de contacto"), 40))
		return false;
	contenido1 += flfactppal.iface.pub_espaciosDerecha(temp, 40); 
	
	nombreDato = util.translate("scripts", "N� justificante de la declaraci�n");
	if ((contenido1.length + 1) !=  108) {
		return this.iface.errorAcumuladoControl(108, nombreDato);
	}
	temp = cursor.valueBuffer("justificante");
	if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N� Justificante de la declaraci�n"), 13))
		return false;
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 13); 
	
	nombreDato = util.translate("scripts", "Declaraci�n complementaria");
	if ((contenido1.length + 1) !=  121) {
		return this.iface.errorAcumuladoControl(121, nombreDato);
	}
	if (cursor.valueBuffer("complementaria"))
		temp = "C";
	else
		temp = " ";
	contenido1 += temp; 
	
	nombreDato = util.translate("scripts", "Declaraci�n sustitutiva");
	if ((contenido1.length + 1) !=  122) {
		return this.iface.errorAcumuladoControl(122, nombreDato);
	}
	if (cursor.valueBuffer("sustitutiva"))
		temp = "S";
	else
		temp = " ";
	contenido1 += temp; 
	
	nombreDato = util.translate("scripts", "N� justificante de la declaraci�n anterior");
	if ((contenido1.length + 1) !=  123) {
		return this.iface.errorAcumuladoControl(123, nombreDato);
	}
	temp = cursor.valueBuffer("jusanterior");
	if (cursor.valueBuffer("complementaria") || cursor.valueBuffer("sustitutiva")) {
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N� Justificante de la declaraci�n anterior"), 13))
			return false;
	} else {
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "N� Justificante de la declaraci�n anterior"), 13))
			return false;
	}
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 13); 
	
	nombreDato = util.translate("scripts", "N� total de personas y entidades");
	if ((contenido1.length + 1) !=  136) {
		return this.iface.errorAcumuladoControl(136, nombreDato);
	}
	temp = cursor.valueBuffer("totalentidades");
	if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "N� total de personas y entidades"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 9); 
	
	nombreDato = util.translate("scripts", "Importe de las operaciones");
	if ((contenido1.length + 1) !=  145) {
		return this.iface.errorAcumuladoControl(145, nombreDato);
	}
	temp = cursor.valueBuffer("importetotal");
	contenido1 += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
	nombreDato = util.translate("scripts", "N� total de inmuebles");
	if ((contenido1.length + 1) !=  160) {
		return this.iface.errorAcumuladoControl(160, nombreDato);
	}
	temp = cursor.valueBuffer("totalinmuebles");
	if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "N� total de inmuebles"), 9))
		return false;
	contenido1 += flfactppal.iface.pub_cerosIzquierda(temp, 9); 
	
	nombreDato = util.translate("scripts", "Importe arrendamientos");
	if ((contenido1.length + 1) !=  169) {
		return this.iface.errorAcumuladoControl(169, nombreDato);
	}
	temp = cursor.valueBuffer("totalarrendamiento");
	contenido1 += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
	nombreDato = util.translate("scripts", "Relleno de blancos hasta 500 caracteres");
	if ((contenido1.length + 1) !=  184) {
		return this.iface.errorAcumuladoControl(184, nombreDato);
	}
	temp = " ";
	contenido1 = flfactppal.iface.pub_espaciosDerecha(contenido1, 500);
	
	// Fin de registro tipo 1

	contenido += contenido1;
	contenido += "\r\n";
	
	//Registros tipo 2 (Declarados)
	var qryMod300Tipo2:FLSqlQuery = new FLSqlQuery();
	qryMod300Tipo2.setTablesList("co_modelo347_tipo2d");
	qryMod300Tipo2.setSelect("nifdeclarado, nifreplegal, apellidosnombrers, codprovincia, codpais, clavecodigo, importe, seguro, arrendlocal, importemetalico, importeinmuebles");
	qryMod300Tipo2.setFrom("co_modelo347_tipo2d");
	qryMod300Tipo2.setWhere("idmodelo = " + cursor.valueBuffer("idmodelo"));
	if (!qryMod300Tipo2.exec()) {
		MessageBox.critical(util.translate("scripts", "Hubo un error al acceder a los datos de registros de declarados.\nEl fichero no se ha podido generar correctamente"), MessageBox.Ok, MessageBox.NoButton);
		return;
	}
	while (qryMod300Tipo2.next()) {
		var declarado:String = "";

		nombreDato = util.translate("scripts", "Tipo de registro");
		if ((declarado.length + 1) !=  1) {
			return this.iface.errorAcumuladoControl(1, nombreDato);
		}
		declarado += "2";

		nombreDato = util.translate("scripts", "Modelo");
		if ((declarado.length + 1) !=  2) {
			return this.iface.errorAcumuladoControl(2, nombreDato);
		}
		declarado += "347";
		
		nombreDato = util.translate("scripts", "Ejercicio");
		if ((declarado.length + 1) !=  5) {
			return this.iface.errorAcumuladoControl(5, nombreDato);
		}
		declarado += ejercicio; 
		
		nombreDato = util.translate("scripts", "NIF del declarante");
		if ((declarado.length + 1) !=  9) {
			return this.iface.errorAcumuladoControl(9, nombreDato);
		}
		temp = cursor.valueBuffer("cifnif");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del declarante"), 9))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
		nombreDato = util.translate("scripts", "NIF del declarado");
		if ((declarado.length + 1) !=  18) {
			return this.iface.errorAcumuladoControl(18, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifdeclarado");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF declarado"), 9))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "NIF del representante legal");
		if ((declarado.length + 1) !=  27) {
			return this.iface.errorAcumuladoControl(27, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifreplegal");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "NIF del representante legal"), 9))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del declarado");
		if ((declarado.length + 1) !=  36) {
			return this.iface.errorAcumuladoControl(36, nombreDato);
		}
		temp = qryMod300Tipo2.value("apellidosnombrers");
		temp = flcontmode.iface.pub_formatoAlfabetico347(temp);
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del declarado"), 40))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 40); 
	
		nombreDato = util.translate("scripts", "Tipo de hoja");
		if ((declarado.length + 1) !=  76) {
			return this.iface.errorAcumuladoControl(76, nombreDato);
		}
		declarado += "D"; 
		
		nombreDato = util.translate("scripts", "Provincia");
		if ((declarado.length + 1) !=  77) {
			return this.iface.errorAcumuladoControl(77, nombreDato);
		}
		temp = qryMod300Tipo2.value("codprovincia");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Provincia"), 2))
			return false;
		declarado += flfactppal.iface.pub_cerosIzquierda(temp, 2);
		
		nombreDato = util.translate("scripts", "Pa�s");
		if ((declarado.length + 1) !=  79) {
			return this.iface.errorAcumuladoControl(79, nombreDato);
		}
		temp = qryMod300Tipo2.value("codpais");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Pa�s"), 2))
			return false;
		declarado += flfactppal.iface.pub_espaciosDerecha(temp, 2);
	
		declarado += " ";

		nombreDato = util.translate("scripts", "Clave c�digo");
		if ((declarado.length + 1) !=  82) {
			return this.iface.errorAcumuladoControl(82, nombreDato);
		}
		temp = qryMod300Tipo2.value("clavecodigo");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Clave c�digo"), 1))
			return false;
		declarado += temp; 
	
		nombreDato = util.translate("scripts", "Importe operaciones");
		if ((declarado.length + 1) !=  83) {
			return this.iface.errorAcumuladoControl(83, nombreDato);
		}
		temp = qryMod300Tipo2.value("importe");
		declarado += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
		nombreDato = util.translate("scripts", "Operaci�n seguro");
		if ((declarado.length + 1) !=  98) {
			return this.iface.errorAcumuladoControl(98, nombreDato);
		}
		if (qryMod300Tipo2.value("seguro"))
			temp = "X";
		else
			temp = " ";
		declarado += temp; 
		
		nombreDato = util.translate("scripts", "Arrendamiento de local");
		if ((declarado.length + 1) !=  99) {
			return this.iface.errorAcumuladoControl(99, nombreDato);
		}
		if (qryMod300Tipo2.value("arrendlocal"))
			temp = "X";
		else
			temp = " ";
		declarado += temp; 
		
		nombreDato = util.translate("scripts", "Importe met�lico");
		if ((declarado.length + 1) !=  100) {
			return this.iface.errorAcumuladoControl(100, nombreDato);
		}
		temp = qryMod300Tipo2.value("importemetalico");
		declarado += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
		nombreDato = util.translate("scripts", "Importe inmuebles");
		if ((declarado.length + 1) !=  115) {
			return this.iface.errorAcumuladoControl(115, nombreDato);
		}
		temp = qryMod300Tipo2.value("importeinmuebles");
		declarado += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
		nombreDato = util.translate("scripts", "Relleno de blancos hasta 500 caracteres");
		if ((declarado.length + 1) !=  130) {
			return this.iface.errorAcumuladoControl(130, nombreDato);
		}
		declarado = flfactppal.iface.pub_espaciosDerecha(declarado, 500); 
	
		// Fin de registro tipo 2
		declarado += "\r\n";
		contenido2 += declarado;
	}
	contenido += contenido2;
	
	//Registros tipo 2 (Inmuebles)
	var qryMod300Tipo2:FLSqlQuery = new FLSqlQuery();
	qryMod300Tipo2.setTablesList("co_modelo347_tipo2i");
	qryMod300Tipo2.setSelect("nifarrendatario, nifreplegal, apellidosnombrers, importe, situacion, refcatastral, codprovincia, localidad, municipio, codmunicipio, codpostal, codtipovia, nombrevia, tiponumeracion, numero, califnumero, bloque, portal, escalera, piso, puerta, complemento");
	qryMod300Tipo2.setFrom("co_modelo347_tipo2i");
	qryMod300Tipo2.setWhere("idmodelo = " + cursor.valueBuffer("idmodelo"));
	if (!qryMod300Tipo2.exec()) {
		MessageBox.critical(util.translate("scripts", "Hubo un error al acceder a los datos de registros de inmuebles.\nEl fichero no se ha podido generar correctamente"), MessageBox.Ok, MessageBox.NoButton);
		return;
	}
	while (qryMod300Tipo2.next()) {
		var inmueble:String = "";

		nombreDato = util.translate("scripts", "Tipo de registro");
		if ((inmueble.length + 1) !=  1) {
			return this.iface.errorAcumuladoControl(1, nombreDato);
		}
		inmueble += "2";

		nombreDato = util.translate("scripts", "Modelo");
		if ((inmueble.length + 1) !=  2) {
			return this.iface.errorAcumuladoControl(2, nombreDato);
		}
		inmueble += "347";
		
		nombreDato = util.translate("scripts", "Ejercicio");
		if ((inmueble.length + 1) !=  5) {
			return this.iface.errorAcumuladoControl(5, nombreDato);
		}
		inmueble += ejercicio; 
		
		nombreDato = util.translate("scripts", "NIF del declarante");
		if ((inmueble.length + 1) !=  9) {
			return this.iface.errorAcumuladoControl(9, nombreDato);
		}
		temp = cursor.valueBuffer("cifnif");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del declarante"), 9))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 9);
	
		nombreDato = util.translate("scripts", "NIF del arrendatario");
		if ((inmueble.length + 1) !=  18) {
			return this.iface.errorAcumuladoControl(18, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifarrendatario");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "NIF del arrendatario"), 9))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "NIF del representante legal");
		if ((inmueble.length + 1) !=  27) {
			return this.iface.errorAcumuladoControl(27, nombreDato);
		}
		temp = qryMod300Tipo2.value("nifreplegal");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "NIF del representante legal"), 9))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 9); 
	
		nombreDato = util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del arrendatario");
		if ((inmueble.length + 1) !=  36) {
			return this.iface.errorAcumuladoControl(36, nombreDato);
		}
		temp = qryMod300Tipo2.value("apellidosnombrers");
		temp = flcontmode.iface.pub_formatoAlfabetico347(temp);
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Apellidos y nombre, raz�n social o denominaci�n del arrendatario"), 40))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 40);
	
		nombreDato = util.translate("scripts", "Tipo de hoja");
		if ((inmueble.length + 1) !=  76) {
			return this.iface.errorAcumuladoControl(76, nombreDato);
		}
		inmueble += "I"; 

		nombreDato = util.translate("scripts", "21 espacios en blanco");
		if ((inmueble.length + 1) !=  77) {
			return this.iface.errorAcumuladoControl(77, nombreDato);
		}
		temp = " ";
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 23); 
		
		nombreDato = util.translate("scripts", "Importe operaciones");
		if ((inmueble.length + 1) !=  100) {
			return this.iface.errorAcumuladoControl(100, nombreDato);
		}
		temp = qryMod300Tipo2.value("importe");
		inmueble += flcontmode.iface.pub_formatoNumero(parseFloat(temp), 13, 2); 
	
		nombreDato = util.translate("scripts", "Situaci�n");
		if ((inmueble.length + 1) !=  115) {
			return this.iface.errorAcumuladoControl(115, nombreDato);
		}
		temp = qryMod300Tipo2.value("situacion");
		inmueble += temp; 
		
		nombreDato = util.translate("scripts", "Referencia catastral");
		if ((inmueble.length + 1) !=  116) {
			return this.iface.errorAcumuladoControl(116, nombreDato);
		}
		temp = qryMod300Tipo2.value("refcatastral");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Referencia catastral"), 25))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 25); 
		
		nombreDato = util.translate("scripts", "Tipo de v�a");
		if ((inmueble.length + 1) !=  141) {
			return this.iface.errorAcumuladoControl(141, nombreDato);
		}
		temp = qryMod300Tipo2.value("codtipovia");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Tipo de v�a"), 5))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 5);
		
		nombreDato = util.translate("scripts", "Nombre de la v�a");
		if ((inmueble.length + 1) !=  146) {
			return this.iface.errorAcumuladoControl(146, nombreDato);
		}
		temp = qryMod300Tipo2.value("nombrevia");
		temp = flcontmode.iface.pub_formatearTexto(temp);
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Nombre de la v�a"), 50))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 50);
		
		nombreDato = util.translate("scripts", "Tipo de numeraci�n");
		if ((inmueble.length + 1) !=  196) {
			return this.iface.errorAcumuladoControl(196, nombreDato);
		}
		temp = qryMod300Tipo2.value("tiponumeracion");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Tipo de numeraci�n"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3);
		
		nombreDato = util.translate("scripts", "N�mero del inmueble");
		if ((inmueble.length + 1) !=  199) {
			return this.iface.errorAcumuladoControl(199, nombreDato);
		}
		temp = qryMod300Tipo2.value("numero");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "N�mero del inmueble"), 5))
			return false;
		inmueble += flfactppal.iface.pub_cerosIzquierda(temp, 5); 
		
		nombreDato = util.translate("scripts", "Calificaci�n de n�mero");
		if ((inmueble.length + 1) !=  204) {
			return this.iface.errorAcumuladoControl(204, nombreDato);
		}
		temp = qryMod300Tipo2.value("califnumero");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Calificaci�n de n�mero"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3);

		nombreDato = util.translate("scripts", "Bloque");
		if ((inmueble.length + 1) !=  207) {
			return this.iface.errorAcumuladoControl(207, nombreDato);
		}
		temp = qryMod300Tipo2.value("bloque");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Bloque"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3);
		
		nombreDato = util.translate("scripts", "Portal");
		if ((inmueble.length + 1) !=  210) {
			return this.iface.errorAcumuladoControl(210, nombreDato);
		}
		temp = qryMod300Tipo2.value("portal");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Portal"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3); 
		
		nombreDato = util.translate("scripts", "Escalera del inmueble");
		if ((inmueble.length + 1) !=  213) {
			return this.iface.errorAcumuladoControl(213, nombreDato);
		}
		temp = qryMod300Tipo2.value("escalera");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Escalera del inmueble"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3); 
		
		nombreDato = util.translate("scripts", "Piso del inmueble");
		if ((inmueble.length + 1) !=  216) {
			return this.iface.errorAcumuladoControl(216, nombreDato);
		}
		temp = qryMod300Tipo2.value("piso");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Piso del inmueble"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3); 
		
		nombreDato = util.translate("scripts", "Puerta del inmueble");
		if ((inmueble.length + 1) != 219) {
			return this.iface.errorAcumuladoControl(219, nombreDato);
		}
		temp = qryMod300Tipo2.value("puerta");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Puerta del inmueble"), 3))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 3); 
		
		nombreDato = util.translate("scripts", "Complemento");
		if ((inmueble.length + 1) != 222) {
			return this.iface.errorAcumuladoControl(222, nombreDato);
		}
		temp = qryMod300Tipo2.value("complemento");
		temp = flcontmode.iface.pub_formatearTexto(temp);
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Complemento"), 40))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 40); 

		nombreDato = util.translate("scripts", "Localidad");
		if ((inmueble.length + 1) !=  262) {
			return this.iface.errorAcumuladoControl(262, nombreDato);
		}
		temp = qryMod300Tipo2.value("localidad");
		temp = flcontmode.iface.pub_formatearTexto(temp);
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "Localidad"), 30))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 30); 
	
		nombreDato = util.translate("scripts", "Municipio");
		if ((inmueble.length + 1) !=  292) {
			return this.iface.errorAcumuladoControl(292, nombreDato);
		}
		temp = qryMod300Tipo2.value("municipio");
		temp = flcontmode.iface.pub_formatearTexto(temp);
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Municipio"), 30))
			return false;
		inmueble += flfactppal.iface.pub_espaciosDerecha(temp, 30); 
	
		nombreDato = util.translate("scripts", "C�digo de municipio");
		if ((inmueble.length + 1) !=  322) {
			return this.iface.errorAcumuladoControl(322, nombreDato);
		}
		temp = qryMod300Tipo2.value("codmunicipio");
		if (!flcontmode.iface.pub_verificarDato(temp, false, util.translate("scripts", "C�digo de municipio"), 5))
			return false;
		inmueble += flfactppal.iface.pub_cerosIzquierda(temp, 5);
	
		nombreDato = util.translate("scripts", "Provincia");
		if ((inmueble.length + 1) !=  327) {
			return this.iface.errorAcumuladoControl(327, nombreDato);
		}
		temp = qryMod300Tipo2.value("codprovincia");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "Provincia"), 2))
			return false;
		inmueble += flfactppal.iface.pub_cerosIzquierda(temp, 2); 
		
		nombreDato = util.translate("scripts", "C�digo postal");
		if ((inmueble.length + 1) !=  329) {
			return this.iface.errorAcumuladoControl(329, nombreDato);
		}
		temp = qryMod300Tipo2.value("codpostal");
		if (!flcontmode.iface.pub_verificarDato(temp, true, util.translate("scripts", "C�digo postal"), 5))
			return false;
		inmueble += flfactppal.iface.pub_cerosIzquierda(temp, 5); 
		
		nombreDato = util.translate("scripts", "Relleno de blancos hasta 500 caracteres");
		if ((inmueble.length + 1) !=  334) {
			return this.iface.errorAcumuladoControl(334, nombreDato);
		}
		inmueble = flfactppal.iface.pub_espaciosDerecha(inmueble, 500); 
	
		// Fin de registro tipo 2 (Inmueble)

		inmueble += "\r\n";
		contenido3 += inmueble;
	}
	contenido += contenido3;

	if (contenido.endsWith("\r\n")) {
		contenido = contenido.left(contenido.length - 2);
	}
	file.write(contenido);
	file.close();

	MessageBox.information(util.translate("scripts", "Generado fichero en :\n\n" + nombreFichero + "\n\n"), MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton);
}

function oficial_errorAcumuladoControl(acumuladoControl:Number, nombreDato:String):Boolean
{
	var util:FLUtil = new FLUtil;
	MessageBox.warning(util.translate("scripts", "Error al crear el fichero: El dato %1 no comienza en la posici�n %2").arg(nombreDato).arg(acumuladoControl), MessageBox.Ok, MessageBox.NoButton);
	return false;
}

//// OFICIAL /////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////


/** @class_definition boe2011 */
//////////////////////////////////////////////////////////////////
//// BOE2011 /////////////////////////////////////////////////////
/** \D Genera un fichero para realizar la presentaci�n telem�tica del modelo
\end */

function boe2011_presTelematica()
{
    this.iface.presTelematica2011();
}

function boe2011_presTelematica2011() {
    
    var curMod:FLSqlCursor = this.cursor();
    if (!curMod.isValid()){
        return;
    }
    
    var nombreFichero = this.iface.nombreFichero();
    if (!nombreFichero){
        return;
    }
    
    var util:FLUtil = new FLUtil();
    flcontmode.iface.error = "";
    
    util.createProgressDialog(util.translate("scripts", "Generando registro de tipo 1"), 10);
    util.setProgress(2);
    
    var file:Object = new File(nombreFichero);
    file.open(File.WriteOnly);
    
    file.write(this.iface.tiporeg1(curMod) + "\r\n");
    util.setProgress(10);
    util.destroyProgressDialog();
    
    
    var curMod2d:FLSqlCursor = new FLSqlCursor("co_modelo347_tipo2d");
    curMod2d.select("idmodelo = " + curMod.valueBuffer("idmodelo"));
    util.createProgressDialog(util.translate("scripts", "Generando registro de tipo 2 declarados operaciones"), curMod2d.size());
    var progreso:Number = 0;
    while (curMod2d.next()){
        util.setProgress(progreso++);
        file.write(this.iface.tiporeg2d(curMod,curMod2d) + "\r\n");
    }
    util.destroyProgressDialog();
    
    var curMod2i:FLSqlCursor = new FLSqlCursor("co_modelo347_tipo2i");
    curMod2i.select("idmodelo = " + curMod.valueBuffer("idmodelo"));
    util.createProgressDialog(util.translate("scripts", "Generando registro de tipo 2 bienes inmuebles"), curMod2d.size());
    var progreso:Number = 0;
    while (curMod2i.next()){
        util.setProgress(progreso++);
        file.write(this.iface.tiporeg2i(curMod,curMod2i) + "\r\n");
    }
    
    file.close();

    // Genera copia del fichero en codificacion ISO
    file.open(File.ReadOnly);
    var content = file.read();
    file.close();

    var fileIso = new File(nombreFichero + ".iso8859" );
    fileIso.open(File.WriteOnly);
    fileIso.write( sys.fromUnicode( content, "ISO-8859-1" ) );
    fileIso.close();

    util.destroyProgressDialog();
    
    var util:FLUtil = new FLUtil();
    if (flcontmode.iface.error == "") {
        MessageBox.information(util.translate("scripts", "Generado fichero en :\n\n" + nombreFichero+".iso8859" + "\n\n"), MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton);
    } else {
        MessageBox.information(util.translate("scripts", "Se han detectado los siguientes errores :\n\n" +flcontmode.iface.error+ "\n\n"), MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton);
    }
}

function boe2011_nombreFichero():String
{
    
    var nombreFichero:String = FileDialog.getSaveFileName("*.*");
    if (!nombreFichero) {
        MessageBox.warning("No ha indicado el nombre del fichero",MessageBox.Ok, MessageBox.NoButton);
        return "";
    } else {
        return nombreFichero;
    }
}

function boe2011_soporteModelo():String{
    
    var util:FLUtil = new FLUtil();
    
    // Tipo de soporte
    var tipoSoporte:String;
    var presTelematica:String = util.translate("scripts", "Transmisi�n telem�tica");
    var soporteMagnetico:String = util.translate("scripts", "Soporte Magn�tico");
    var soportes:Array = [presTelematica, soporteMagnetico];
    var opcion:String = Input.getItem(util.translate("scripts", "Indique el tipo de soporte"), soportes, presTelematica, false);
    if (!opcion){
        MessageBox.warning("No ha indicado el tipo de soporte.\nSe asignara presentaci�n telem�tica como valor por defecto",MessageBox.Ok,MessageBox.NoButton);
        return "T";
    }
        
    switch (opcion) {
        case presTelematica:
            tipoSoporte = "T";
            break;
    
    case soporteMagnetico:
            tipoSoporte = "C";
            break;
    }
    
    return tipoSoporte;
}
    
function boe2011_tiporeg1(curMod:FLSlqCursor):String {

    //Registro de tipo 1 declarante
    var codReg = "1";
    var desReg:Array = flcontmode.iface.pub_desRegistro347(codReg);
    
    var util:FLUtil = new FLUtil();
    var valorCampo;
    var nombreCampo = "";
    var formatoCampo = "";
    var registro:Object = {};
    
    for (var i = 0; i < desReg.length; i++) {
        nombreCampo = desReg[i][0];
        longitudCampo = desReg[i][2];
        formatoCampo = desReg[i][3];
        if (formatoCampo == "B") {
            valorCampo = " ";
        } else {
            switch(nombreCampo) {
                case "tiporeg":
                    valorCampo = "1";
                    break;
                
                case "modelo":
                    valorCampo = "347";
                    break;
                    
                case "ejercicio":
                    valorCampo = util.sqlSelect("ejercicios","date_part('year',fechainicio)","codejercicio='"+curMod.valueBuffer("codejercicio")+"'");
                    break;
                
                case "tiposoporte":
                    valorCampo = this.iface.soporteModelo();
                    break;
                
                case "complementaria":
                    if (curMod.valueBuffer("complementaria")) {
                        valorCampo = "C";
                    } else {
                        valorCampo = " ";
                    }
                    break;
                case "sustitutiva":
                    if (curMod.valueBuffer("sustitutiva")) {
                        valorCampo = "S";
                    } else{
                        valorCampo = " ";
                    }
                    break;
                    
                case "jusanterior":
                    if (curMod.valueBuffer("complementaria") || curMod.valueBuffer("sustitutiva")) {
                        valorCampo = curMod.valueBuffer("jusanterior");
                    } else {
                        valorCampo = "0";
                    }
                    break;
                
                case "signo":
                    if (curMod.valueBuffer("importetotal") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importetotal":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod.valueBuffer("importetotal"))), 13, 2); 
                    break;
                    
                case "totalarrendamiento":
                    valorCampo = flcontmode.iface.pub_formatoNumero(parseFloat(curMod.valueBuffer("totalarrendamiento")), 13, 2); 
                    break;
                    
                default :
                    valorCampo = curMod.valueBuffer(nombreCampo);
                    break;
            }
        }

        registro[nombreCampo] = valorCampo;
    }
    
    return flcontmode.iface.pub_generarRegistro(desReg,registro);
    
}


function boe2011_tiporeg2d(curMod:FLSlqCursor,curMod2d:FlsqlCursor):String {

    //Registro de tipo 2 declarados
    var codReg = "2d";
    var desReg:Array = flcontmode.iface.pub_desRegistro347(codReg);
    
    var util:FLUtil = new FLUtil();
    var valorCampo;
    var nombreCampo = "";
    var formatoCampo = "";
    var registro:Object = {};
    
    for (var i = 0; i < desReg.length; i++) {
        nombreCampo = desReg[i][0];
        longitudCampo = desReg[i][2];
        formatoCampo = desReg[i][3];
        if (formatoCampo == "B") {
            valorCampo = " ";
        } else {
            switch(nombreCampo) {
                case "tiporeg":
                    valorCampo = "2";
                    break;
                
                case "modelo":
                    valorCampo = "347";
                    break;
                    
                case "ejercicio":
                    valorCampo = util.sqlSelect("ejercicios","date_part('year',fechainicio)","codejercicio='"+curMod.valueBuffer("codejercicio")+"'");
                    break;
                    
                case "cifnif":
                    valorCampo = curMod.valueBuffer(nombreCampo);
                    break;
                
                case "tipohoja":
                    valorCampo = "D";
                    break;
                
                case "signo":
                    if (curMod2d.valueBuffer("importe") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importe":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importe"))), 13, 2); 
                    break;
                    
                case "seguro":
                    if (curMod2d.valueBuffer("seguro"))
                        valorCampo = "X";
                    else
                        valorCampo = " ";
                    break;
                
                case "arrendlocal":
                    if (curMod2d.valueBuffer("arrendlocal"))
                        valorCampo = "X";
                    else
                        valorCampo = " ";
                    break;
                    
                case "importemetalico":
                    valorCampo = flcontmode.iface.pub_formatoNumero(parseFloat(curMod2d.valueBuffer("importemetalico")), 13, 2); 
                    break;
                    
                case "signoinmuebles":
                    if (curMod2d.valueBuffer("importeinmuebles") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importeinmuebles":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importeinmuebles"))), 13, 2); 
                    break;
                 
                case "ejerciciometalico":
                    if (!curMod2d.valueBuffer("importemetalico"))
                        valorCampo = "0";
                    else
                        valorCampo = curMod2d.valueBuffer("ejerciciometalico");
                    break;
                    
                case "signo1t":
                    if (curMod2d.valueBuffer("importe1t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importe1t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importe1t"))), 13, 2); 
                    break;
                    
                case "signoinmuebles1t":
                    if (curMod2d.valueBuffer("importeinmuebles1t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importeinmuebles1t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importeinmuebles1t"))), 13, 2); 
                    break;
                
                case "signo2t":
                    if (curMod2d.valueBuffer("importe2t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importe2t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importe2t"))), 13, 2); 
                    break;
                    
                case "signoinmuebles2t":
                    if (curMod2d.valueBuffer("importeinmuebles2t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importeinmuebles2t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importeinmuebles2t"))), 13, 2); 
                    break;
                 
                case "signo3t":
                    if (curMod2d.valueBuffer("importe3t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importe3t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importe3t"))), 13, 2); 
                    break;
                    
                case "signoinmuebles3t":
                    if (curMod2d.valueBuffer("importeinmuebles3t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importeinmuebles3t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importeinmuebles3t"))), 13, 2); 
                    break;
                
                case "signo4t":
                    if (curMod2d.valueBuffer("importe4t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importe4t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importe4t"))), 13, 2); 
                    break;
                    
                case "signoinmuebles4t":
                    if (curMod2d.valueBuffer("importeinmuebles4t") < 0) {
                        valorCampo = "N"; 
                    }else {
                        valorCampo = " ";
                    }
                    break;
                    
                case "importeinmuebles4t":
                    valorCampo = flcontmode.iface.pub_formatoNumero(Math.abs(parseFloat(curMod2d.valueBuffer("importeinmuebles4t"))), 13, 2); 
                    break;
                    
                default :
                    valorCampo = curMod2d.valueBuffer(nombreCampo);
                    break;
            }
        }

        registro[nombreCampo] = valorCampo;
    }
    
    return flcontmode.iface.pub_generarRegistro(desReg,registro);

}    
    
function boe2011_tiporeg2i(curMod:FLSlqCursor,curMod2i:FlsqlCursor):String {

    //Registro de tipo 2 inmuebles
    var codReg = "2i";
    var desReg:Array = flcontmode.iface.pub_desRegistro347(codReg);
    
    var util:FLUtil = new FLUtil();
    var valorCampo;
    var nombreCampo = "";
    var formatoCampo = "";
    var registro:Object = {};
    
    for (var i = 0; i < desReg.length; i++) {
        nombreCampo = desReg[i][0];
        longitudCampo = desReg[i][2];
        formatoCampo = desReg[i][3];
        if (formatoCampo == "B") {
            valorCampo = " ";
        } else {
            switch(nombreCampo) {
                case "tiporeg":
                    valorCampo = "2";
                    break;
                
                case "modelo":
                    valorCampo = "347";
                    break;
                    
                case "ejercicio":
                   valorCampo = util.sqlSelect("ejercicios","date_part('year',fechainicio)","codejercicio='"+curMod.valueBuffer("codejercicio")+"'");
                    break;
                    
                case "cifnif":
                    valorCampo = curMod.valueBuffer(nombreCampo);
                    break;
                
                case "tipohoja":
                    valorCampo = "I";
                    break;
                    
                case "importe":
                    valorCampo = flcontmode.iface.pub_formatoNumero(parseFloat(curMod2i.valueBuffer("importe")), 13, 2); 
                    break;
                    
                default :
                    valorCampo = curMod2i.valueBuffer(nombreCampo);
                    break;
            }
        }

        registro[nombreCampo] = valorCampo;
    }
    
    return flcontmode.iface.pub_generarRegistro(desReg,registro);

}

//// BOE2011 /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_definition head */
/////////////////////////////////////////////////////////////////
//// DESARROLLO /////////////////////////////////////////////////

//// DESARROLLO /////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////
