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
var optionsDataSource;
var editedItem;

    function oneGeneAutoCompleteEditor(container, options) {
        $('<input name="one" validationMessage="Enter a valid gene or SNP" data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoAutoComplete({
                dataTextField: "_id",
                filter: "contains",
                autoWidth: true,
                minLength:1,
                dataSource: optionsDataSource
            });
    }

    function twoGeneAutoCompleteEditor(container, options) {
        $('<input name="two" validationMessage="Enter a valid gene or SNP" data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoAutoComplete({
                dataTextField: "_id",
                filter: "contains",
                autoWidth: true,
                minLength:1,
                dataSource: optionsDataSource
            });
    }

    function threeGeneAutoCompleteEditor(container, options) {
        $('<input name="three" validationMessage="Enter a valid gene or SNP" data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoAutoComplete({
                dataTextField: "_id",
                filter: "contains",
                autoWidth: true,
                minLength:1,
                dataSource: optionsDataSource
            });
    }

    function fourGeneAutoCompleteEditor(container, options) {
        $('<input name="four" validationMessage="Enter a valid gene or SNP" data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoAutoComplete({
                dataTextField: "_id",
                filter: "contains",
                autoWidth: true,
                minLength:1,
                dataSource: optionsDataSource
            });
    }

    function fiveGeneAutoCompleteEditor(container, options) {
        $('<input name="five" validationMessage="Enter a valid gene or SNP" data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoAutoComplete({
                dataTextField: "_id",
                filter: "contains",
                autoWidth: true,
                minLength:1,
                dataSource: optionsDataSource
            });
    }


