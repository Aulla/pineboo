// EnebooCursorClient = formImport.from("sistema/libreria/contexts/shared/infrastructure/EnebooCursorClient.qs")
CondicionesCompraArticulo = formImport.from("facturacion/almacen/contexts/condicionescompraarticulo/domain/CondicionesCompraArticulo.qs")

class CursorCondicionesCompraArticuloQsaRepository {
    var cache_ = {}

    function find(referencia) {
        const articulosProvData = EnebooCursorClient.getDataFromTableRows("articulosprov", "referencia = '" + referencia + "'")
        const primitives = {
            "referencia": referencia,
            "provDefecto": this.getProveedorDefecto(articulosProvData),
            "condiciones_x_proveedor": formARRAY.map(articulosProvData, this.tableRowToPrimitivesCondicionProveedor)
        }
        this.cacheaEntidad(primitives)
        return CondicionesCompraArticulo.fromPrimitives(primitives)
    }

    function getProveedorDefecto(articulosProvData) {
        const esProveedorDefecto = function (condicion) {
            return condicion["pordefecto"]
        }
        const condicionDefecto = formARRAY.find(articulosProvData, esProveedorDefecto)
        return condicionDefecto
            ? condicionDefecto["codproveedor"]
            : null
    }

    function cacheaEntidad(condiciones) {
        const ids = formARRAY.map(condiciones["condiciones_x_proveedor"], formDICT.getClave, "id")
        this.cache_[condiciones["referencia"]] = formARRAY.toDict(ids)
    }
    function cacheaConcicion(condicion, referencia) {
        this.cache_[referencia][condicion["id"]] = true
    }

    function save(condiciones) {
        const condicionesGuardadas = this.find(condiciones.referencia)
        this.saveCondicionesPorProveedor(condicionesGuardadas, condiciones)
    }

    function saveCondicionesPorProveedor(condicionesPrevias, condiciones) {
        const previo = condicionesPrevias.toPrimitives()["condiciones_x_proveedor"]
        const actual = condiciones.toPrimitives()["condiciones_x_proveedor"]

        const previoForTable = formARRAY.map(previo, this.primitivesCondicionProveedorToTableRow, condicionesPrevias)
        const actualForTable = formARRAY.map(actual, this.primitivesCondicionProveedorToTableRow, condiciones)
        EnebooCursorClient.save1M(previoForTable, actualForTable, "articulosprov")
    }

    function primitivesCondicionProveedorToTableRow(primitives, aggregate) {
        const tabla = "articulosprov"
        const camposTabla = formMETA.getCamposTabla(tabla)

        function asignaValorCampo(acum, campo, primitives) {
            var valor
            switch (campo) {
                case "referencia": {
                    valor = aggregate.referencia
                    break
                }
                case "coddivisa": {
                    valor = "EUR"
                    break
                }
                case "pordefecto": {
                    valor = aggregate.provDefecto == primitives["codproveedor"]
                    break
                }
                default: {
                    valor = (campo in primitives)
                        ? primitives[campo]
                        : null
                }
            }
            acum[campo] = valor
            return acum
        }
        return formARRAY.reduce(camposTabla, asignaValorCampo, {}, primitives)
    }

    function tableRowToPrimitivesCondicionProveedor(tableRowData) {
        const tabla = "articulosprov"
        const camposTabla = formMETA.getCamposTabla(tabla)

        function asignaValorPrimitive(acum, campo, tableRowData) {
            var valorCampo = tableRowData[campo]
            switch (campo) {
                // Lo cargamos en la cabecera
                case "provdefecto": {
                    break
                }
                default: {
                    acum[campo] = valorCampo
                }
            }

            return acum
        }
        return formARRAY.reduce(camposTabla, asignaValorPrimitive, {}, tableRowData)
    }
}