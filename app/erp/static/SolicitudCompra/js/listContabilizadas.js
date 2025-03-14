var tblSol;
var userGroups = [];
var selectedCheckboxes = {};
var checkedProd = [];
var checkedServ = [];

$(document).ready(function () {
    $.ajax({
        url: '/erp/getUserGroups/',
        type: 'GET',
        success: function (data) {
            userGroups = data;
            var table = $('#tblSolicitudesContab').DataTable();

        },
        error: function (xhr, status, error) {
            console.error('Error al obtener los grupos del usuario:', error);
        }
    });
});


$(function initializeDataTable() {
    console.log('Valor inicial de #detallesMoneda:', $('#detallesMoneda').text().trim());
    tblSol = $('#tblSolicitudesContab').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        order: [[0, 'desc']],
        "language": {
            "sProcessing": "Procesando...",
            "sLengthMenu": "Mostrar _MENU_ registros",
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
            },
            "lengthMenu": ""
        },
        "dom":
            "<'row mb-2'" +
            "<'col-sm-6 d-flex align-items-center justify-conten-start dt-toolbar'l>" +
            "<'col-sm-6 search d-flex align-items-center justify-content-end dt-toolbar'f>" +
            ">" +

            "<'table-responsive'tr>" +

            "<'row'" +
            "<'col-sm-12 col-md-5 d-flex align-items-center justify-content-center justify-content-md-start'i>" +
            "<'col-sm-12 col-md-7 d-flex align-items-center justify-content-center justify-content-md-end'p>" +
            ">",
        ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: function (d) {
                    d.action = 'searchSolicitudes';
                },
                dataSrc: function (json) {
                    console.log('Datos recibidos:', json); // Debug: Ver los datos recibidos
                    return json;
                }
        },
        columns: [
            { "data": null },
            { "data": null },
            { "data": "DocNumSAP" },
            { "data": "ReqIdUser" },
            { "data": "DocType" },
            { "data": "moneda" },
            { "data": "DocDate" },
            { "data": "DocDueDate" },
            { "data": "DocStatus" },
            { "data": "TotalImp" },
            { "data": null },
        ],
        columnDefs: [
            {
                targets: [1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row, meta) {
                    return row.DocNum + ' - ' + '<span class="badge badge-success">' + row.Serie + '</span>';
                },
            },
            {
                targets: [0],
                class: "text-center",
                orderable: false,
                render: function (data, type, row, meta) {
                    return meta.row + 1;
                },
            },
            {
                targets: [2],
                class: "text-center",
                orderable: true,
                render: function (data, type, row) {
                    if (type === 'display' || type === 'filter') {
                        if (row.DocStatus === 'R') {
                            return '<span class="badge badge-warning" style="background-color: #f8285a;">No Aprobado</span>'; // Badge rojo
                        }
                        if (!data) {
                            return '<span class="badge badge-warning" style="background-color: #f6c000 ;">Aun no Aprobado</span>'; // Badge rojo
                        }
                        return data; // Si data es válido, devolverlo
                    }
                    return data; // Para otros tipos, devolver el dato sin cambios
                }
            },
            {
                targets: [9],
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
                targets: [3, 5, 6, 7],
                class: "text-center",
                orderable: false,
            },
            {
                targets: [6],
                class: "text-center",
                orderable: true,
            },
            {
                targets: [-1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    return '<button rel="remove" type="button" class="btn btn-primary btn-xs btn-flat" onclick="mostrarDetalles(' + parseInt(row.DocEntry) + ')"><i class="fas fa-info-circle"></i> Detalles</button>';
                },
            },
            {
                targets: [-7],
                class: "text-center",
                orderable: true,
                render: function (data, type, row) {
                    var type = row.DocType;
                    var badgeClass = '';
                    var statusText = '';
        
                    if (type === 'I') {
                        badgeClass = 'badge-dark';
                        statusText = 'Artículo';
                    } else if (type === 'S') {
                        badgeClass = 'badge-primary';
                        statusText = 'Servicio';
                    }
                    return '<span class="badge ' + badgeClass + '">' + statusText + '</span>';
                },
            },
            {
                targets: [-3],
                class: "text-center",
                orderable: true,
                render: function (data, type, row) {
                    var status = row.DocStatus;
                    var badgeClass = '';
                    var statusText = '';
        
                    if (status === 'P') {
                        badgeClass = 'badge-warning';
                        statusText = 'Pendiente';
                    } else if (status === 'A') {
                        badgeClass = 'badge-success';
                        statusText = 'Aprobado<br>por Jefatura';
                    } else if (status === 'R') {
                        badgeClass = 'badge-danger';
                        statusText = 'Rechazado<br>por Jefatura';
                    } else if (status == 'C') {
                        badgeClass = 'badge-success';
                        statusText = 'Contabilizado';
                    } else if (status == 'CP') {
                        badgeClass = 'badge-success';
                        statusText = 'Contabilizado Parcial';
                    }
        
                    return '<span class="badge ' + badgeClass + '">' + statusText + '</span>';
                },
            },
        ],
        initComplete: function (settings, json) {
            var hasGroupAccess = userGroups.includes('Jefe_de_Presupuesto', 'Jefe_De_Area', 'Administrador', 'Validador');
            if (hasGroupAccess) {
                $('#tblSolicitudesContab').on('change', 'input[type="checkbox"]', function () {
                    var $checkbox = $(this);
                    var docEntry = $(this).val();
                    var table = $('#tblSolicitudesContab').DataTable();
                    var rowDataC = table.row($checkbox.closest('tr')).data();
                    updateCheckBoxDetails();

                    
                });
            }
        },
        drawCallback: function (settings) {
            var hasGroupAccess = userGroups.includes('Jefe_de_Presupuesto', 'Jefe_De_Area', 'Administrador', 'Validador');
            if (hasGroupAccess) {
                $('#tblSolicitudesContab').find('input[type="checkbox"]').each(function () {
                    var docEntry = $(this).val();
                    if (selectedCheckboxes[docEntry]) {
                        $(this).prop('checked', true);
                    } else {
                        $(this).prop('checked', false);
                    }
                });
                
            }
        }
    });


});