const csrftoken = getCookie('csrftoken');

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');
    optionsDataSource = new kendo.data.DataSource.create({
        transport: {
            read: {
                url: "/JobConfigurations/GetAllOptions/",
                dataType: "json",
                type: "GET"
            }
        }
    });

    editedItem = 'FakeValue';

    var datalist = optionsDataSource.read();

    $("#ml_window").kendoWindow({
        modal: true,
        visible: false,
        width: 900,
        height: 750,
    });

    $("#jobgrid").kendoGrid({
        dataSource: {
            transport: {
                read: {
                    url: "/JobConfigurations/GetAllJobs/",
                    dataType: "json",
                    type: "GET"
                },
                update: {
                    url: "/JobConfigurations/Edit/",
                    dataType: "jsonp",
                    // data: {og_name: editedItem},
                },
                destroy: {
                    url: "/JobConfigurations/Delete/",
                    dataType: "jsonp"
                },
                create: {
                    url: "/JobConfigurations/Create/",
                    dataType: "jsonp"
                },
                parameterMap:
                    function(options, operation) {
                        if (operation == "update") {
                            console.log(editedItem);
                            options['og_id'] = editedItem;
                        }
                        return options;
                    }
            },
            requestEnd: function(e) {
                $("#jobgrid").data("kendoGrid").refresh();
            },
            schema: {
                model: {
                    id: "name",
                    fields: {
                        one: {type:"string", validation: {
                            onevalidation: function (input) {
                                if (input.is("[name='one']") && input.val() != ""){
                                    items = optionsDataSource.data()
                                    item_ids = []
                                    for(i of items){
                                        item_ids.push(i['_id'])
                                    }
                                    if (item_ids.includes(input.val())){
                                        return true;
                                    } else {
                                        input.attr("validationMessage", "Items must be valid genes or SNPs");
                                        return false;
                                    }
                                }
                                return true;
                            }
                            }},
                        two: { type: "string" , validation: {
                            twovalidation: function (input) {
                                if (input.is("[name='two']") && input.val() != ""){
                                    items = optionsDataSource.data()
                                    item_ids = []
                                    for(i of items){
                                        item_ids.push(i['_id'])
                                    }
                                    if (item_ids.includes(input.val())){
                                        return true;
                                    } else {
                                        input.attr("validationMessage", "Items must be valid genes or SNPs");
                                        return false;
                                    }
                                }
                                return true;
                            }
                            }},
                        three: { type: "string" , validation: {
                            threevalidation: function (input) {
                                if (input.is("[name='three']") && input.val() != ""){
                                    items = optionsDataSource.data()
                                    item_ids = []
                                    for(i of items){
                                        item_ids.push(i['_id'])
                                    }
                                    if (item_ids.includes(input.val())){
                                        return true;
                                    } else {
                                        input.attr("validationMessage", "Items must be valid genes or SNPs");
                                        return false;
                                    }
                                }
                                return true;
                            }
                            }},
                        four: { type: "string" , validation: {
                            fourvalidation: function (input) {
                                if (input.is("[name='four']") && input.val() != ""){
                                    items = optionsDataSource.data()
                                    item_ids = []
                                    for(i of items){
                                        item_ids.push(i['_id'])
                                    }
                                    if (item_ids.includes(input.val())){
                                        return true;
                                    } else {
                                        input.attr("validationMessage", "Items must be valid genes or SNPs");
                                        return false;
                                    }
                                }
                                return true;
                            }
                            }},
                        five: {type: "string", validation: {
                            onevalidation: function (input) {
                                if (input.is("[name='five']") && input.val() != ""){
                                    items = optionsDataSource.data()
                                    item_ids = []
                                    for(i of items){
                                        item_ids.push(i['_id'])
                                    }
                                    if (item_ids.includes(input.val())){
                                        return true;
                                    } else {
                                        input.attr("validationMessage", "Items must be valid genes or SNPs");
                                        return false;
                                    }
                                }
                                return true;
                            }
                            }},
                        status: {type: "string", editable: false, defaultValue: "draft"},
                        name: {type: "string",
                            validation: { required: true,
                                namevalidation: function (input) {
                                    if (input.is("[name='name']") && input.val() != "") {
                                        d = $("#jobgrid").data("kendoGrid").dataSource.data();
                                        var x = 0
                                        var cur_row = input.closest("tr").index()
                                        counter = 0
                                        for (s of d) {
                                            if(input.val() == s['name'] && cur_row != counter) {
                                                x = 1
                                            }
                                            counter += 1;
                                        }
                                        if (x == 1) {
                                            input.attr("data-namevalidation-msg", "Job configuration name must be unique");
                                            return false;
                                        } else {
                                            return true;
                                        }

                                    }
                                    return true;
                                }
                            }
                        },
                        }
                    },
                },
            pageSize: 20,
            resizable: true,
            serverSorting: false,
        },
        height: 550,
        sortable: true,
        pageable: true,
        toolbar: ["create"],
        editable: {
            confirmation: true,
            mode: "inline",
            confirmDelete: "Yes"
        },
        columns: [
            {field: "name", title: "Name", width: "250px"},
            {field:"one", title:"1", width: "150px", sortable: false, editor: oneGeneAutoCompleteEditor},
            {field:"two", title: "2", width: "150px", sortable: false, editor: twoGeneAutoCompleteEditor},
            {field:"three", title:"3", width: "150px", sortable: false, editor: threeGeneAutoCompleteEditor},
            {field:"four", title:"4", width: "150px", sortable: false, editor: fourGeneAutoCompleteEditor},
            {field:"five", title: "5", width: "150px", sortable: false, editor: fiveGeneAutoCompleteEditor},
            {field: 'status', title: "Status", width: "150px", editable: false, nullable: true, defaultValue: "draft"},
            {
                command:[{
                    name: "Details",

                    click: function(e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        ml_configs(dataItem.name)
                    }
                }],

                title: "ML Configurations",
                template: '<input type="button" class="k-button  k-rounded-md" name="details" value="Details" />',
            filterable: false, sortable: false, width: "200px"
            },
            { command: "edit", width: "200px"},
            { command: "destroy", width: "150px"}
        ],
        beforeEdit: function(e) {
            editedItem = e.model.name;
        }
    });
});
