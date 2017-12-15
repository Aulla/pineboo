/***************************************************************************
                      masterremesas.qs  -  description
                             -------------------
    begin                : lun may 31 2004
    copyright            : (C) 2004 by InfoSiAL S.L.
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
	function recordDelAfterremesas() { return this.ctx.interna_recordDelAfterremesas(); }
}
//// INTERNA /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_declaration oficial */
//////////////////////////////////////////////////////////////////
//// OFICIAL /////////////////////////////////////////////////////
class oficial extends interna {
    function oficial( context ) { interna( context ); }
		function imprimir() {
				return this.ctx.oficial_imprimir();
		}
		function volcarADisco() {
				return this.ctx.oficial_volcarADisco();
		}
}
//// OFICIAL /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_declaration norma58 */
/////////////////////////////////////////////////////////////////
//// NORMA_58 ///////////////////////////////////////////////////
class norma58 extends oficial /** %from: oficial */ {
    function norma58( context ) { oficial ( context ); }
	function init() {
		return this.ctx.norma58_init();
	}
	function volcarADisco58() {
		return this.ctx.norma58_volcarADisco58();
	}
}
//// NORMA_58 ///////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_declaration sepa19b2b */
/////////////////////////////////////////////////////////////////
//// SEPA19B2B //////////////////////////////////////////////////
class sepa19b2b extends norma58 /** %from: oficial */ {
    function sepa19b2b( context ) { norma58 ( context ); }
		function init() {
				return this.ctx.sepa19b2b_init();
		}
		function volcarADisco_sepa19b2b_clicked() {
				return this.ctx.sepa19b2b_volcarADisco_sepa19b2b_clicked();
		}
}
//// SEPA19B2B //////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_declaration head */
/////////////////////////////////////////////////////////////////
//// DESARROLLO /////////////////////////////////////////////////
class head extends sepa19b2b {
    function head( context ) { sepa19b2b ( context ); }
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

		connect(this.child("toolButtonPrint"), "clicked()", this, "iface.imprimir");
		connect(this.child("pbnADisco"), "clicked()", this, "iface.volcarADisco");
}

/** \C Para todos los recibos pertenecientes a la remesa, el �ltimo pago o devoluci�n de la lista de pagos y devoluciones se elimina, y se permite de nuevo crear nuevos pagos y devoluciones para el recibo. Se actualiza el estado del recibo a devuelto o emitido, en funci�n de si quedan pagos y devoluciones o no respectivamente.
\end */
function interna_recordDelAfterremesas()
{
/*
	var idremesa:Number = this.cursor().valueBuffer("idremesa");
	var curRecibos:FLSqlCursor = new FLSqlCursor("reciboscli");
	var curPagosDev:FLSqlCursor = new FLSqlCursor("pagosdevolcli");
	var curFactura:FLSqlCursor = new FLSqlCursor("facturascli");
	var recibo:Number, idfactura:Number;
	with(curRecibos) {
		select("idremesa = " + idremesa);
		while (next()) {
			setModeAccess(Edit);
			refreshBuffer();
			setValueBuffer("idremesa", 0);
			recibo = valueBuffer("idrecibo");
			idfactura = valueBuffer("idfactura");
			with(curPagosDev) {
				select("idrecibo = " + recibo + " ORDER BY idpagodevol");
				if (last()) {
					setModeAccess(Del);
					refreshBuffer();
					commitBuffer();
				}
				select("idrecibo = " + recibo + " ORDER BY idpagodevol");
				if (last())
					setUnLock("editable", true);
			}
			if (curPagosDev.size() == 0)
				setValueBuffer("estado", "Emitido");
			else
				setValueBuffer("estado", "Devuelto");
			commitBuffer();
			curFactura.select("idfactura = " + idfactura);
			if (curFactura.first())
				curFactura.setUnLock("editable", true);
		}
	}
*/
}
//// INTERNA /////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition oficial */
//////////////////////////////////////////////////////////////////
//// OFICIAL /////////////////////////////////////////////////////
/** \D Crea un informe con el listado de registros de la remesa. Funciona cuando est� cargado el m�dulo de informes
\end */
function oficial_imprimir()
{
	if (this.cursor().size() == 0)
		return;

	if (sys.isLoadedModule("flfactinfo")) {
		var idRemesa:Number = this.cursor().valueBuffer("idremesa");
		var curImprimir:FLSqlCursor = new FLSqlCursor("i_remesascli");
		curImprimir.setModeAccess(curImprimir.Insert);
		curImprimir.refreshBuffer();
		curImprimir.setValueBuffer("descripcion", "temp");
		curImprimir.setValueBuffer("i_remesas_idremesa", idRemesa);
		flfactinfo.iface.pub_lanzarInforme(curImprimir, "i_remesascli");
	} else
		flfactppal.iface.pub_msgNoDisponible("Informes");
}

/** \D Abre el formulario para guardar en disco
\end */
function oficial_volcarADisco()
{
		var cursor:FLSqlCursor = this.cursor();
		cursor.setAction("vdisco");
		cursor.editRecord();
		cursor.setAction("remesas");
}

//// OFICIAL /////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition norma58 */
/////////////////////////////////////////////////////////////////
//// NORMA_58 ///////////////////////////////////////////////////

function norma58_init()
{
	this.iface.__init();
	connect(this.child("pbnADisco58"), "clicked()", this, "iface.volcarADisco58");
}

function norma58_volcarADisco58()
{
	var cursor:FLSqlCursor = this.cursor();
	cursor.setAction("vdisco58");
	cursor.editRecord();
	cursor.setAction("remesas");
}

//// NORMA_58 ///////////////////////////////////////////////////
//////////////////////////////////////////////////////////////

/** @class_definition sepa19b2b */
/////////////////////////////////////////////////////////////////
//// SEPA19B2B /////////////////////////////////////////////////

function sepa19b2b_init()
{
	var _i = this.iface;

	_i.__init();

	connect(this.child("pbnADisco_sepa19b2b"), "clicked()", _i, "volcarADisco_sepa19b2b_clicked");
}

function sepa19b2b_volcarADisco_sepa19b2b_clicked()
{
		var cursor = this.cursor();
		cursor.setAction("vdisco_sepa19b2b");
		cursor.editRecord();
		cursor.setAction("remesas");
}

//// SEPA19B2B //////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition head */
/////////////////////////////////////////////////////////////////
//// DESARROLLO /////////////////////////////////////////////////

//// DESARROLLO /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

