$(document).ready(function () {
    iniciarTabla();
});

let TAX_RATE = 0.00; // Solo para inicializar valor


function iniciarTabla() {
    tableContabilizados = $('#tblContabilizados').DataTable({
        destroy: true,
        responsive: true,
        autoWidth: false,
        order: [[0, 'asc']],
        scrollX: true,
        "dom":
        "<'row mb-2'" +
        "<'col-sm-6 d-flex align-items-center justify-content-start'l>" +
        "<'col-sm-6 search-container d-flex align-items-center justify-content-end'f>" + // Modificado: se agregó search-container
        ">" +
        "<'table-responsive'tr>" +
        "<'row'" +
        "<'col-sm-12 col-md-5 d-flex align-items-center justify-content-center justify-content-md-start'i>" +
        "<'col-sm-12 col-md-7 d-flex align-items-center justify-content-center justify-content-md-end'p>" +
        ">",
        "language": {
            "lengthMenu": "",
            "sProcessing": "Procesando...",
            "sZeroRecords": "No se encontraron resultados",
            "sEmptyTable": "Ningún dato disponible en esta tabla",
            "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
            "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix": "",
            "sSearch": "Buscar:",
            "sUrl": "",
            "sInfoThousands": ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            }
        },
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchSolicitudes'
            },
            dataSrc: ""
        },
        columns: [
            // Mantén tus columnas actuales
            { "data": null },
            { "data": "DocNum" },
            { "data": "Serie" },
            { "data": "ReqIdUser" },
            { "data": "TotalImp" },
            { "data": null },
            { "data": null },
        ],
        columnDefs: [
            {
                targets: [4],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    // Usar row.moneda directamente desde los datos de la fila
                    var monedaTexto = row.moneda ? row.moneda.trim() : '';
                    var monedaSimbolo;
                    if (monedaTexto === 'SOL') {
                        monedaSimbolo = 'S/. ';
                    } else if (monedaTexto === 'USD') {
                        monedaSimbolo = '$ ';
                    } else if (monedaTexto === 'EUR') {
                        monedaSimbolo = '€ ';
                    } else {
                        monedaSimbolo = ''; // Valor por defecto si no hay moneda
                    }

                    if (row.DocStatus === 'P' || row.DocStatus === 'R') {
                        return monedaSimbolo + data;
                    } else if (row.DocStatus === 'A' || row.DocStatus === 'C' || row.DocStatus === 'CP') {
                        var totalImp = 0;
                        $.ajax({
                            url: '/erp/getLineDetails/',
                            type: 'POST',
                            data: {
                                'docEntry': row.DocEntry,
                                'lineStatus': 'A,C,L'
                            },
                            headers: { "X-CSRFToken": csrftoken },
                            async: false,
                            success: function (response) {
                                console.log('Response from getLineDetails:', response);
                                for (var i = 0; i < response.length; i++) {
                                    totalImp += response[i].totalimpdet;
                                }
                            },
                            error: function (xhr, status, error) {
                                console.error('Error al obtener los detalles de las líneas:', error);
                            }
                        });
                        return monedaSimbolo + totalImp.toFixed(2);
                    }
                    return monedaSimbolo + '0.00';
                },
            },
            {
                targets: [0],
                class: "text-center",
                orderable: true,
                render: function (data, type, row, meta) {
                    return meta.row + 1;
                },
            },
            {
                targets: [1],
                class: "text-center",
                orderable: true,
                render: function (data, type, row, meta) {
                    return '<span class="badge badge-primary">' + row.DocNum + '</span>';
                },

            },
            {
                targets: [2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row, meta) {
                    if (row.Serie == 120) {
                        return '<span class="badge badge-black">120 </span> / <span class="badge badge-success"> Primario</span>';
                    } else {
                        return row.Serie;
                    }
                },
            },
            {
                targets: [-2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row, meta) {
                    return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox" value="' + row.DocEntry + '" id="' + row.DocEntry + '" style="width: 20px; height: 50px; vertical-align: center;" ></input></div>';
                },
            },
            {
                targets: [-1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    return '<button rel="remove" type="button" class="btn btn-primary btn-xs btn-flat" onclick="mostrarDetallesContabilizados(' + parseInt(row.DocEntry) + ')"><i class="fas fa-info-circle"></i> Detalles</button>';
                },
            },
        ],
        initComplete: function (settings, json) {
            $('#tblContabilizados').on('change', 'input[type="checkbox"]', function () {
                var $checkbox = $(this);
                var table = $('#tblContabilizados').DataTable();
                var rowDataC = table.row($checkbox.closest('tr')).data();
                obtenerTaxRate(rowDataC.TaxCode); // Obtener la tasa de impuesto basada en el TaxCode de la solicitud

                if ($checkbox.is(':checked')) {
                    if (rowDataC.DocType === 'I') {
                        $.ajax({
                            url: window.location.pathname,
                            type: 'POST',
                            data: {
                                'action': 'getDetails',
                                'code': rowDataC.DocEntry
                            },
                            dataSrc: "",
                            success: function (response) {
                                for (var j = 0; j < response.length; j++) {
                                    // Eliminamos la búsqueda de productos iguales
                                    var index = checked.findIndex(function (item) {
                                        return item.Code === response[j].Code && item.ItemCode === response[j].ItemCode;
                                    });
                                    
                                    if (index === -1) {
                                        // Agregamos cada producto como una nueva línea
                                        orden.add({
                                            ...response[j],
                                            moneda: rowDataC.moneda, // Agregar moneda desde la fila de tblContabilizados
                                            LineUniqueId: response[j].Code + '_' + new Date().getTime() + '_' + j
                                        });
                                        orden.list();
                                        checked.push({ 
                                            Code: response[j].Code, 
                                            ItemCode: response[j].ItemCode,
                                            LineUniqueId: response[j].Code + '_' + new Date().getTime() + '_' + j
                                        });
                                    }
                                }
                            },
                            error: function (xhr, status, error) {
                                console.error('Error en la solicitud:', status, error);
                            }
                        });
                    } else if (rowDataC.DocType === 'S') {
                        $.ajax({
                            url: window.location.pathname,
                            type: 'POST',
                            data: {
                                'action': 'getDetails',
                                'code': rowDataC.DocEntry
                            },
                            dataSrc: "",
                            success: function (response) {
                                console.log('rowDataC.moneda:', rowDataC.moneda);
                                for (var j = 0; j < response.length; j++) {
                                    var index = checkedSv.findIndex(function (item) {
                                        return item.Code === response[j].Code && item.ItemCode === response[j].ItemCode;
                                    });
                                    
                                    if (index === -1) {
                                        // Agregamos cada servicio como una nueva línea
                                        ordenServ.add({
                                            ...response[j],
                                            moneda: rowDataC.moneda, // Agregar moneda desde la fila de tblContabilizados
                                            LineUniqueId: response[j].Code + '_' + new Date().getTime() + '_' + j
                                        });
                                        ordenServ.list();
                                        checkedSv.push({ 
                                            Code: response[j].Code, 
                                            ItemCode: response[j].ItemCode,
                                            LineUniqueId: response[j].Code + '_' + new Date().getTime() + '_' + j
                                        });
                                    }
                                }
                            },
                            error: function (xhr, status, error) {
                                console.error('Error en la solicitud:', status, error);
                            }
                        });
                    }
                } else {
                    if (rowDataC.DocType === 'I') {
                        $.ajax({
                            url: window.location.pathname,
                            type: 'POST',
                            data: {
                                'action': 'getDetails',
                                'code': rowDataC.DocEntry
                            },
                            dataSrc: "",
                            success: function (response) {
                                for (var j = 0; j < response.length; j++) {
                                    if (orden.items.item.length > 0) {
                                        // Eliminar todas las líneas que coincidan con el Code de la solicitud
                                        orden.items.item = orden.items.item.filter(function(item) {
                                            return item.Code !== response[j].Code;
                                        });
                                        orden.list();
                                    }
                                    
                                    // Eliminar del array checked
                                    checked = checked.filter(function(item) {
                                        return item.Code !== response[j].Code;
                                    });
                                }
                            },
                            error: function (xhr, status, error) {
                                console.error('Error en la solicitud:', status, error);
                            }
                        });
                    } else if (rowDataC.DocType === 'S') {
                        $.ajax({
                            url: window.location.pathname,
                            type: 'POST',
                            data: {
                                'action': 'getDetails',
                                'code': rowDataC.DocEntry
                            },
                            dataSrc: "",
                            success: function (response) {
                                for (var j = 0; j < response.length; j++) {
                                    if (ordenServ.items.item.length > 0) {
                                        for (var i = 0; i < ordenServ.items.item.length; i++) {
                                            if (ordenServ.items.item[i].ItemCode == response[j].ItemCode && ordenServ.items.item[i].Almacen == response[j].Almacen && ordenServ.items.item[i].LineVendor == response[j].LineVendor && ordenServ.items.item[i].UnidadMedida == response[j].UnidadMedida) {
                                                ordenServ.items.item[i].Quantity = ordenServ.items.item[i].Quantity - response[j].Quantity;
                                                ordenServ.items.item[i].total = ordenServ.items.item[i].total - response[j].total;
                                                if (ordenServ.items.item[i].Quantity === 0 && ordenServ.items.item[i].total === 0) {
                                                    ordenServ.items.item.splice(i, 1);
                                                }
                                                ordenServ.list();
                                                break;
                                            }
                                        }
                                    }
                                    var index = checkedSv.findIndex(function (item) {
                                        return item.Code === response[j].Code && item.ItemCode === response[j].ItemCode;
                                    });
                                    if (index > -1) {
                                        checkedSv.splice(index, 1);
                                    }
                                }
                            },
                            error: function (xhr, status, error) {
                                // Maneja cualquier error aquí
                                console.error('Error en la solicitud:', status, error);
                            }
                        });
                    }
                }
                updateSubtotals('productos');
                updateSubtotals('servicios');
            });
            
        }
    });
}

