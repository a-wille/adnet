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

function more_information(gene) {
    var info = $("#information_window").data("kendoWindow");
    if (info == null) {
        info = $('#information_window').kendoWindow({
            modal: true,
            visible: false,
            width: 700,
            height: 900,
        }).data("kendoWindow");
    }
    info.title('Gene: ' + gene);
    info.refresh({
        url: 'get_information/' + gene
    }).open();
    info.center();
}


const csrftoken = getCookie('csrftoken');

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');

    $("#information_window").kendoWindow({
        modal: true,
        visible: false,
        width: 900,
        height: 750,
    });

    $("#genes").kendoAutoComplete({
        dataTextField: "name",
        filter: "contains",
        autoWidth: true,
        minLength: 1,
        dataSource: {
            transport: {
                read: {
                    url: "/GeneSearch/GetAllGenes/",
                    dataType: "json",
                    type: "GET"
                }
            }
        },
        select: function (e) {
            var item = e.item;
            var text = item.text();
            console.log(text)
            $('#geneData').empty();
            more_information(text)
        },
    });
    $("#genegrid").kendoGrid({
        dataSource: {
            transport: {
                read: {
                    url: "/GeneSearch/GetAllGenes/",
                    dataType: "json",
                    type: "GET"
                }
            },
            schema: {
                model: {
                    fields: {
                        name: {type:"string"},
                        chromosome: { type: "string" },
                        type: { type: "string" },
                        description: { type: "string" }
                        }
                    }
                },
            pageSize: 20,
            resizable: true,
        },
        height: 550,
        filterable: true,
        sortable: true,
        resizable: true,
        pageable: true,
        columns: [
            {field:"name", title:"Name", width:"150px"},
            {field:"chromosome", title: "Chr", width:"100px"},
            {field:"range", title: "Chr. Range", width:"225px", template:"#=range.begin# - #=range.end#"},
            {field:"range", title: "Orientation", width: "150px", template:"#=range.orientation#"},
            {field:"type", title: "Type", width:"225px"},
            {field:"description", title:"Description"},
            {
                command:[{
                    name: "More Details ",
                    width: "150px",
                    click: function(e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        more_information(dataItem.name)
                    }
                }],
                title: "More Information ",
                template: '<input type="button" class="k-button info" name="info" value="Details" />',
            filterable: false, sortable: false, width: "150px"}
        ]
    });

});
