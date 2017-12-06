/***************************************************************************
                      masterremesas_prov.qs  -  description
                             -------------------
    begin                : jue dic 21 2006
    copyright            : (C) 2006 by InfoSiAL S.L.
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
	function imprimir() {
		return this.ctx.oficial_imprimir();
	}
}
//// OFICIAL /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

/** @class_declaration norma34 */
/////////////////////////////////////////////////////////////////
//// NORMA 34 ///////////////////////////////////////////////////
class norma34 extends oficial {
    function norma34( context ) { oficial ( context ); }
	function init() {
		this.ctx.norma34_init();
	}
	function volcarADisco34() {
		return this.ctx.norma34_volcarADisco34();
	}
	function volcarADisco34sepa() {
		return this.ctx.norma34_volcarADisco34sepa();
	}
}
//// NORMA 34 ///////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_declaration head */
/////////////////////////////////////////////////////////////////
//// DESARROLLO /////////////////////////////////////////////////
class head extends norma34 {
    function head( context ) { norma34 ( context ); }
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
		var curImprimir:FLSqlCursor = new FLSqlCursor("i_recibosprov");
		curImprimir.setModeAccess(curImprimir.Insert);
		curImprimir.refreshBuffer();
		curImprimir.setValueBuffer("descripcion", "temp");
		flfactinfo.iface.pub_lanzarInforme(curImprimir, "i_resrecibosprov", "recibosprov.codigo", "", false, false, "idrecibo IN (SELECT idrecibo FROM pagosdevolprov WHERE idremesa = " + idRemesa + ")");
	} else
		flfactppal.iface.pub_msgNoDisponible("Informes");
}

//// OFICIAL /////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition norma34 */
/////////////////////////////////////////////////////////////////
//// NORMA 34 ///////////////////////////////////////////////////
function norma34_init()
{
	var _i = this.iface;

	_i.__init();
	connect(this.child("tbnNorma34"), "clicked()", _i, "volcarADisco34");
	connect(this.child("tbnNorma34Sepa"), "clicked()", _i, "volcarADisco34sepa");
}
/** \D Abre el formulario para guardar en disco
\end */

function norma34_volcarADisco34()
{
	var cursor = this.cursor();
	cursor.setAction("vdisco34");
	cursor.editRecord();
	cursor.setAction("remesasprov");
}

function norma34_volcarADisco34sepa()
{
	var cursor = this.cursor();
	cursor.setAction("vdisco34sepa");
	cursor.editRecord();
	cursor.setAction("remesasprov");
}
//// NORMA 34 ///////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

/** @class_definition head */
/////////////////////////////////////////////////////////////////
//// DESARROLLO /////////////////////////////////////////////////

//// DESARROLLO /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