//Métodos para manejar las Tablas Productos y Servicios

var tblOrdenProd;
var orden = {
    items: {
        item: []
    },
    // add: function (item) {
    //     this.items.item.push(item);
    // },
    //PROBLEMA DE /X DISPONIBLES CAMBIA
    // add: function (item) {
    //     // Asegurar que los valores iniciales sean correctos
    //     const quantity = Math.min(item.Quantity, item.Quantity_rest);
    //     item.Quantity = quantity;
    //     item.total = quantity * item.Precio;
    //     // Calcular los valores rest
    //     item.Quantity_rest = Math.max(0, item.Quantity_rest - quantity);
    //     item.total_rest = item.Quantity_rest * item.Precio;
    //     this.items.item.push(item);
    // },

    add: function (item) {
        const quantity = Math.min(item.Quantity, item.Quantity_rest);
        item.Quantity = quantity;
        item.total = quantity * item.Precio;
        item.Quantity_rest = Math.max(0, item.Quantity_rest - quantity);
        item.total_rest = item.Quantity_rest * item.Precio;
        item.originalQuantity = item.Quantity_rest + quantity;
        this.items.item.push(item);
        this.list(); // Actualiza la tabla
        updateSubtotals('productos'); // Actualiza subtotales después de agregar
    },
    list: function (item) {
        tblOrdenProd = $('#tblOrdenProd').DataTable({
            destroy: true,
            responsive: true,
            autoWidth: false,
            scrollX: true,
            "language": {
                "sProcessing": "Procesando...",
                "sLengthMenu": "_MENU_ registros",
                "sZeroRecords": "No se encontraron resultados",
                "sEmptyTable": "Ningún dato disponible en esta tabla",
                "sInfo": "",
                "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
                "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
                "sInfoPostFix": "",
                "sSearch": "Buscar:",
                "sUrl": "",
                "sInfoThousands": ",",
                "sLoadingRecords": "Cargando...",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "oAria": {
                    "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                    "sSortDescending": ": Activar para ordenar la columna de manera descendente"
                }
            },
            data: this.items.item,
            columns: [
                { "data": null },
                { "data": "ItemCode" },
                { "data": "Description" },
                { 
                    "data": "Quantity",
                    render: function(data, type, row) {
                        if (type === 'display') {
                            return `<div class="d-flex align-items-center">
                                       <input type="number" 
                                              class="form-control quantity-input me-2" 
                                              value="${row.Quantity}" 
                                              min="1" 
                                              max="${row.originalQuantity}"
                                              style="width: 80px;">
                                       <span class="text-muted">/ ${row.originalQuantity} disponibles</span>
                                   </div>`;
                        }
                        return data;
                    }
                },
                { 
                    "data": "total",
                    render: function (data, type, row) {
                        // Usar row.moneda directamente desde los datos de la fila
                        var monedaTexto = row.moneda ? row.moneda.trim() : '';
                        var monedaSimbolo;
                        if (monedaTexto === 'SOL') {
                            monedaSimbolo = 'S/. ';
                        } else if (monedaTexto === 'USD') {
                            monedaSimbolo = '$ ';
                        } else if (monedaTexto === 'EUR') {
                            monedaSimbolo = '€ ';
                        } else {
                            monedaSimbolo = ''; // Valor por defecto si no hay moneda
                        }
                        return `${monedaSimbolo}${(row.Quantity * row.Precio).toFixed(2)}`;
                    }
                },
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: "text-center",
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    },
                },
            ],
            initComplete: function (settings, json) {
                updateSubtotals('productos'); // Actualiza subtotales al cargar la tabla
            }
        });

        // Evento para cambios en la cantidad
        $('#tblOrdenProd').on('change', '.quantity-input', function() {
            var $input = $(this);
            var newQuantity = parseInt($input.val());
            var row = tblOrdenProd.row($input.closest('tr')).data();
            
            if (newQuantity === 0) {
                $.alert({
                    title: 'Error',
                    content: `La cantidad no puede ser menor a 1 para el Producto: ${row.Description}`,
                    type: 'red',
                    theme: 'modern'
                });
                $input.val(row.originalQuantity);
                newQuantity = row.originalQuantity;
            } else if (newQuantity > row.originalQuantity) {
                $.alert({
                    title: 'Error',
                    content: `La cantidad no puede exceder ${row.originalQuantity} unidades disponibles del Producto: ${row.Description}`,
                    type: 'red',
                    theme: 'modern'
                });
                $input.val(row.originalQuantity);
                newQuantity = row.originalQuantity;
            }
            
            row.Quantity = newQuantity;
            row.total = newQuantity * row.Precio;
            row.Quantity_rest = Math.max(0, row.originalQuantity - newQuantity);
            row.total_rest = row.Quantity_rest * row.Precio;
            
            tblOrdenProd.row($input.closest('tr')).data(row).draw(false);
            var index = orden.items.item.findIndex(item => item.Code === row.Code);
            if (index !== -1) {
                orden.items.item[index] = row;
            }
            updateSubtotals('productos'); // Actualiza subtotales después de cambiar cantidad
        });
    },
    delete: function () {
        tblOrdenProd.clear().draw();
        orden.items.item = [];
        this.list();
        updateSubtotals('productos'); // Actualiza subtotales después de eliminar todo
    }
};

