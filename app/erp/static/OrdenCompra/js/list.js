$(document).ready(function () {
    var table = $('#tblOrdenCompra').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: 'data'  // Changed from empty string to 'data'
        },
        columns: [
            { data: 'DocNumOC' },
            { data: 'DocNumSAPOC' },
            { data: 'SolicitanteOC' },
            { data: 'DocTypeOC' },
            { data: 'MonedaOC' },
            // { data: 'TaxCodeOC' },
            { data: 'SystemDateOC' },
            {
                data: null,
                defaultContent: '<span class="badge badge-success">Orden de Compra</span>'
            },
            
            { data: 'TotalImpuestosOC' },
            {
                data: null,
                defaultContent: '<button type="button" class="btn btn-primary btn-sm btn-ver-detalles"><i class="fas fa-eye"></i> Ver</button>'
            },
        ],
        order: [[, '']],
        columnDefs: [
            {
                targets: [0, 1, 2, 3, 4, 5, 6, 7,8],
                class: "text-center",
            },
            {
                targets: [3],
                class: "text-center",
                orderable: true,
                render: function (data, type, row) {
                    var type = row.DocTypeOC;
                    var badgeClass = '';
                    var statusText = '';

                    if (type === 'I') {
                        badgeClass = 'badge-dark';
                        statusText = 'Artículo';
                    } else if (type === 'S') {
                        badgeClass = 'badge-primary';
                        statusText = 'Servicio';
                    } else {
                        badgeClass = 'badge-warning'; 
                        statusText = 'Otro';
                    }
                    return '<span class="badge ' + badgeClass + '">' + statusText + '</span>';
                },
            },
            {
                targets: [7], // Índices de las columnas TotalOC y TotalImpuestosOC
                render: function (data, type, row) {
                    if (type === 'display' || type === 'filter') {
                        return 'S/. ' + parseFloat(data).toFixed(2); // Anteponer 'S/. ' y formatear a dos decimales
                    }
                    return data; // Para otros tipos, devolver el dato sin cambios
                }
            }
        ],
        dom: "<'row mb-2'"
            + "<'col-sm-6 d-flex align-items-center justify-content-start dt-toolbar'l>"
            + "<'col-sm-6 d-flex align-items-center justify-content-end dt-toolbar'f>"
            + ">"
            + "<'table-responsive'tr>"
            + "<'row'"
            + "<'col-sm-12 col-md-5 d-flex align-items-center justify-content-center justify-content-md-start'i>"
            + "<'col-sm-12 col-md-7 d-flex align-items-center justify-content-center justify-content-md-end'p>"
            + ">",
        language: {
            lengthMenu: "Mostrar _MENU_",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            search: "Buscar:",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            },
            infoFiltered: "(filtrado de _MAX_ registros totales)"
        },
        initComplete: function(settings, json) {
            console.log("DataTable initialized:", json);
        }
    });

    $('#tblOrdenCompra tbody').on('click', '.btn-ver-detalles', function() {
        var tr = $(this).closest('tr');
        var data = table.row(tr).data();

        // var originsHtml = '';
        // data.origins.forEach(function(origin) {
        // originsHtml += `
        //     <div class="d-flex align-items-center mb-8">
        //     <div class="flex-grow-1">
        //         <a class="text-gray-800 text-hover-primary fw-bold fs-6">
        //         SOLICITUD #${origin.BaseEntryOCD}
        //         </a>
        //         <span class="text-muted fw-semibold d-block">${origin.DescriptionOCD}</span>
        //     </div>
        //     <a href="#" class="badge badge-primary fs-8 fw-bold">Ver</a>
        //     </div>`;
        // });
        // $('#container-origins').html(originsHtml);

        // Modifica esta parte en el evento click de '.btn-ver-detalles'
        var originsHtml = '';
        var currentDocNum = null;

        // Ordenar los origins por BaseEntryOCD para agruparlos
        data.origins.sort((a, b) => a.BaseEntryOCD - b.BaseEntryOCD);

        data.origins.forEach(function(origin) {
            if (currentDocNum !== origin.BaseEntryOCD) {
                // Encabezado de SOLICITUD con el botón Ver alineado a la derecha
                originsHtml += `
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="text-gray-800 text-hover-primary fw-bold fs-6">
                            SOLICITUD #${origin.BaseEntryOCD}
                        </div>
                        <a href="#" class="badge badge-primary fs-8 fw-bold">Ver</a>
                    </div>
                    <div class="mb-3">
                        <span class="text-muted fw-semibold d-block">${origin.DescriptionOCD}</span>
                    </div>`;
                currentDocNum = origin.BaseEntryOCD;
            } else {
                // Si es el mismo número de solicitud, solo mostrar la descripción
                originsHtml += `
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-grow-1"> <!-- Añadimos padding-left para indentar -->
                            <span class="text-muted fw-semibold d-block">${origin.DescriptionOCD}</span>
                        </div>
                    </div>`;
            }
        });
        $('#container-origins').html(originsHtml);

        $('#container-origins').on('click', '.badge-primary', function() {
            var baseEntry = $(this).closest('.d-flex')
                .find('.fw-bold')
                .text()
                .replace('SOLICITUD #', '')
                .trim();
                        
            $.ajax({
                url: '/erp/solicitud/detalle/' + encodeURIComponent(baseEntry) + '/',
                type: 'GET',
                success: function(data) {
                    if (typeof data === 'string') {
                        data = JSON.parse(data);
                    }
                    
                    // Show solicitud modal with specific IDs
                    $('#modalDetallesSolicitud').modal('show');

                    // Use solicitud-specific IDs
                    $('#solicitud_DocNum').text(data.DocNum);
                    $('#solicitud_Serie').text(data.Serie);
                    if (data.TipoDoc === 'OC') {
                        $('#solicitud_DocStatus').text('Cerrado');
                    } else {
                        if (data.DocStatus === 'P') {
                            $('#solicitud_DocStatus').text('Pendiente');
                        } else if (data.DocStatus === 'A') {
                            $('#solicitud_DocStatus').text('Aprobado por Jefatura');
                        } else if (data.DocStatus === 'R') {
                            $('#solicitud_DocStatus').text('Rechazado por Jefatura');
                        } else if (data.DocStatus === 'C') {
                            $('#solicitud_DocStatus').text('Contabilizado');
                        } else if (data.DocStatus === 'CP') {
                            $('#solicitud_DocStatus').text('Contabilizado Parcial');
                            if ($('#btnAprobar').length && $('#btnRechazar').length) {
                                disableAndMakeTransparent();
                            }
                        }
                    }
                    $('#solicitud_DocDate').text(data.DocDate);
                    $('#solicitud_DocDueDate').text(data.DocDueDate);
                    $('#solicitud_Moneda').text(data.moneda);
                    $('#solicitud_TaxCode').text(data.TaxCode);
                    
                    $('#solicitud_Total').text(data.Total);
                    $('#solicitud_TotalImp').text(data.TotalImp);
                    $('#solicitud_ReqIdUser').text(data.ReqIdUser);
                    $('#solicitud_Department').text(data.Department);

                    $('#solicitud_DocEntry').text(data.DocEntry);

                    if (data.DocType === 'I') {
                        $('#solicitud_DocType').text('Artículo');
                        $('#tblDetallesSolicitudServ').hide();
                            if ($.fn.DataTable.isDataTable('#tblDetallesSolicitudServ')) {
                                $('#tblDetallesSolicitudServ').DataTable().destroy();
                            }
                        $('#tblDetallesSolicitudProd').show();
                        tablaSolicitudDetalleProducto(data.DocNum);
                    } else if (data.DocType === 'S') {
                        $('#solicitud_DocType').text('Servicio');
                        $('#tblDetallesSolicitudProd').hide();
                            if ($.fn.DataTable.isDataTable('#tblDetallesSolicitudProd')) {
                                $('#tblDetallesSolicitudProd').DataTable().destroy();
                            }
                        $('#tblDetallesSolicitudServ').show();
                        tablaSolicitudDetalleServicio(data.DocNum);
                    } else {
                        $('#solicitud_DocType').text('No especificado');
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Error:", error);
                }
            });
        });       
        
        // Llenar modal con datos 
        $('#idOrden').text(data.DocNumOC);
        $('#detallesDocNum').text(data.DocNumOC);
        if (data.SerieOC === "OrdenCompra") {
            $('#detalleSerie').text("117");
        } else {
            $('#detalleSerie').text(data.SerieOC);
        }
        $('#detallesDocDate').text(data.DocDateOC);
        $('#detallesDocDueDate').text(data.DocDueDateOC);
        $('#detallesSystemDate').text(data.SystemDateOC);
        $('#detallesMoneda').text(data.MonedaOC);
        $('#detallesSolicitante').text(data.SolicitanteOC);
        $('#detallesProveedor').text(data.ProveedorOC);
        $('#detallesMoneda').text(data.MonedaOC);
        $('#detallesTaxCode').text(data.TaxCodeOC);
        if (data.DocTypeOC === 'I') {
            $('#detallesDocType').text('Artículo');
        } else if (data.DocTypeOC === 'S') {
            $('#detallesDocType').text('Servicio');
        } else {
            $('#detallesDocType').text('No especificado');
        }
        $('#detallesTotal').text(data.TotalOC.toFixed(2));
        $('#detallesTotalImp').text(data.TotalImpuestosOC.toFixed(2));
        $('#detallesSolicitante').text(data.SolicitanteOC);
    
        // Llenar tabla de detalles con datos de PRQ1, asegúrate de tener estos datos en la respuesta del servidor
        var detallesHtml = '';
        data.detalles.forEach(function(detalle) {
            console.log(detalle);  // Esto te mostrará la estructura del objeto detalle en la consola
            detallesHtml += `
                <tr>
                    <td>${detalle.ItemCodeOCD}</td>
                    <td>${detalle.DescriptionOCD}</td>
                    <td style="text-align: center;">${detalle.QuantityOCD}</td>
                    <td style="text-align: center;">S/. ${detalle.PrecioOCD}</td>
                    <td style="text-align: center;">S/.${detalle.TotalOCD}</td>
                    
                </tr>
            `;
        });
        $('#tblDetalles tbody').html(detallesHtml);
    
        // Mostrar modal
        $('#modalDetalles').modal('show');
    });
});


