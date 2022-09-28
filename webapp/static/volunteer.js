
$(document).ready(function() {
    //creates and populates list of all potential events a user can volunteer for
    $("#listView").kendoListView({
        template: "<li>${data}</li>",
        dataSource: {
              transport: {
                    type: "GET",
                    read: {
                        url: "/Volunteer/GetEvents/",
                        dataType: "json",
                    }
              },
          }
      });
    $("#horizontal").kendoSplitter({
        panes: [
            { collapsible: false, size: "40%" },
            { collapsible: false, size: "60%" }
        ],
        orientation: "horizontal",
        width: "100%",
    });

    //creates and populates grid with all events a user could potentially volunteer for
    $("#grid").kendoGrid({
        dataSource: {
            transport: {
                type: "GET",
                read: {
                    url: "/Volunteer/GetAllEvents/",
                    dataType: "json",
                },
                pageSize: 20
            },},
            height: 500,
            groupable: false,
            sortable: true,
            pageable: {
                refresh: true,
                pageSizes: true
            },
            columns: [
                {field: 'start', title: 'Date', width: "117px", type: 'date', template: '#= kendo.toString(start,"MM/dd/yyyy") #'},
                {field: 'start', title: 'Start Time',  width: "84px", type: 'date',template: '#= kendo.toString(start,"h:mm tt") #'},
                {field: 'end', title: 'End Time',  width: "84px", type: 'date', template: '#= kendo.toString(end, "h:mm tt") #'},
                {field: 'name', title: 'Event', type: 'string', width: "20%"},
                {field: 'description', title: 'Description', type: 'string', width: "10%"},
                {field: 'location', title: 'Location', type: 'string', width: "12%"},
                {field: 'volunteers_needed', title: '# Volunteers Needed', width: "12%", type: 'string'},
                {field: 'volunteers', hidden: "true"},
                { command: [{
                        name: "sign up",
                        click: function(e) {
                            e.preventDefault();
                            var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                            console.log(dataItem);
                            $.ajax({
                                type: "POST",
                                url: "/Volunteer/SignUp/",
                                headers: {'X-CSRFToken': csrftoken},
                                data: {'id': dataItem.id},
                                contentType: "application/x-www-form-urlencoded",
                                success: function(response) {
                                    console.log(response)
                                    if(response == '{"success": "false"}'){
                                        alert("Sorry, you aren't signed up to volunteer for this event because you are already scheduled to volunteer another shift at conflicting times.")
                                    }
                                    else{
                                         $('#grid').data('kendoGrid').dataSource.read();
                                         $('#mygrid').data('kendoGrid').dataSource.read();
                                    }
                                }
                            });
                        }

                    }],
                    title: "Sign Up", width: "12%"
                }
            ],
    });

    //creates and populates a grid with all the events a volunteer is currently signed up for
    $("#mygrid").kendoGrid({
        dataSource: {
            transport: {
                type: "GET",
                read: {
                    url: "/Volunteer/GetEvents/",
                    dataType: "json",
                },
                pageSize: 20
            },},
            height: 500,
            groupable: false,
            sortable: true,
            pageable: {
                refresh: true,
                pageSizes: true
            },
            columns: [
                {field: 'start', title: 'Date', type: 'date', width: "117px", template: '#= kendo.toString(start,"MM/dd/yyyy") #', attributes: {"class": "table-cell text-left", style: "text-align: left"}},
                {field: 'start', title: 'Start Time', width: '84px', type: 'date', template: '#= kendo.toString(start,"h:mm tt") #', attributes: {"class": "table-cell text-left", style: "text-align: left"}},
                {field: 'end', title: 'End Time',  width: '84px', type: 'date', template: '#= kendo.toString(end, "h:mm tt") #', attributes: {"class": "table-cell text-left", style: "text-align: left"}},
                {field: 'name', title: 'Event', type: 'string', width: '17%', attributes: {"class": "table-cell text-left", style: "text-align: left"}},
                {field: 'location', title: 'Location', type: 'string', attributes: {"class": "table-cell text-left", style: "text-align: left"}},
                { command: [{
                        name: "cancel  ",
                        click: function(e) {
                            e.preventDefault();
                            var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                            console.log(dataItem);
                            $.ajax({
                                type: "POST",
                                url: "/Volunteer/Cancel/",
                                headers: {'X-CSRFToken': csrftoken},
                                data: {'id': dataItem.id},
                                contentType: "application/x-www-form-urlencoded",
                                success: function(response) {
                                    $('#grid').data('kendoGrid').dataSource.read();
                                    $('#mygrid').data('kendoGrid').dataSource.read();

                                }
                            });
                        }

                    }],
                    title: "Cancel", width: "125px", attributes: {"class": "table-cell text-left", style: "text-align: left; font-size: 10px;"}
                },

            ],
    });
});