var tblOrdenServ;
var ordenServ = {
    items: {
        item: []
    },
    add: function (item) {
        this.items.item.push(item);
        this.list();
        updateSubtotals('servicios'); // Actualiza subtotales después de agregar
    },
    list: function (item) {
        tblOrdenServ = $('#tblOrdenServ').DataTable({
            destroy: true,
            responsive: true,
            autoWidth: false,
            scrollX: true,
            "language": {
                "sProcessing": "Procesando...",
                "sLengthMenu": "_MENU_ registros",
                "sZeroRecords": "No se encontraron resultados",
                "sEmptyTable": "Ningún dato disponible en esta tabla",
                "sInfo": "",
                "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
                "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
                "sInfoPostFix": "",
                "sSearch": "Buscar:",
                "sUrl": "",
                "sInfoThousands": ",",
                "sLoadingRecords": "Cargando...",
                "oPaginate": {
                    "sFirst": "Primero",
                    "sLast": "Último",
                    "sNext": "Siguiente",
                    "sPrevious": "Anterior"
                },
                "oAria": {
                    "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                    "sSortDescending": ": Activar para ordenar la columna de manera descendente"
                }
            },
            data: this.items.item,
            columns: [
                { "data": null },
                { "data": "ItemCode" },
                { "data": "Description" },
                { "data": "Quantity" },
                { 
                    "data": "total",
                    render: function (data, type, row) {
                        // Usar row.moneda directamente desde los datos de la fila
                        var monedaTexto = row.moneda ? row.moneda.trim() : '';
                        var monedaSimbolo;
                        if (monedaTexto === 'SOL') {
                            monedaSimbolo = 'S/. ';
                        } else if (monedaTexto === 'USD') {
                            monedaSimbolo = '$ ';
                        } else if (monedaTexto === 'EUR') {
                            monedaSimbolo = '€ ';
                        } else {
                            monedaSimbolo = ''; // Valor por defecto si no hay moneda
                        }
                        return `${monedaSimbolo}${(row.Quantity * row.Precio).toFixed(2)}`;
                    }
                }
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: "text-center",
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    },
                },
            ],
            initComplete: function (settings, json) {
                updateSubtotals('servicios'); // Actualiza subtotales al cargar la tabla
            }
        });
    },
    delete: function () {
        tblOrdenServ.clear().draw();
        ordenServ.items.item = [];
        this.list();
        updateSubtotals('servicios'); // Actualiza subtotales después de eliminar todo
    }
}

