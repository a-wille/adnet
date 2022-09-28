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

function unrestricted_donation() {
    //creates and populates window so user can make an unrestricted donation
    $("#unrestricted_window").show().kendoWindow({
        content: {
            url: 'donate_unrestricted'
        },
        width: 250,
        height: 300,
    });
};

function restricted_donation(data_id) {
    //creates and populates window so user can make a restricted donation
    $("#restricted_window").show().kendoWindow({
        title: 'Event ' + event_id + ': ' + data_id,
        content: {
            url: 'donate_restricted/'+event_id
        },
        width: 450,
        height: 320,
    });
}

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');
    //sets up button for on click event to make unrestricted donation
    $('#ud').kendoButton({
        click: function(e) {
            e.preventDefault();
            unrestricted_donation();
        }
    });

    //creates and populates a grid with all events you can make a donation to
    $("#donation_grid").kendoGrid({
        dataSource: {
            transport: {
                type: "GET",
                read: {
                    url: "/Donate/GetAllEvents/",
                    dataType: "json",
                },
                pageSize: 20
            },},
            height: 400,
            groupable: false,
            sortable: true,
            pageable: {
                refresh: true,
                pageSizes: true
            },
            columns: [
                {field: 'start', title: 'Date', type: 'date', width: "12%", template: '#= kendo.toString(start,"MM/dd/yyyy") #'},
                {field: 'start', title: 'Start Time', type: 'date', width: "12%",template: '#= kendo.toString(start,"h:mm tt") #'},
                {field: 'end', title: 'End Time', type: 'date', width: "12%", template: '#= kendo.toString(end, "h:mm tt") #'},
                {field: 'name', title: 'Event', type: 'string', width: "20%"},
                {field: 'description', title: 'Description', type: 'string', width: "10%"},
                {field: 'location', title: 'Location', type: 'string', width: "12%"},
                { command: [{
                        name: "donate",
                        click: function(e) {
                            e.preventDefault();
                            var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                            event_id = dataItem.id
                            restricted_donation(dataItem.name);
                        }

                    }],
                    title: "Donate", width: "12%"
                }
            ],
    });

    //creates and populates a grid with data about a user's historical donations
    $("#my_donation_grid").kendoGrid({
        dataSource: {
            transport: {
                type: "GET",
                read: {
                    url: "/Donate/GetMyDonations/",
                    dataType: "json",
                },
                pageSize: 20
            },},
            height: 400,
            groupable: false,
            sortable: true,
            pageable: {
                refresh: true,
                pageSizes: true
            },
            columns: [
                {field: 'dark', title: 'Date', type: 'string', width: "12%"},
                {field: 'darktime', title: 'Time', type: 'string', width: "12%"},
                {field: 'type', title: 'Donation Type', type: 'string', width: "20%"},
                {field: 'event_id', title: 'Event (if applicable)', type: 'string', width: "10%"},
                {field: 'amount', title: 'Donation Amount', type: 'string', width: "12%"},
            ],
    });
});
