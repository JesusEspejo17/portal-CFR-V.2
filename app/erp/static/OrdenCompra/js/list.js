$(document).ready(function () {
    $('#tblOrdenCompra').DataTable({
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
            dataSrc: ""
        },
        columns: [
            { data: 'position' },
            { data: 'ItemDescription' },
            { data: 'DocType' },
            { data: 'SystemDate' },
            { data: 'Solicitante' },
            { data: 'NumDoc' },  // Nueva columna para NumDoc
            { data: 'Moneda' },
            { data: 'Quantity' },
            { data: 'Total' },
        ],
        order: [[0, 'desc'], [1, 'asc']], // Ordenar por la columna 'position' en orden descendente
        columnDefs: [
            {
                targets: [3, 4, 5, 6, 7], // Índice de las columnas a centrar
                class: "text-center", // Clase para centrar el texto
            },
            {
                targets: [2], // Cambia esto al índice correcto de la columna DocType
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
                    } else {
                        badgeClass = 'badge-warning'; // Para otros tipos
                        statusText = 'Otro';
                    }
                    return '<span class="badge ' + badgeClass + '">' + statusText + '</span>';
                },
            }
        ],
        // Configuración avanzada de DOM Positioning
        "dom":
            "<'row mb-2'" +
            "<'col-sm-6 d-flex align-items-center justify-content-start dt-toolbar'l>" +
            "<'col-sm-6 d-flex align-items-center justify-content-end dt-toolbar'f>" +
            ">" +
            "<'table-responsive'tr>" +
            "<'row'" +
            "<'col-sm-12 col-md-5 d-flex align-items-center justify-content-center justify-content-md-start'i>" +
            "<'col-sm-12 col-md-7 d-flex align-items-center justify-content-center justify-content-md-end'p>" +
            ">",

        // Lenguaje en español para etiquetas
        "language": {
            "lengthMenu": "Mostrar _MENU_",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            },
            "infoFiltered": "(filtrado de _MAX_ registros totales)"
        },
        initComplete: function(settings, json){
            // Puedes agregar lógica adicional aquí si es necesario
        }
    });
});