//Listener para el botón remove en tabla Productos y tabla Servicios

$(document).ready(function () {
    $('#tblOrdenProd tbody').on('click', 'a[rel="remove"]', function () {
        var trIndex = $('#tblOrdenProd').DataTable().cell($(this).closest('td')).index();
        var itemCodeToRemove = orden.items.item[trIndex.row].ItemCode;
        var CodeToRemove = orden.items.item[trIndex.row].Code;
        orden.items.item.splice(trIndex.row, 1);
        orden.list();
        checked = checked.filter(function (item) {
            return item.ItemCode !== itemCodeToRemove;
        });
        var table = $('#tblContabilizados').DataTable();
        for (var p = 0; p < table.data().count(); p++) {
            (function (p) {
                var data = table.row(p).data();
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'getDetails',
                        'code': data.DocEntry
                    },
                    success: function (response) {
                        for (var l = 0; l < response.length; l++) {
                            if (response[l].ItemCode == itemCodeToRemove) {
                                var rowNode = table.row(p).node();
                                if (rowNode) {
                                    var $checkbox = $(rowNode).find('input[type="checkbox"]');
                                    $checkbox.prop('checked', false);
                                }
                            }
                        }
                    },
                    error: function (xhr, status, error) {
                        console.error('Error en la solicitud:', status, error);
                    }
                });
            })(p);
        }
    });
});

$(document).ready(function () {
    $('#tblOrdenServ tbody').on('click', 'a[rel="remove"]', function () {
        var trIndex = $('#tblOrdenServ').DataTable().cell($(this).closest('td')).index();

        console.log("trIndex para Servicios:", trIndex); // Agrega esta línea

        var itemCodeToRemove = ordenServ.items.item[trIndex.row].ItemCode;
        var CodeToRemove = ordenServ.items.item[trIndex.row].Code;
        ordenServ.items.item.splice(trIndex.row, 1);
        ordenServ.list();
        //ordenServ = checkedSv.filter(function (item) {
        checkedSv = checkedSv.filter(function (item) {
            return item.ItemCode !== itemCodeToRemove;
        });
        var table = $('#tblContabilizados').DataTable();
        for (var p = 0; p < table.data().count(); p++) {
            (function (p) {
                var data = table.row(p).data();
                $.ajax({
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'getDetails',
                        'code': data.DocEntry
                    },
                    success: function (response) {
                        for (var l = 0; l < response.length; l++) {
                            if (response[l].ItemCode == itemCodeToRemove) {
                                var rowNode = table.row(p).node();
                                if (rowNode) {
                                    var $checkbox = $(rowNode).find('input[type="checkbox"]');
                                    $checkbox.prop('checked', false);
                                }
                            }
                        }
                    },
                    error: function (xhr, status, error) {
                        console.error('Error en la solicitud:', status, error);
                    }
                });
            })(p);
        }
    });
});


//Función para mostrar datos de detalle de una solicitud en un modal
function mostrarDetallesContabilizados(docNum) {
    var data = $('#tblContabilizados').DataTable().row(function (index, data) {
        return parseInt(data.DocEntry) === parseInt(docNum);
    }).data();
    $('#idSolicitud').text(data.DocNum);
    $('#InputDocEntry').text(data.DocEntry);
    $('#detallesDocNum').text(data.DocNum);
    $('#detallesReqIdUser').text(data.ReqIdUser);
    $('#departmentUser').text(data.Department);
    if (data.DocType === 'I') {
        $('#detallesDocType').text('Artículo');
        tablaDetalleProducto(docNum);
    } else if (data.DocType === 'S') {
        $('#detallesDocType').text('Servicio');
        tablaDetalleServicio(docNum);
    } else {
        $('#detallesDocType').text('No especificado');
    }
    $('#detallesMoneda').text(data.moneda);
    $('#detalleSerie').text(data.Serie);
    $('#detallesTaxCode').text(data.TaxCode);
    $('#detallesDocDate').text(data.DocDate);
    $('#detallesDocDueDate').text(data.DocDueDate);
    if (data.DocStatus === 'P') {
        $('#detallesDocStatus').text('Pendiente');
        if ($('#btnAprobar').length && $('#btnRechazar').length) {
            document.getElementById("btnAprobar").disabled = false;
            document.getElementById("btnRechazar").disabled = false;
        }
    } else if (data.DocStatus === 'A') {
        $('#detallesDocStatus').text('Aprobado por Jefatura');
        if ($('#btnAprobar').length && $('#btnRechazar').length) {
            disableAndMakeTransparent();
        }

    } else if (data.DocStatus === 'R') {
        $('#detallesDocStatus').text('Rechazado por Jefatura');
        if ($('#btnAprobar').length && $('#btnRechazar').length) {
            disableAndMakeTransparent();
        }
    } else if (data.DocStatus === 'C') {
        $('#detallesDocStatus').text('Contabilizado');
        if ($('#btnAprobar').length && $('#btnRechazar').length) {
            disableAndMakeTransparent();
        }
    } else if (data.DocStatus === 'CP') {
        $('#detallesDocStatus').text('Contabilizado Parcial');
        if ($('#btnAprobar').length && $('#btnRechazar').length) {
            disableAndMakeTransparent();
        }
    }
    else {
        $('#detallesDocStatus').text('No especificado');
    }
    $('#detallesTotal').text(data.Total);
    $('#detallesTotalImp').text(data.TotalImp);
    if ($.fn.DataTable.isDataTable('#tblDetalles')) {
        $('#tblDetalles').DataTable().destroy();
    }
    $('#modalDetallesContabilizados').modal('show');
}

