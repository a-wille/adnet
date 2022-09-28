
function getCookie(name) {
    //returns cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                 break;
            }
        }
    }
    return cookieValue;
}

var user_id = '';

function user_summary(data_id) {
    //creates window for viewing a user report on button click
    $("#report_window").show().kendoWindow({
        title: 'User Report Summary',
        content: {
            url: 'user_summary/'+user_id
        },
        width: 750,
        height: 500,
    });
}

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');

    //populates grid with active user data
    $("#active_grid").kendoGrid({
        dataSource: {
            transport: {
                read:  {
                    type: "GET",
                    url: "/Volunteer/ViewActive/",
                    dataType: "json",
                },
            },
        },
        height: 400,
        groupable: false,
        sortable: true,
        filterable: true,
        pageable: {
            refresh: true,
            pageSizes: true
        },
        columns: [
            {field: 'user', title: 'User', type: 'string'},
            {field: 'id', title: 'Email', type: 'string'},
            {field: 'volunteer', title: 'Is Volunteer', type: 'boolean',
                editor: function(container, options) {
                    container.append($("<input type='checkbox' class='k-checkbox-item' id='volunteer' title='Volunteer Permissions' autocomplete='off' aria-labelledby='volunteer-form-label' data-bind='value:volunteer'>"));
                }
            },
            {field: 'donor', title: 'Is Donor', type: 'boolean',
                editor: function(container, options) {
                    container.append($("<input type='checkbox' class='k-checkbox-item' id='donor' title='Donor Permissions' autocomplete='off' aria-labelledby='donor-form-label' data-bind='value:donor'>"));
                }
            },
            {field: 'admin', title: 'Is Admin', type: 'boolean',
                editor: function(container, options) {
                    container.append($("<input type='checkbox' class='k-checkbox-item' id='admin' title='Admin Permissions' autocomplete='off' aria-labelledby='donor-form-label' data-bind='value:donor'>"));
                }
            },
            {
                command: [{
                    name: "deactivate",
                    click: function (e) {
                        var unid = e.currentTarget.closest("tr").cells[1].textContent;
                         $.ajax({
                            type: "POST",
                            url: "/Volunteer/Deactivate/",
                            headers: {'X-CSRFToken': csrftoken},
                            data: {'id': unid},
                            contentType: "application/x-www-form-urlencoded",
                            success: function(response) {
                                if (response == "Good"){
                                    alert("Account successfully deactivated");
                                } else{
                                    alert("You may not deactivate your own current account");
                                }
                                $('#active_grid').data('kendoGrid').dataSource.read();
                                $('#active_grid').data('kendoGrid').refresh();
                                $('#delete_grid').data('kendoGrid').dataSource.read();
                                $('#delete_grid').data('kendoGrid').refresh();
                            }
                        });
                    }
                }],
                title: "Deactivate", width: "12%"
            },
            {
                command: [{
                    name: "summary",
                    click: function (e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        user_id = dataItem.id
                        user_summary(dataItem.name);
                    }

                }],
                title: "User Summary", width: "12%"
            }
        ],
    });

    //populates inactive user grid for frontend
    $("#delete_grid").kendoGrid({
        dataSource: {
            transport: {
                read:  {
                    type: "GET",
                    url: "/Volunteer/ViewInActive/",
                    dataType: "json",
                },
            },
        },
        height: 400,
        groupable: false,
        sortable: true,
        pageable: {
            refresh: true,
            pageSizes: true
        },
        columns: [
            {field: 'user', title: 'User', type: 'string'},
            {field: 'id', title: 'Email', type: 'string'},
            {field: 'volunteer', title: 'Is Volunteer', type: 'boolean',
                editor: function(container, options) {
                    container.append($("<input type='checkbox' class='k-checkbox-item' id='volunteer' title='Volunteer Permissions' autocomplete='off' aria-labelledby='volunteer-form-label' data-bind='value:volunteer'>"));
                }
            },
            {field: 'donor', title: 'Is Donor', type: 'boolean',
                editor: function(container, options) {
                    container.append($("<input type='checkbox' class='k-checkbox-item' id='donor' title='Donor Permissions' autocomplete='off' aria-labelledby='donor-form-label' data-bind='value:donor'>"));
                }
            },
            {field: 'admin', title: 'Is Admin', type: 'boolean',
                editor: function(container, options) {
                    container.append($("<input type='checkbox' class='k-checkbox-item' id='admin' title='Admin Permissions' autocomplete='off' aria-labelledby='donor-form-label' data-bind='value:donor'>"));
                }
            },
            {
                command: [{
                    name: "activate",
                    click: function (e) {
                        var unid = e.currentTarget.closest("tr").cells[1].textContent;
                         $.ajax({
                            type: "POST",
                            url: "/Volunteer/Activate/",
                            headers: {'X-CSRFToken': csrftoken},
                            data: {'id': unid},
                            contentType: "application/x-www-form-urlencoded",
                            success: function(response) {
                                if (response == "Good"){
                                    alert("User account successfully activated!");
                                } else{
                                    alert("Error");
                                }
                                $('#active_grid').data('kendoGrid').dataSource.read();
                                $('#active_grid').data('kendoGrid').refresh();
                                $('#delete_grid').data('kendoGrid').dataSource.read();
                                $('#delete_grid').data('kendoGrid').refresh();
                            }
                        });
                    }
                }],
                title: "Activate", width: "12%"
            },
            {
                command: [{
                    name: "summary",
                    click: function (e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        user_id = dataItem.id;
                        console.log(dataItem);
                        user_summary(dataItem.user);
                    }

                }],
                title: "User Summary", width: "12%"
            }
        ],
    });
})