function mostrarDetalles(docNum) {
    var data = $('#tblSolicitudesContab').DataTable().row(function (index, data) {
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
    $('#modalDetalles').modal('show');
}




function tablaDetalleServicio(docNum) {
    $("#tblDetallesProd").hide();
    $("#tblDetallesProd_wrapper").hide();
    $("#tblDetallesServ").show();
    // $('#tblDetallesServ').DataTable({
    var table = $('#tblDetallesServ').DataTable({
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
            {
                "data": "LineVendor",
                "render": function(data, type, row) {
                    if (!data || data.toLowerCase() === "none") {
                        return '<span class="badge badge-dark">No Asignado</span>';
                    }
                    return data;
                }
            },
            { "data": "Description" },
            { "data": "Quantity" },
            { "data": "Precio" },
            { "data": "CuentaMayor" },
            { "data": "total" },
            {
                data: 'LineStatus',
                class: "text-center",
                render: function(data, type, row) {
                    // Cambiar el valor de LineStatus a un badge con color
                    let badgeClass = '';
                    let badgeText = '';
            
                    if (data === 'C') {
                        badgeClass = 'badge badge-info'; // Clase para "Cerrado"
                        badgeText = 'Cerrado';
                    } else if (data === 'R') {
                        badgeClass = 'badge badge-danger'; // Clase para "Rechazado"
                        badgeText = 'Rechazado';
                    } else if (data === 'A' || data === 'L') {
                        badgeClass = 'badge badge-warning'; // Clase para "Pendiente"
                        badgeText = 'Pendiente';
                    } else {
                        badgeClass = 'badge badge-secondary'; // Clase para otros estados
                        badgeText = data; // Retornar el valor original si no es 'C', 'R', 'A' ni 'L'
                    }
            
                    return `<span class="${badgeClass}" style="padding: 5px; border-radius: 5px;">${badgeText}</span>`;
                }
            }
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
                targets: [4,5,6],
                class: "text-center",
            },
            
        ],
        createdRow: function (row, data, dataIndex) {
            if (data.LineStatus != 'P') {
                if(data.LineStatus == 'R'){
                    $(row).addClass('disabled-row');
                }

            }
        },
        initComplete: function (settings, json) {
            $('#tblDetallesServ').off('change', 'input[type="checkbox"]').on('change', 'input[type="checkbox"]', function () {
                var $checkbox = $(this);
                var rowDataC = table.row($checkbox.closest('tr')).data();
                var atLeastOne = false;

                if ($checkbox.is(':checked')) {
                    if (!checkedServ.some(item => item.Code === rowDataC.Code)) {
                        checkedServ.push({ Code: rowDataC.Code, ItemCode: rowDataC.ItemCode });
                        // También agregar a checkedProd
                        checkedProd.push({ Code: rowDataC.Code, ItemCode: rowDataC.ItemCode });
                    }
                    updateTableSolicitudes(docNum, true);
                } else {
                    // Remover de ambos arrays
                    var indexServ = checkedServ.findIndex(item =>
                        item.Code === rowDataC.Code && item.ItemCode === rowDataC.ItemCode
                    );
                    if (indexServ !== -1) {
                        checkedServ.splice(indexServ, 1);
                    }

                    var indexProd = checkedProd.findIndex(item =>
                        item.Code === rowDataC.Code && item.ItemCode === rowDataC.ItemCode
                    );
                    if (indexProd !== -1) {
                        checkedProd.splice(indexProd, 1);
                    }

                    // Verificar si queda algún item seleccionado
                    for (var k = 0; k < table.data().count(); k++) {
                        data = table.row(k).data();
                        if (checkedServ.some(item => item.Code === data.Code)) {
                            atLeastOne = true;
                            break;
                        }
                    }

                    updateTableSolicitudes(docNum, atLeastOne);
                }
                
                console.log(checkedServ);
            });
        }
    });
}
function tablaDetalleProducto(docNum) {
    $("#tblDetallesServ").hide();
    $("#tblDetallesServ_wrapper").hide();
    $("#tblDetallesProd").show();
    var table = $('#tblDetallesProd').DataTable({
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
            {
                "data": "LineVendor",
                "render": function(data, type, row) {
                    if (!data || data.toLowerCase() === "none") {
                        return '<span class="badge badge-dark">No Asignado</span>';
                    }
                    return data;
                }
            },
            { "data": "Description" },
            { "data": "Quantity" },
            { "data": "Precio" },
            { "data": "UnidadMedida" },
            { "data": "Almacen" },
            { "data": "total" },
            {
                data: 'LineStatus',
                class: "text-center",
                render: function(data, type, row) {
                    // Cambiar el valor de LineStatus a un badge con color
                    let badgeClass = '';
                    let badgeText = '';
            
                    if (data === 'C') {
                        badgeClass = 'badge badge-info'; // Clase para "Cerrado"
                        badgeText = 'Cerrado';
                    } else if (data === 'R') {
                        badgeClass = 'badge badge-danger'; // Clase para "Rechazado"
                        badgeText = 'Rechazado';
                    } else if (data === 'A' || data === 'L') {
                        badgeClass = 'badge badge-warning'; // Clase para "Pendiente"
                        badgeText = 'Pendiente';
                    } else {
                        badgeClass = 'badge badge-secondary'; // Clase para otros estados
                        badgeText = data; // Retornar el valor original si no es 'C', 'R', 'A' ni 'L'
                    }
            
                    return `<span class="${badgeClass}" style="padding: 5px; border-radius: 5px;">${badgeText}</span>`;
                }
            }
        ],
        columnDefs: [
            {
                targets: [5,6],
                class: "text-center",
            },
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
        ],
        createdRow: function (row, data, dataIndex) {
            if (data.LineStatus != 'P') {
                if(data.LineStatus == 'R'){
                    $(row).addClass('disabled-row');
                }

            }
        },
        initComplete: function (settings, json) {
            $('#tblDetallesProd').off('change', 'input[type="checkbox"]').on('change', 'input[type="checkbox"]', function () {
                var $checkbox = $(this);
                var rowDataC = table.row($checkbox.closest('tr')).data();
                var atLeastOne = false;
                if ($checkbox.is(':checked')) {
                    // Agregar si no está ya en el arreglo
                    if (!checkedProd.some(item => item.Code === rowDataC.Code)) {
                        checkedProd.push({ Code: rowDataC.Code, ItemCode: rowDataC.ItemCode });
                    }
                    updateTableSolicitudes(docNum, true);
                } else {
                    var index = checkedProd.findIndex(function (item) {
                        return item.Code === rowDataC.Code && item.ItemCode === rowDataC.ItemCode;
                    });
                    if (index !== -1) {
                        checkedProd.splice(index, 1);
                    }
                    for (var k = 0; k < table.data().count(); k++) {
                        data = table.row(k).data();
                        var index = checkedProd.findIndex(function (item) {
                            return item.Code === data.Code && item.ItemCode === data.ItemCode;
                        });
                        if (index !== -1) {
                            atLeastOne=true;
                        }
                    }
                    if (!atLeastOne) {
                        updateTableSolicitudes(docNum, false);
                    } else {
                        updateTableSolicitudes(docNum, true);
                    }
                }
                
                console.log(checkedProd);
            });
        }
    });
}