//Funciones que manejan el detalle de un producto
var checked = [];
var checkedSv = [];
function tablaDetalleProducto(docNum) {
    $("#tblDetallesServ").hide();
    $("#tblDetallesServ_wrapper").hide();
    $("#tblDetallesProd").show();
    // Desvincula eventos previos
    $('#tblDetallesProd').off('change', 'input[type="checkbox"]')
    $('#tblDetallesProd').DataTable({
        destroy: true,
        responsive: true,
        autoWidth: false,
        "language": {
            "sProcessing": "Procesando...",
            "sLengthMenu": "",
            "sZeroRecords": "No se encontraron resultados",
            "sEmptyTable": "Ningún dato disponible en esta tabla",
            "sInfo": "",
            "sInfoEmpty": "",
            "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix": "",
            "sSearch": "Buscar:",
            "sUrl": "",
            "sInfoThousands": ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            }
        },
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'showDetails',
                'id': docNum
            },
            dataSrc: ""
        },
        columns: [
            { "data": "ItemCode" },
            { "data": "LineVendor" },
            { "data": "Description" },
            { "data": "Quantity" },
            {
                data: 'Precio',
                render: function(data, type, row) {
                    // Obtener el texto de la moneda desde el elemento HTML
                    var monedaTexto = $('#detallesMoneda').text().trim(); // Asegúrate de eliminar espacios en blanco

                    // Definir el símbolo de la moneda basado en el texto obtenido
                    var monedaSimbolo;
                    if (monedaTexto === 'SOL') {
                        monedaSimbolo = 'S/. ';
                    } else if (monedaTexto === 'USD') {
                        monedaSimbolo = '$ ';
                    } else if (monedaTexto === 'EUR') {
                        monedaSimbolo = '€ ';
                    } else {
                        monedaSimbolo = ''; // En caso de que no coincida con ninguna moneda conocida
                    }
                    return monedaSimbolo + parseFloat(data).toFixed(2);
                }
            },
            { "data": "UnidadMedida" },
            { "data": "Almacen" },
            { "data": "total" },
            { "data": null }
        ],
        columnDefs: [
            {
                targets: [-2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    // Obtener el texto de la moneda desde el elemento HTML
                    var monedaTexto = $('#detallesMoneda').text().trim(); // Asegúrate de eliminar espacios en blanco

                    // Definir el símbolo de la moneda basado en el texto obtenido
                    var monedaSimbolo;
                    if (monedaTexto === 'SOL') {
                        monedaSimbolo = 'S/. ';
                    } else if (monedaTexto === 'USD') {
                        monedaSimbolo = '$ ';
                    } else if (monedaTexto === 'EUR') {
                        monedaSimbolo = '€ ';
                    } else {
                        monedaSimbolo = ''; // En caso de que no coincida con ninguna moneda conocida
                    }

                    var value = parseFloat(row.total).toFixed(2);
                    //var sol = 'S/. ';
                    return monedaSimbolo + value;
                },
            },
            {
                targets: [-1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    if (checked.length > 0) {
                        for (var i = 0; i < checked.length; i++) {
                            if (checked[i].Code === row.Code) {
                                return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" checked></input></div>';
                            }
                        }
                        return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ></input></div>';
                    } else {
                        return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ></input></div>';
                    }
                },
            },
        ],
        // initComplete: function (settings, json) {
        //     $('#tblDetallesProd').on('change', 'input[type="checkbox"]', function () {
        //         var founded = false;
        //         var atLeastOne = false;
        //         var $checkbox = $(this);
        //         var table = $('#tblDetallesProd').DataTable();
        //         var rowData = table.row($checkbox.closest('tr')).data();
        //         if ($checkbox.is(':checked')) {
        //             if (orden.items.item.length > 0) {
        //                 for (var i = 0; i < orden.items.item.length; i++) {
        //                     if (orden.items.item[i].ItemCode == rowData.ItemCode && orden.items.item[i].Almacen == rowData.Almacen && orden.items.item[i].LineVendor == rowData.LineVendor && orden.items.item[i].UnidadMedida == rowData.UnidadMedida) {
        //                         orden.items.item[i].Quantity = orden.items.item[i].Quantity + rowData.Quantity;
        //                         orden.items.item[i].total = orden.items.item[i].total + rowData.total;
        //                         founded = true;
        //                         break;
        //                     }
        //                 }
        //                 if (founded == false) {
        //                     orden.add(rowData);
        //                     orden.list();
        //                 } else {
        //                     orden.list();
        //                 }
        //             } else {
        //                 orden.add(rowData);
        //                 orden.list();
        //             }
        //             checked.push({ Code: rowData.Code, ItemCode: rowData.ItemCode });
        //             updateTableContabilizados(docNum, true);

        //         } else {
        //             if (orden.items.item.length > 0) {
        //                 for (var i = 0; i < orden.items.item.length; i++) {
        //                     if (orden.items.item[i].ItemCode == rowData.ItemCode && orden.items.item[i].Almacen == rowData.Almacen && orden.items.item[i].LineVendor == rowData.LineVendor && orden.items.item[i].UnidadMedida == rowData.UnidadMedida) {
        //                         orden.items.item[i].Quantity = orden.items.item[i].Quantity - rowData.Quantity;
        //                         orden.items.item[i].total = orden.items.item[i].total - rowData.total;
        //                         if (orden.items.item[i].Quantity === 0 && orden.items.item[i].total === 0) {
        //                             orden.items.item.splice(i, 1);
        //                         }
        //                         orden.list();
        //                         break;
        //                     }
        //                 }
        //             }
        //             var index = checked.findIndex(function (item) {
        //                 return item.Code === rowData.Code && item.ItemCode === rowData.ItemCode;
        //             });
        //             if (index !== -1) {
        //                 checked.splice(index, 1);
        //             }
        //             for (var k = 0; k < table.data().count(); k++) {
        //                 data = table.row(k).data();
        //                 var index = checked.findIndex(function (item) {
        //                     return item.Code === data.Code && item.ItemCode === data.ItemCode;
        //                 });
        //                 if (index !== -1) {
        //                     atLeastOne = true;
        //                 }
        //             }
        //             if (!atLeastOne) {
        //                 updateTableContabilizados(docNum, false);
        //             } else {
        //                 updateTableContabilizados(docNum, true);
        //             }
        //         }
        //     });
        // }


        //SEPARA LOS DE DIFERENTE SOLi E IGUAL SOLI PERO DESDE
        initComplete: function (settings, json) {
            // Primero, removemos cualquier event listener existente, que crea duplicidad cada que abrimos el modal
            $('#tblDetallesProd').off('change', 'input[type="checkbox"]');

            $('#tblDetallesProd').on('change', 'input[type="checkbox"]', function () {
                var $checkbox = $(this);
                var table = $('#tblDetallesProd').DataTable();
                var rowData = table.row($checkbox.closest('tr')).data();
                
                if ($checkbox.is(':checked')) {
                    // Simplemente agregar el producto como una nueva línea
                    orden.add({...rowData}); // Usamos spread operator para crear una copia nueva del objeto
                    orden.list();
                    checked.push({ 
                        Code: rowData.Code, 
                        ItemCode: rowData.ItemCode,
                        LineUniqueId: rowData.Code + '_' + new Date().getTime() // Agregamos un identificador único
                    });
                    updateTableContabilizados(docNum, true);
                } else {
                    if (orden.items.item.length > 0) {
                        // Buscar y eliminar exactamente el item que fue desmarcado
                        var indexToRemove = orden.items.item.findIndex(function(item) {
                            return item.Code === rowData.Code && 
                                   item.ItemCode === rowData.ItemCode && 
                                   item.LineVendor === rowData.LineVendor &&
                                   item.Quantity === rowData.Quantity; // Comparamos todos los campos relevantes
                        });
                        
                        if (indexToRemove !== -1) {
                            orden.items.item.splice(indexToRemove, 1);
                            orden.list();
                        }
                    }
        
                    // Eliminar el item de checked usando el Code exacto
                    var index = checked.findIndex(function (item) {
                        return item.Code === rowData.Code && 
                               item.ItemCode === rowData.ItemCode &&
                               item.LineVendor === rowData.LineVendor;
                    });
                    
                    if (index !== -1) {
                        checked.splice(index, 1);
                    }
        
                    // Verificar si quedan items seleccionados de esta solicitud
                    var atLeastOne = false;
                    for (var k = 0; k < table.data().count(); k++) {
                        var data = table.row(k).data();
                        var index = checked.findIndex(function (item) {
                            return item.Code === data.Code;
                        });
                        if (index !== -1) {
                            atLeastOne = true;
                            break;
                        }
                    }
        
                    updateTableContabilizados(docNum, atLeastOne);
                }
            });
        }
    });
}

