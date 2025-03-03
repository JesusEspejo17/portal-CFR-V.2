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
            var table = $('#tblSolicitudes').DataTable();

            updateButtonStates();

            setupCheckboxChangeListener();
        },
        error: function (xhr, status, error) {
            console.error('Error al obtener los grupos del usuario:', error);
        }
    });
});

function disableAndMakeTransparentMasivo() {
    if (userGroups.includes('Jefe_de_Presupuestos')) {
        document.getElementById("btnContabilizarMasivo").disabled = false;
        document.getElementById("btnRechazarMasivo").disabled = false;
    } else {
        document.getElementById("btnAprobarMasivo").disabled = true;
        document.getElementById("btnRechazarMasivo").disabled = true;
    }
}


function updateButtonStates() {
    var table = $('#tblSolicitudes').DataTable();
    var selectedIds = [];
    table.rows().nodes().to$().find('input[type="checkbox"]').each(function () {
        if ($(this).prop('checked')) {
            selectedIds.push($(this).val());
        }
    });

    if (selectedIds.length === 0) {
        disableAndMakeTransparentMasivo();
    } else {
        if (userGroups.includes('Jefe_de_Presupuestos')) {
            document.getElementById("btnContabilizarMasivo").disabled = false;
            document.getElementById("btnRechazarMasivo").disabled = false;
        } else {
            document.getElementById("btnAprobarMasivo").disabled = false;
            document.getElementById("btnRechazarMasivo").disabled = false;
        }
    }
}

function setupCheckboxChangeListener() {
    $('#tblSolicitudes').on('change', 'input[type="checkbox"]', function () {
        updateButtonStates();
        var $checkbox = $(this);
        var docEntry = $(this).val();
        var table = $('#tblSolicitudes').DataTable();
        var rowDataC = table.row($checkbox.closest('tr')).data();

        if ($(this).is(':checked')) {
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
                        if (response[j].LineStatus !== 'R') { // Filtrar ítems con LineStatus diferente de "R"
                            if (rowDataC.DocType === 'S') {
                                // Para servicios
                                if (!checkedServ.some(item => item.Code === response[j].Code)) {
                                    checkedServ.push({
                                        Code: response[j].Code,
                                        ItemCode: response[j].ItemCode
                                    });
                                }
                                // También agregar a checkedProd para mantener consistencia con el backend
                                if (!checkedProd.some(item => item.Code === response[j].Code)) {
                                    checkedProd.push({
                                        Code: response[j].Code,
                                        ItemCode: response[j].ItemCode
                                    });
                                }
                            } else {
                                // Para productos
                                if (!checkedProd.some(item => item.Code === response[j].Code)) {
                                    checkedProd.push({
                                        Code: response[j].Code,
                                        ItemCode: response[j].ItemCode
                                    });
                                }
                            }
                        }
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error en la solicitud:', status, error);
                }
            });
        } else {
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
                        if (response[j].LineStatus !== 'R') { // Filtrar ítems con LineStatus diferente de "R"
                            // Remover de checkedProd
                            var indexProd = checkedProd.findIndex(function (item) {
                                return item.Code === response[j].Code && item.ItemCode === response[j].ItemCode;
                            });
                            if (indexProd !== -1) {
                                checkedProd.splice(indexProd, 1);
                            }

                            // Si es servicio, también remover de checkedServ
                            if (rowDataC.DocType === 'S') {
                                var indexServ = checkedServ.findIndex(function (item) {
                                    return item.Code === response[j].Code && item.ItemCode === response[j].ItemCode;
                                });
                                if (indexServ !== -1) {
                                    checkedServ.splice(indexServ, 1);
                                }
                            }
                        }
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error en la solicitud:', status, error);
                }
            });
        }
    });
}


