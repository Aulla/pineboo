/***************************************************************************
                 lib_str.qs  -  description
                             -------------------
    begin                : mar ene 19 2019
    copyright            : (C) 2019 by Yeboyebo
    email                : mail@yeboyebo
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

function entry_point(user, verb, model, params, method) {
    debug("Hola");
    return;
    const f = get_api_function(verb, model, method);
    if (!f) {
        // raise error
        return false;
    }
    try {
        debug("f = " + f)
        return;
        // if verb != get -> transaction
        const response_data = f(user, params)
        // response(response_data)
        return response_data;
    }
  catch (e) {
    debug("Error " + e);
  }
}

// Esto puede hacerlo el motor
function get_api_function(verb, model, method) {
    var f = false;
    switch (model) {
        case 'gt_tareas': {
            switch (verb) {
                case 'get': {
                    switch (method) {
                        case undefined: {
                            f = "Hola";
                            //f = formgt_tareas_api_get.iface.get;
                            break;
                        }
                    }
                    break;
                }
            }
            break;
        }
    }
    return f
}