//

function updateTableContabilizados(docNum, isChecked) {
    var tableContabilizados = $('#tblContabilizados').DataTable();
    tableContabilizados.rows().every(function () {
        var data = this.data();
        if (parseInt(data.DocEntry) === parseInt(docNum)) {
            var rowNode = this.node();
            var $checkbox = $(rowNode).find('input[type="checkbox"]');
            $checkbox.prop('checked', isChecked);
        }
    });
}



function tablaDetalleServicio(docNum) {
    $("#tblDetallesProd").hide();
    $("#tblDetallesProd_wrapper").hide();
    $("#tblDetallesServ").show();
    $('#tblDetallesServ').DataTable({
        destroy: true,
        responsive: true,
        autoWidth: false,
        "language": {
            "sProcessing": "Procesando...",
            "sLengthMenu": "",
            "sZeroRecords": "No se encontraron resultados",
            "sEmptyTable": "Ningún dato disponible en esta tabla",
            "sInfo": "",
            "sInfoEmpty": "",
            "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix": "",
            "sSearch": "Buscar:",
            "sUrl": "",
            "sInfoThousands": ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            }
        },
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'showDetails',
                'id': docNum
            },
            dataSrc: ""
        },
        columns: [
            { "data": "ItemCode" },
            { "data": "LineVendor" },
            { "data": "Description" },
            { "data": "Quantity" },
            {
                data: 'Precio',
                render: function(data, type, row) {
                    // Obtener el texto de la moneda desde el elemento HTML
                    var monedaTexto = $('#detallesMoneda').text().trim(); // Asegúrate de eliminar espacios en blanco

                    // Definir el símbolo de la moneda basado en el texto obtenido
                    var monedaSimbolo;
                    if (monedaTexto === 'SOL') {
                        monedaSimbolo = 'S/. ';
                    } else if (monedaTexto === 'USD') {
                        monedaSimbolo = '$ ';
                    } else if (monedaTexto === 'EUR') {
                        monedaSimbolo = '€ ';
                    } else {
                        monedaSimbolo = ''; // En caso de que no coincida con ninguna moneda conocida
                    }
                    return monedaSimbolo + parseFloat(data).toFixed(2);
                }
            },
            { "data": "CuentaMayor" },
            { "data": "total" },
            { "data": null }
        ],
        columnDefs: [
            {
                targets: [-2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    // Obtener el texto de la moneda desde el elemento HTML
                    var monedaTexto = $('#detallesMoneda').text().trim(); // Asegúrate de eliminar espacios en blanco

                    // Definir el símbolo de la moneda basado en el texto obtenido
                    var monedaSimbolo;
                    if (monedaTexto === 'SOL') {
                        monedaSimbolo = 'S/. ';
                    } else if (monedaTexto === 'USD') {
                        monedaSimbolo = '$ ';
                    } else if (monedaTexto === 'EUR') {
                        monedaSimbolo = '€ ';
                    } else {
                        monedaSimbolo = ''; // En caso de que no coincida con ninguna moneda conocida
                    }

                    var value = parseFloat(row.total).toFixed(2);
                    //var sol = 'S/. ';
                    return monedaSimbolo + value;
                },
            },
            {
                targets: [-1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    if (checkedSv.length > 0) {
                        for (var i = 0; i < checkedSv.length; i++) {
                            if (checkedSv[i].Code === row.Code) {
                                return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" checked></input></div>';
                            }
                        }
                        return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ></input></div>';
                    } else {
                        return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ></input></div>';
                    }
                },
            },
        ],
        initComplete: function (settings, json) {
            // Primero, removemos cualquier event listener existente, que crea duplicidad cada que abrimos el modal
            $('#tblDetallesServ').off('change', 'input[type="checkbox"]');

            $('#tblDetallesServ').on('change', 'input[type="checkbox"]', function () {
                var $checkbox = $(this);
                var table = $('#tblDetallesServ').DataTable();
                var rowData = table.row($checkbox.closest('tr')).data();
                
                if ($checkbox.is(':checked')) {
                    // Simplemente agregar el servicio como una nueva línea
                    ordenServ.add({
                        ...rowData,
                        moneda: rowData.moneda, // Mantener la moneda
                        LineUniqueId: rowData.Code + '_' + new Date().getTime() + '_' + ordenServ.items.item.length
                    });
                    ordenServ.list();
                    checkedSv.push({ 
                        Code: rowData.Code, 
                        ItemCode: rowData.ItemCode,
                        LineUniqueId: rowData.Code + '_' + new Date().getTime() + '_' + (ordenServ.items.item.length - 1)
                    });
                    updateTableContabilizados(docNum, true);
                } else {
                    if (ordenServ.items.item.length > 0) {
                        // Buscar y eliminar exactamente el servicio que fue desmarcado
                        var indexToRemove = ordenServ.items.item.findIndex(function(item) {
                            return item.Code === rowData.Code && 
                                   item.ItemCode === rowData.ItemCode && 
                                   item.LineVendor === rowData.LineVendor &&
                                   item.Quantity === rowData.Quantity;
                        });
                        
                        if (indexToRemove !== -1) {
                            ordenServ.items.item.splice(indexToRemove, 1);
                            ordenServ.list();
                        }
                    }
        
                    // Eliminar del array checkedSv
                    var index = checkedSv.findIndex(function (item) {
                        return item.Code === rowData.Code && 
                               item.ItemCode === rowData.ItemCode &&
                               item.LineVendor === rowData.LineVendor;
                    });
                    
                    if (index !== -1) {
                        checkedSv.splice(index, 1);
                    }
        
                    // Verificar si quedan servicios seleccionados de esta solicitud
                    var atLeastOne = false;
                    for (var k = 0; k < table.data().count(); k++) {
                        var data = table.row(k).data();
                        var index = checkedSv.findIndex(function (item) {
                            return item.Code === data.Code;
                        });
                        if (index !== -1) {
                            atLeastOne = true;
                            break;
                        }
                    }
        
                    if (!atLeastOne) {
                        updateTableContabilizados(docNum, false);
                    } else {
                        updateTableContabilizados(docNum, true);
                    }
                }
            });
        }
    });
}

