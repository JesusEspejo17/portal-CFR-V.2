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
            { data: 'position' },
            { data: 'DocNumOC' },
            { data: 'SolicitanteOC' },
            { data: 'DocTypeOC' },
            { data: 'MonedaOC' },
            { data: 'DocDateOC' },
            { data: 'TotalOC' },
            { data: 'TotalImpuestosOC' },
            {
                data: null,
                defaultContent: '<button type="button" class="btn btn-primary btn-sm btn-ver-detalles"><i class="fas fa-eye"></i> Ver</button>'
            }
        ],
        order: [[1, 'desc'], [2, 'asc']],
        columnDefs: [
            {
                targets: [0, 1, 2, 3, 4, 5, 6, 7, 8],
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

        var originsHtml = '';
        data.origins.forEach(function(origin) {
        originsHtml += `
            <div class="d-flex align-items-center mb-8">
            <div class="flex-grow-1">
                <a class="text-gray-800 text-hover-primary fw-bold fs-6">
                SOLICITUD #${origin.BaseEntryOCD}
                </a>
                <span class="text-muted fw-semibold d-block">${origin.DescriptionOCD}</span>
            </div>
            <a href="#" class="badge badge-primary fs-8 fw-bold">Ver</a>
            </div>`;
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
                    if (data.DocStatus === 'P') {
                        $('#solicitud_DocStatus').text('Pendiente');
                    } else if (data.DocStatus === 'A') {
                        $('#solicitud_DocStatus').text('Aprobado por Jefatura');
                    } else if (data.DocStatus === 'R') {
                        $('#solicitud_DocStatus').text('Rechazado por Jefatura');
                    } else if (data.DocStatus === 'C') {
                        $('#solicitud_DocStatus').text('Contabilizado');
                    }
                    else {
                        $('#solicitud_DocStatus').text('No especificado');
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
                        $('#tblDetallesSolicitudProd').show();
                        tablaSolicitudDetalleProducto(data.DocNum);
                    } else if (data.DocType === 'S') {
                        $('#solicitud_DocType').text('Servicio');
                        $('#tblDetallesSolicitudProd').hide();
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
        $('#detalleSerie').text(data.SerieOC);
        $('#detallesDocDate').text(data.DocDateOC);
        $('#detallesDocDueDate').text(data.DocDueDateOC);
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
        $('#detallesTotal').text(data.TotalOC);
        $('#detallesTotalImp').text(data.TotalImpuestosOC);
        $('#detallesSolicitante').text(data.SolicitanteOC);
    
        // Llenar tabla de detalles con datos de PRQ1, asegúrate de tener estos datos en la respuesta del servidor
        var detallesHtml = '';
        data.detalles.forEach(function(detalle) {
            console.log(detalle);  // Esto te mostrará la estructura del objeto detalle en la consola
            detallesHtml += `
                <tr>
                    <td>${detalle.ItemCodeOCD}</td>
                    <td>${detalle.DescriptionOCD}</td>
                    <td>${detalle.QuantityOCD}</td>
                    <td>${detalle.PrecioOCD}</td>
                    <td>${detalle.TotalOCD}</td>
                    <td>${detalle.LineStatusOCD}</td>
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
            }
        },
        columns: [
            { data: 'ItemCode__ItemCode' },
            { data: 'LineVendor__CardName' },
            { data: 'Description' },
            { data: 'Quantity' },
            { data: 'Precio' },
            { data: 'UnidadMedida__Name' },
            { data: 'Almacen__WhsName' },
            { data: 'total' },
        ],
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
        ],
        initComplete: function(settings, json) {
            console.log('3. DataTable servicios inicializada:', json);
        },
        error: function (xhr, error, thrown) {
            console.error('Error en tabla servicios:', error);
        }
    });
}