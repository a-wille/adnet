
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

var event_id = 0;

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');

    //populates grid of all events for admin
    $("#event_grid").kendoGrid({
        dataSource: {
            transport: {
                read: function(options) {
                    $.ajax({
                        type: "GET",
                        url: "/Events/ViewAllTime/",
                        dataType: "json",
                        contentType: "application/json",
                        success: function(result) {
                            $("#event_grid").data("kendoGrid").dataSource.data(result);
                        },
                        error: function(result) {
                            console.log("WHAT");
                            console.log(result);
                        }
                    });
                },
                update: function(options) {
                    options.data['id'] = event_id;

                    $.ajax({
                        type: "POST",
                        url: "/Events/Edit/",
                        headers: {'X-CSRFToken': csrftoken},
                        dataType: "json",
                        data: options.data,
                        success: function(result) {
                            console.log("HI");
                        },
                        error: function(result) {

                            console.log(result);
                            if (result.responseText == "False") {
                                alert("Sorry, this event already took place, so details for this event cannot be edited.");
                            }
                            $.ajax({
                                type: "GET",
                                url: "/Events/ViewAllTime/",
                                dataType: "json",
                                contentType: "application/json",
                                success: function(result) {
                                    $("#event_grid").data("kendoGrid").dataSource.data(result);
                                },
                                error: function(result) {
                                    console.log("WHAT");
                                    console.log(result);
                                }
                            });
                            $('#event_grid').data('kendoGrid').refresh();

                        }
                    });
                },
                destroy: function (options) {
                },
                pageSize: 20
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
            {
                field: 'startdate',
                title: 'Date',
                type: 'date',
                width: "12%",
                template: '#= kendo.toString(startdate,"MM/dd/yyyy") #',
                editor: "DatePicker"
            },
            {
                field: 'start',
                title: 'Start Time',
                type: 'string',
                width: "12%",
            },
            {
                field: 'end',
                title: 'End Time',
                type: 'string',
                width: "12%",
            },
            {field: 'name', title: 'Event', type: 'string', width: "20%"},
            {field: 'description', title: 'Description', type: 'string', width: "10%"},
            {field: 'location', title: 'Location', type: 'string', width: "12%"},
            {field: 'id', type: 'string', editor: "NumericTextBox"},
            {command: "edit"},
            {
                command: [{
                    name: "delete",
                    click: function (e) {
                         event_id = parseInt(e.currentTarget.closest("tr").cells[6].textContent);
                         console.log(event_id);
                         $.ajax({
                            type: "POST",
                            url: "/Events/DeleteEvent/",
                            headers: {'X-CSRFToken': csrftoken},
                            data: {'id': event_id},
                            contentType: "application/x-www-form-urlencoded",
                            success: function(response) {
                                if (response == "Good"){
                                    alert("event deleted successfully!");
                                } else{
                                    alert("event couldn't be deleted because it already happened.");
                                }
                                $.ajax({
                                    type: "GET",
                                    url: "/Events/ViewAllTime/",
                                    dataType: "json",
                                    contentType: "application/json",
                                    success: function(result) {
                                        $("#event_grid").data("kendoGrid").dataSource.data(result);
                                    },
                                    error: function(result) {
                                        console.log("WHAT");
                                        console.log(result);
                                    }
                                });
                                $('#event_grid').data('kendoGrid').refresh();
                                $('#cancel_grid').data('kendoGrid').dataSource.read();
                                $('#cancel_grid').data('kendoGrid').refresh();
                            }
                        });
                    }

                }],
                title: "Cancel", width: "12%"
            }
        ],
        editable: "popup",
        edit: function(e) {
            e.preventDefault();
            event_id = e.model.id;
            var numeric = e.container.find("input[name=id]").data("kendoNumericTextBox");
            numeric.enable(false);

        },
        save: function(e) {
            var ths = this;
            ths.refresh();
        }
    });

    //populates cancelled events grid for admin
    $("#cancel_grid").kendoGrid({
        dataSource: {
            transport: {
                read:  {
                    type: "GET",
                    url: "/Events/ViewCancelled/",
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
            {
                field: 'startdate',
                title: 'Date',
                type: 'date',
                width: "12%",
                template: '#= kendo.toString(startdate,"MM/dd/yyyy") #',
                editor: "DatePicker"
            },
            {
                field: 'start',
                title: 'Start Time',
                type: 'string',
                width: "12%",
            },
            {
                field: 'end',
                title: 'End Time',
                type: 'string',
                width: "12%",
            },
            {field: 'name', title: 'Event', type: 'string', width: "20%"},
            {field: 'description', title: 'Description', type: 'string', width: "10%"},
            {field: 'location', title: 'Location', type: 'string', width: "12%"},
            {field: 'id', type: 'string', editor: "NumericTextBox"},
            {
                command: [{
                    name: "uncancel",
                    click: function (e) {
                        var unid = parseInt(e.currentTarget.closest("tr").cells[6].textContent);
                         $.ajax({
                            type: "POST",
                            url: "/Events/UncancelEvent/",
                            headers: {'X-CSRFToken': csrftoken},
                            data: {'id': unid},
                            contentType: "application/x-www-form-urlencoded",
                            success: function(response) {
                                if (response == "Good"){
                                    alert("event readded successfully!");
                                } else{
                                    alert("event couldn't be added because it already would have happened.");
                                }
                                location.reload();
                            }
                        });
                    }

                }],
                title: "Un-Cancel", width: "12%"
            }
        ],
    });
})