$(function initializeDataTable() {
    tblSol = $('#tblSolicitudes').DataTable({
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
                d.estado = $('#filtrarEstado').val();
                d.action = 'searchSolicitudes';
            },
            dataSrc: ""
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
            { "data": null },
        ],
        columnDefs: [
            // {
            //     targets: [-2],
            //     class: "text-center",
            //     orderable: false,
            //     render: function (data, type, row, meta) {
            //         var hasGroupAccess = userGroups.some(group => ['Jefe_de_Presupuestos', 'Jefe_De_Area', 'Administrador', 'Validador'].includes(group));
            //         var isHeadofBudget = userGroups.includes('Jefe_de_Presupuestos');
            //         if (hasGroupAccess) {
            //             if (isHeadofBudget) {
            //                 return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox"  value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" ></input></div>';
            //             } else {
            //                 if (row.seleccionable == 1) {
            //                     return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox"  value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" ></input></div>';
            //                 } else {
            //                     return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox" value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" disabled></input></div>';
            //                 }
            //             }
            //         } else {
            //             return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox" value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" disabled></input></div>';
            //         }
            //     },
            // },
            {
                targets: [-2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row, meta) {
                    var hasGroupAccess = userGroups.some(group => ['Jefe_de_Presupuestos', 'Jefe_De_Area', 'Administrador', 'Validador'].includes(group));
                    var isHeadofBudget = userGroups.includes('Jefe_de_Presupuestos');
                    if (hasGroupAccess) {
                        if (isHeadofBudget) {
                            return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox"  value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" ></input></div>';
                        } else {
                            if (row.seleccionable == 1) {
                                return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox"  value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" ></input></div>';
                            } else {
                                return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox" value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" disabled></input></div>';
                            }
                        }
                    } else {
                        return '<div class="form-check"> <input class="form-check-input" style="width: 20px;height: 40px;" type="checkbox" value="' + row.DocEntry + '" id="' + row.DocEntry + '" id="defaultCheck1" style="width: 20px; height: 50px;" disabled></input></div>';
                    }
                },
            },
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
            // {
            //     targets: [2],
            //     class: "text-center",
            //     orderable: true,
            // },
            {
                targets: [2],
                class: "text-center",
                orderable: true,
                render: function (data, type, row) {
                    if (type === 'display' || type === 'filter') {
                        if (row.DocStatus === 'R') {
                            if (row.DocNumSAP) {
                                return `<span class="">${row.DocNumSAP}</span>`; // Mostrar DocNumSAP si existe
                            } else {
                                return '<span class="badge badge-warning" style="background-color: #f8285a;">No Aprobado</span>'; // Badge rojo
                            }
                        }
                        if (!data) {
                            return '<span class="badge badge-warning" style="background-color: #f6c000;">Aun no Aprobado</span>'; // Badge amarillo
                        }
                        return data; // Si data es válido, devolverlo
                    }
                    return data;
                }
            },
            // {
            //     targets: [9],
            //     class: "text-center",
            //     orderable: false,
            //     render: function (data, type, row) {
            //         var value = row.TotalImp;
            //         var sol = 'S/. ';
            //         return sol + value;
            //     },
            // },
            {
                targets: [9],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    if (row.DocStatus === 'P' || row.DocStatus === 'R') {
                        return 'S/. ' + data;
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
                                //console.log('Response from getLineDetails:', response); // Verificar la respuesta del backend
                                for (var i = 0; i < response.length; i++) {
                                    //console.log('Processing line item:', response[i]); // Verificar cada línea procesada
                                    totalImp += response[i].totalimpdet;
                                }
                            },
                            error: function (xhr, status, error) {
                                console.error('Error al obtener los detalles de las líneas:', error);
                            }
                        });
                        //console.log('Total Impuesto Calculado:', totalImp); // Verificar el total calculado
                        return 'S/. ' + totalImp.toFixed(2);
                    }
                    return 'S/. 0.00';
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
                targets: [-8],
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
                targets: [-4],
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
                $('#tblSolicitudes').on('change', 'input[type="checkbox"]', function () {
                    var $checkbox = $(this);
                    var docEntry = $(this).val();
                    var table = $('#tblSolicitudes').DataTable();
                    var rowDataC = table.row($checkbox.closest('tr')).data();
                    updateCheckBoxDetails();

                    updateButtonStates();
                });
            }
        },
        drawCallback: function (settings) {
            var hasGroupAccess = userGroups.includes('Jefe_de_Presupuesto', 'Jefe_De_Area', 'Administrador', 'Validador');
            if (hasGroupAccess) {
                $('#tblSolicitudes').find('input[type="checkbox"]').each(function () {
                    var docEntry = $(this).val();
                    if (selectedCheckboxes[docEntry]) {
                        $(this).prop('checked', true);
                    } else {
                        $(this).prop('checked', false);
                    }
                });
                updateButtonStates();
            }
        }
    });

    $("#filtrarEstado").change(function () {
        //Recargar la página
        tblSol.ajax.reload();
    });
});