function tablaSolicitudDetalleProducto(docNum) {
    console.log('1. Iniciando carga de tabla productos, DocNum:', docNum);
    
    $('#tblDetallesSolicitudProd').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: '/erp/solicitud/detalle_producto/' + docNum + '/',
            type: 'GET',
            dataSrc: function(json) {
                console.log('2. Datos recibidos productos:', json);
                return json;
            },
            error: function(xhr, error, thrown) {
                console.error('Error al cargar datos:', error);
            }
        },
        columns: [
            { data: 'ItemCode__ItemCode' },
            { data: 'LineVendor__CardName' },
            { data: 'Description' },
            { data: 'Quantity' },
            {
                data: 'Precio',
                render: function(data, type, row) {
                    return 'S/. ' + parseFloat(data).toFixed(2); // Anteponer 'S/. ' y formatear a dos decimales
                }
            },
            { data: 'UnidadMedida__Name' },
            { data: 'Almacen__WhsName' },
            {
                data: 'total',
                render: function(data, type, row) {
                    return 'S/. ' + parseFloat(data).toFixed(2); // Anteponer 'S/. ' y formatear a dos decimales
                }
            },
            {
                data: 'Quantity_rest',
                render: function(data, type, row) {
                    // Si LineStatus es 'C' o 'R', retornar 0
                    if (row.LineStatus === 'C' || row.LineStatus === 'R') {
                        return 0;
                    }
                    return data; // De lo contrario, retornar el valor original
                }
            },
            {
                data: 'LineStatus',
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
                targets: [3, 5, 6, 7,8, 9],
                class: "text-center",
            },
        ],
        language: {
            "sEmptyTable": "No hay datos disponibles en la tabla",
            "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
            "sInfoEmpty": "",
            "sInfoFiltered": "",
            "sLengthMenu": "",
            "sLoadingRecords": "Cargando...",
            "sProcessing": "Procesando...",
            "sSearch": "Buscar:",
            "sZeroRecords": "No se encontraron resultados",
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
        initComplete: function(settings, json) {
            console.log('3. DataTable productos inicializada:', json);
        }
    });
}