// EVENTOS BOTONES GUARDAR LOGISTICA

$(document).ready(function () {
    // Manejo de guardar productos
    $('#btnGuardarProductos').on('click', function () {
        if (orden.items.item.length === 0) {
            $.alert({
                title: 'Aviso',
                content: 'No hay productos seleccionados. Por favor, seleccione al menos un producto.',
                type: 'red',
                theme: 'modern'
            });
            return false;
        }
        console.log("Enviando Productos:", orden.items.item); // Depuración para ver los Productos enviados

        // Validación del proveedor
        var proveedorSeleccionado = $('#SelectProveedorProductos').val();
        if (!proveedorSeleccionado) {
            $.alert({
                title: 'Aviso',
                content: 'Por favor, seleccione un proveedor.',
                type: 'red',
                theme: 'modern'
            });
            return false;
        }

        // Preparación de los datos 
        var data = {
            items: orden.items.item,
            proveedor: proveedorSeleccionado
        };

        console.log("Datos enviados para productos:", JSON.stringify(data));
        var token = $('input[name="csrfmiddlewaretoken"]').val();

        $.confirm({
            theme: 'modern',
            title: 'Confirmación',
            content: '¿Desea guardar los productos seleccionados?',
            icon: 'fas fa-check',
            type: 'green',
            buttons: {
                confirm: function () {
                    abrir_modal_cargar();
                    $.ajax({
                        headers: { "X-CSRFToken": token },
                        type: "POST",
                        url: `/erp/logistica/guardarProducto/`, 
                        contentType: "application/json",
                        data: JSON.stringify(data),
                        success: function (response) {
                            console.log("Respuesta del servidor:", response);  // Para depuración
                            if (response.message === "Producto enviado y guardado correctamente.") {
                            //if (response === "OK") {
                                $.confirm({
                                    title: 'Éxito',
                                    content: 'Los productos se han guardado correctamente.',
                                    type: 'green',
                                    theme: 'modern',
                                    buttons: {
                                        confirm: function () {
                                            $('#modalCarga').modal('hide'); 
                                            location.reload(true); 
                                        },
                                    }
                                });
                            } else {
                                $.alert({
                                    title: 'Error',
                                    icon: 'fa fa-times-circle',
                                    theme: 'modern',
                                    type: 'red',
                                    content: response.error || "Error al guardar los productos. Intente nuevamente."
                                    //content: "Error al guardar los productos. Intente nuevamente."
                                });
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            console.error("Error al guardar productos:", errorThrown);
                            console.log("Respuesta completa del servidor:", jqXHR.responseText);
                            $.alert({
                                title: 'Error',
                                content: 'Error al guardar productos: ' + textStatus,
                                type: 'red',
                                theme: 'modern'
                            });
                        }
                    });
                },
                cancel: function () {
                }
            }
        });
    });

    // Manejo de guardar servicios
    $('#btnGuardarServicios').on('click', function () {
        if (ordenServ.items.item.length === 0) {
            $.alert({
                title: 'Aviso',
                content: 'No hay servicios seleccionados. Por favor, seleccione al menos un servicio.',
                type: 'red',
                theme: 'modern'
            });
            return false;
        }

        // Validación del proveedor
        var proveedorSeleccionadoServicio = $('#SelectProveedorServicios').val();
        if (!proveedorSeleccionadoServicio) {
            $.alert({
                title: 'Aviso',
                content: 'Por favor, seleccione un proveedor.',
                type: 'red',
                theme: 'modern'
            });
            return false;
        }

        // Preparación de los datos 
        var data = {
            items: ordenServ.items.item,
            proveedorServicio: proveedorSeleccionadoServicio
        };

        console.log("Datos enviados para servicios:", JSON.stringify(data)); // Verificar los datos aquí
        var token = $('input[name="csrfmiddlewaretoken"]').val();

        $.confirm({
            theme: 'modern',
            title: 'Confirmación',
            content: '¿Desea guardar los servicios seleccionados?',
            icon: 'fas fa-check',
            type: 'green',
            buttons: {
                confirm: function () {
                    abrir_modal_cargar(); 
                    $.ajax({
                        headers: { "X-CSRFToken": token },
                        type: "POST",
                        url: `/erp/logistica/guardarServicio/`, 
                        contentType: "application/json",
                        data: JSON.stringify(data),
                        success: function (response) {
                            console.log("Respuesta del servidor:", response);  // Para depuración
                            if (response.message === "Servicio enviado y guardado correctamente.") {
                                $.confirm({
                                    title: 'Éxito',
                                    content: 'Los servicios se han guardado correctamente.',
                                    type: 'green',
                                    theme: 'modern',
                                    buttons: {
                                        confirm: function () {
                                            $('#modalCarga').modal('hide'); 
                                            location.reload(true); 
                                        },
                                    }
                                });
                            } else {
                                $.alert({
                                    title: 'Error',
                                    icon: 'fa fa-times-circle',
                                    theme: 'modern',
                                    type: 'red',
                                    content: response.error || "Error al guardar los servicios. Intente nuevamente."
                                });
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            $.alert({
                                title: 'Error',
                                content: 'Error al guardar servicios: ' + textStatus,
                                type: 'red',
                                theme: 'modern'
                            });
                        }
                    });
                },
                cancel: function () {
                }
            }
        });
    });
});


function limpiarCheckboxesContabilizados() {
    var table = $('#tblContabilizados').DataTable();
    table.rows().every(function () {
        var rowNode = this.node();
        $(rowNode).find('input[type="checkbox"]').prop('checked', false);
    });
}


// Función para obtener la tasa de impuesto desde el backend para LOGISTICA
function obtenerTaxRate(taxCode) {
    console.log('Obteniendo tasa de impuesto para:', taxCode);
    $.ajax({
        url: '/erp/obtener_impuesto_logistica/',
        type: 'GET',
        data: {
            'TaxCode': taxCode
        },
        success: function (response) {
            if (response.rate) {
                TAX_RATE = response.rate;
                console.log('Tasa de impuesto obtenida:', TAX_RATE);
                updateSubtotals('productos');
                updateSubtotals('servicios');
            } else {
                console.error('Error al obtener la tasa de impuesto:', response.error);
            }
        },
        error: function (xhr, status, error) {
            console.error('Error en la solicitud AJAX:', error);
        }
    });
}


// Función para calcular y actualizar subtotales
function updateSubtotals(type) {
    let items, subtotalElement, subtotalImpElement;
    if (type === 'productos') {
        items = orden.items.item;
        subtotalElement = $('#subtotalProd');
        subtotalImpElement = $('#subtotalImpProd');
    } else if (type === 'servicios') {
        items = ordenServ.items.item;
        subtotalElement = $('#subtotalServ');
        subtotalImpElement = $('#subtotalImpServ');
    }

    // Calcular subtotal
    let subtotal = items.reduce((sum, item) => sum + (item.Quantity * item.Precio), 0);
    let subtotalConImpuestos = subtotal * (1 + TAX_RATE);

    // Obtener la moneda desde el primer ítem (si existe)
    let monedaTexto = items.length > 0 && items[0].moneda ? items[0].moneda.trim() : '';
    let monedaSimbolo;
    if (monedaTexto === 'SOL') {
        monedaSimbolo = 'S/. ';
    } else if (monedaTexto === 'USD') {
        monedaSimbolo = '$ ';
    } else if (monedaTexto === 'EUR') {
        monedaSimbolo = '€ ';
    } else {
        monedaSimbolo = ''; // Valor por defecto si no hay moneda
    }

    // Log para verificar los cálculos y la moneda
    console.log(`Calculando subtotales para ${type}`);
    console.log(`Subtotal: ${subtotal.toFixed(2)}`);
    console.log(`Subtotal con impuestos (${TAX_RATE * 100}%): ${subtotalConImpuestos.toFixed(2)}`);
    console.log(`Moneda detectada: ${monedaTexto}, Símbolo: ${monedaSimbolo}`);

    // Actualizar elementos en el tfoot con símbolo dinam
    subtotalElement.text(`${monedaSimbolo}${subtotal.toFixed(2)}`);
    subtotalImpElement.text(`${monedaSimbolo}${subtotalConImpuestos.toFixed(2)}`);
}