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

$(document).ready(function () {
    const csrftoken = getCookie('csrftoken');

    var results = $("#results_window").kendoWindow({
        visible: false,
        width: 900,
        height: 750,
    }).data("kendoWindow");

    $("#resultsgrid").kendoGrid({
        dataSource: {
            transport: {
                read: {
                    url: "/JobConfigurations/GetCompletedJobs/",
                    dataType: "json",
                    type: "GET"
                },
            },

            schema: {
                model: {
                    id: "name",
                    fields: {
                        one: {type: "string"},
                        two: {type: "string"},
                        three: {type: "string"},
                        four: {type: "string"},
                        five: {type: "string"},
                        status: {type: "string", editable: false, defaultValue: "draft"},
                        name: {type: "string"}
                    },
                },
            },
            pageSize: 20,
            resizable: true,
            serverSorting: false,
        },
        // height: 550,
        sortable: true,
        pageable: true,
        noRecords: true,
        columns: [
            {field: "name", title: "Name", width: "250px"},
            {field: "one", title: "1", width: "150px", sortable: false},
            {field: "two", title: "2", width: "150px", sortable: false},
            {field: "three", title: "3", width: "150px", sortable: false},
            {field: "four", title: "4", width: "150px", sortable: false},
            {field: "five", title: "5", width: "150px", sortable: false},
            {
                command: [{
                    name: "Results",

                    click: function (e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        var result_id = dataItem.id;
                        console.log(result_id);
                        var info = $("#results_window").data("kendoWindow");
                        if (!info) {
                            info = $("#results_window").kendoWindow({
                                visible: false,
                                width: 900,
                                height: 750,
                            }).data("kendoWindow");
                        }
                        info.title('Results Configurations for ' + results_id);
                        console.log(results_id);
                        console.log('again');
                        info.refresh({
                            url: '/JobConfigurations/Results/' + results_id + '/'
                        })
                        info.center().open();
                        // ml_configs(dataItem.name)
                    }
                }],

                title: "Results",
                template: '<input type="button" class="k-button  k-rounded-md" name="details" value="Results" />',
                filterable: false, sortable: false, width: "160px"
            },
        ],
    });
});