function tablaSolicitudDetalleServicio(docNum) {
    console.log('1. Iniciando carga de tabla servicios, DocNum:', docNum);
    
    $('#tblDetallesSolicitudServ').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: '/erp/solicitud/detalle_servicio/' + docNum + '/',
            type: 'GET',
            dataSrc: function(json) {
                console.log('2. Datos recibidos servicios:', json);
                return json;
            },
            error: function(xhr, error, thrown) {
                console.error('Error al cargar datos:', error);
            }
        },
        columns: [
            { data: 'ItemCode__ItemCode' },
            { data: 'LineVendor__CardName' },
            { data: 'Description' },
            { data: 'Quantity' },
            { data: 'Precio' },
            { data: 'CuentaMayor__AcctName' },
            { data: 'total' },
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
                targets: [3,4,5,6,7],
                class: "text-center",
            },
        ],
        language: {
            "sEmptyTable": "No hay datos disponibles en la tabla",
            "sInfo": "",
            "sInfoEmpty": "",
            "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
            "sLengthMenu": "",
            "sLoadingRecords": "Cargando...",
            "sProcessing": "Procesando...",
            "sSearch": "Buscar:",
            "sZeroRecords": "No se encontraron resultados",
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
        initComplete: function(settings, json) {
            console.log('3. DataTable servicios inicializada:', json);
        },
        error: function (xhr, error, thrown) {
            console.error('Error en tabla servicios:', error);
        }
    });
}