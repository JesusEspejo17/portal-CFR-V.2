//nuevo filtrado para bootstrap, con documentacion: https://preview.keenthemes.com/html/metronic/docs/general/datatables/advanced
$(function(){
    var userIdToDelete;
    var userNameToDelete;

    $('#tblUsers').DataTable({
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
            {"data": null},
            {"data": null},
            {"data": null},
            {"data": "SAP_Code"},
            {"data": "username"},
            {"data": "last_login"},
            {"data": "first_name"},
            {"data": "last_name"},
            {"data": "email"},
            {"data": "UserType"}
        ],
        columnDefs: [
            {
                targets: [0],
                class: "text-center",
                orderable: false,
                render: function(data, type, row, meta){
                    return meta.row +1;
                },
            },
            {
                targets: [1],
                class: "text-center",
                orderable: false,
                render: function(data, type, row){
                    return '<a href="/users/edit/'+row.id +'/"" type="button" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-pen"></i></a>';
                },
            },
            {
                targets: [2],
                class: "text-center",
                orderable: false,
                render: function(data, type, row){
                    return '<button type="button" class="btn btn-danger btn-xs btn-flat btn-delete" data-id="'+row.id+'" data-username="'+row.username+'"><i class="fas fa-trash-alt"></i></button>';
                },
            }
        ],
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
        }
    });

    $('#tblUsers tbody').on('click', 'button.btn-delete', function(){
        userIdToDelete = $(this).data('id');
        userNameToDelete = $(this).data('username');
        $('#deleteMessage').text('¿Eliminar registro de ' + userNameToDelete + '?');
        $('#deleteModal').modal('show');
    });

    $('#confirmDelete').on('click', function(){
        $.ajax({
            url: '/users/delete/' + userIdToDelete + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response){
                $('#deleteModal').modal('hide');
                $('#tblUsers').DataTable().ajax.reload();
            },
            error: function(error){
                console.log(error);
            }
        });
    });
});