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

const csrftoken = getCookie('csrftoken');

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');

    //populate and display kendo scheduler with all events
    $("#scheduler").kendoScheduler({
        date: new Date(Date.now()),
        startTime: new Date(Date.now()),
        height: 400,
        views: [
            "week",
            "month",
            "year",
            { type: "agenda", selected: true, eventHeight: 100},
            { type: "timeline", eventHeight: 50}
        ],
        dataSource: {
            batch: true,
            transport: {
                read: {
                    url: "/Events/ViewAll/",
                    dataType: "json",
                    type: "GET"
                },
                update: {
                    url: "/Events/Edit/",
                    dataType: "json",
                    type: "POST"
                },
                create: {
                    url: "/Events/Create/",
                    dataType: "json",
                    type: "POST"
                    },
                destroy: {
                    url: "/Events/Delete/",
                    dataType: "json",
                    type: "POST",
                    headers: {'X-CSRFToken': csrftoken},
                },
            },
            schema: {
                model: {
                    id: "id",
                    fields: {
                        id: { from: "id", type: "number" },
                        title: { from: "name", type: "string" },
                        description: { from: "location", type: "string" },
                        start: { type: "date", from: "start" },
                        end: { type: "date", from: "end" },
                    }
                }
            },
        },
    });

    //creates a form that an admin can create events from
    $("#event-form").kendoForm({
        orientation: "vertical",
        items: [{
            type: "group",
            label: "Create An Event",
            items: [
                {field: "myname", label: "Event Name", validation: {required: true}},
                {field: "description", label: "Description:", validation: { required: true}},
                {field: "start", label: "Start", validation: {required: true},
                    editor: "DateTimePicker",
                    editorOptions: {min: new Date()}
                },
                {field: "end", label: "End", validation: {required: true},
                    editor: "DateTimePicker",
                    editorOptions: {min: new Date()},
                    validation: {
                        required: true,
                        greaterdate: function (input) {
                            if (input.is("[name='end']") && input.val() != "") {
                                var date = kendo.parseDate(input.val()),
                                    start = kendo.parseDate($("[name='start']").val());
                                input.attr("data-greaterdate-msg", "Event should end after event start");
                                return start == null || start.getTime() < date.getTime();
                            }
                            return true;
                        }
                    }
                },
                {field: "location", label: "Location", validation: {required: true}},
                {field: "num_volunteers", label: "Number of Volunteers Needed", editor: "NumericTextBox", editorOptions: {format: "#"}, validation: {required: true}},
            ]
        }],
        submit: function(e) {
            e.preventDefault();
            var $myname = $('#myname');
            var $description= $('#description');
            var $start = $('#start');
            var $end = $('#end');
            var $location = $('#location');
            var $num = $('#num_volunteers');
            var vals = {
                'myname': $myname.val(),
                'description': $description.val(),
                'start': $start.val(),
                'end': $end.val(),
                'location': $location.val(),
                'num_volunteers': $num.val()
            };
            $.ajax({
                type: "POST",
                url: "/Events/Create/",
                headers: {'X-CSRFToken': csrftoken},
                data: vals,
                contentType: "application/x-www-form-urlencoded",
                success: function(response) {
                    alert("Success!");
                    $('#scheduler').data('kendoScheduler').dataSource.read();
                    var form = $("#event-form").getKendoForm();
                    // form.clear();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
            return false;
        },
        clear: function(ev) {
        }
     });
});