function mostrarDetalles(docNum) {
    var data = $('#tblSolicitudes').DataTable().row(function (index, data) {
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


function disableAndMakeTransparent() {
    document.getElementById("btnAprobar").disabled = true;
    document.getElementById("btnRechazar").disabled = true;
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
            { "data": "LineStatus" },
        ],
        columnDefs: [
            {
                targets: [-2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    var value = row.total;
                    var sol = 'S/. ';
                    return sol + value;
                },
            },
            {
                targets: [5,6],
                class: "text-center",
            },
            // {
            //     targets: [-1],
            //     class: "text-center",
            //     orderable: false,
            //     render: function (data, type, row) {
            //         var checked = '';
            //         if (row.LineStatus === 'P') {
            //             checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
            //         } else {
            //             return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" disabled></input></div>';
            //         }
            //         return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ' + checked + '></input></div>';
            //     }
            // }




            // {
            //     targets: [-1],
            //     class: "text-center",
            //     orderable: false,
            //     render: function (data, type, row) {
            //         var checked = '';
            //         var isHeadofBudget = userGroups.includes('Jefe_de_Presupuestos');

            //         // Si es Jefe de Presupuestos, siempre puede marcar los checkboxes
            //         if (isHeadofBudget) {
            //             checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
            //             //return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ' + checked + '></input></div>';
            //             return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
            //         }

            //         // Para otros roles, mantener la lógica existente
            //         if (row.LineStatus === 'P') {
            //             checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
            //         } else {
            //             //return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" disabled></input></div>';
            //             return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
            //         }
            //         //return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ' + checked + '></input></div>';
            //         return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
            //     }
            // },
            {
                targets: [-1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    var checked = '';
                    var isHeadofBudget = userGroups.includes('Jefe_de_Presupuestos');
                    var isHeadOfArea = userGroups.includes('Jefe_De_Area');
            
                    // Verificar si el LineStatus es "A" o "C"
                    var hasLineStatusAorC = row.LineStatus === 'A' || row.LineStatus === 'C' || row.LineStatus === 'L';
            
                    // Si es Jefe de Presupuestos, siempre puede marcar los checkboxes
                    if (isHeadofBudget) {
                        checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
                        return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
                    }
            
                    // Si es Jefe de Área y el LineStatus es "A" o "C", deshabilitar checkboxes
                    if (isHeadOfArea && hasLineStatusAorC) {
                        return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" disabled></div>`;
                    }
            
                    // Para otros roles, mantener la lógica existente
                    if (row.LineStatus === 'P') {
                        checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
                    } else {
                        return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
                    }
            
                    return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
                }
            }
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
                updateButtonStates();
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
            { "data": "LineStatus" },
        ],
        columnDefs: [
            {
                targets: [-2],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    var value = parseFloat(row.total).toFixed(2);

                    var sol = 'S/. ';
                    return sol + value;
                },
            },
            // {
            //     targets: [-1],
            //     class: "text-center",
            //     orderable: false,
            //     render: function (data, type, row) {
            //         var checked = '';
            //         if (row.LineStatus === 'P') {
            //             checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
            //         } else {
            //             return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" disabled></input></div>';
            //         }
            //         return '<div class="form-check"> <input class="form-check-input" type="checkbox" value="' + row.Code + '" id="' + row.Code + '" ' + checked + '></input></div>';
            //     }
            // }





            // {
            //     targets: [-1],
            //     class: "text-center",
            //     orderable: false,
            //     render: function (data, type, row) {
            //         var checked = '';
            //         var isHeadofBudget = userGroups.includes('Jefe_de_Presupuestos');

            //         //AGREGUE NAME Y VALUE A LOS TRES CHECKBOX, FALTA SERVICIO

            //         // Si es Jefe de Presupuestos, siempre puede marcar los checkboxes
            //         if (isHeadofBudget) {
            //             checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
            //             return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
            //         }

            //         // Para otros roles, mantener la lógica existente
            //         if (row.LineStatus === 'P') {
            //             checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
            //         } else {
            //             return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
            //         }
            //         return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
            //     }
            // }
            {
                targets: [-1],
                class: "text-center",
                orderable: false,
                render: function (data, type, row) {
                    var checked = '';
                    var isHeadofBudget = userGroups.includes('Jefe_de_Presupuestos');
                    var isHeadOfArea = userGroups.includes('Jefe_De_Area');
            
                    // Verificar si el LineStatus es "A" o "C"
                    var hasLineStatusAorC = row.LineStatus === 'A' || row.LineStatus === 'C' || row.LineStatus === 'L';
            
                    // Si es Jefe de Presupuestos, siempre puede marcar los checkboxes
                    if (isHeadofBudget) {
                        checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
                        return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
                    }
            
                    // Si es Jefe de Área y el LineStatus es "A" o "C", deshabilitar checkboxes
                    if (isHeadOfArea && hasLineStatusAorC) {
                        return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" disabled></div>`;
                    }
            
                    // Para otros roles, mantener la lógica existente
                    if (row.LineStatus === 'P') {
                        checked = checkedProd.some(item => item.Code === row.Code) ? 'checked' : '';
                    } else {
                        return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
                    }
            
                    return `<div class="form-check"> <input class="form-check-input" type="checkbox" name="chk-detalle" value="${row.Code}" id="chk-${row.Code}" ${checked}></div>`;
                }
            }
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
                updateButtonStates();
                console.log(checkedProd);
            });
        }
    });
}

function updateTableSolicitudes(docNum, isChecked) {
    var tableSolicitudes = $('#tblSolicitudes').DataTable();
    tableSolicitudes.rows().every(function () {
        var data = this.data();
        if (parseInt(data.DocEntry) === parseInt(docNum)) {
            var rowNode = this.node();
            var $checkbox = $(rowNode).find('input[type="checkbox"]');
            $checkbox.prop('checked', isChecked);
        }
    });
}
