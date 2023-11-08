var optionsDataSource;
var editedItem;
var mlWindow;

function oneGeneAutoCompleteEditor(container, options) {
    $('<input name="one" validationMessage="Enter a valid SNP" data-bind="value:' + options.field + '"/>')
        .appendTo(container)
        .kendoAutoComplete({
            dataTextField: "_id",
            filter: "contains",
            autoWidth: true,
            minLength: 1,
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
            minLength: 1,
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
            minLength: 1,
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
            minLength: 1,
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
            minLength: 1,
            dataSource: optionsDataSource
        });
}

function setUpGrid() {
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
                    complete: function (e) {
                        var grid = $("#jobgrid").data("kendoGrid");
                        if (!grid) {
                            setUpGrid();
                        }
                        $("#jobgrid").data("kendoGrid").dataSource.read();
                    }
                },
                destroy: {
                    url: "/JobConfigurations/Delete/",
                    dataType: "jsonp",
                    complete: function (e) {
                        var grid = $("#jobgrid").data("kendoGrid");
                        if (!grid) {
                            setUpGrid();
                        }
                        $("#jobgrid").data("kendoGrid").dataSource.read();
                    }
                },
                create: {
                    url: "/JobConfigurations/Create/",
                    dataType: "jsonp",
                    complete: function (e) {
                        var grid = $("#jobgrid").data("kendoGrid");
                        if (!grid) {
                            setUpGrid();
                        }
                        $("#jobgrid").data("kendoGrid").dataSource.read();
                    }
                },
                parameterMap:
                    function (options, operation) {
                        if (operation == "update") {
                            console.log(editedItem);
                            options['og_id'] = editedItem;
                        }
                        return options;
                    }
            },

            schema: {
                model: {
                    id: "name",
                    fields: {
                        one: {
                            type: "string", validation: {
                                onevalidation: function (input) {
                                    if (input.is("[name='one']") && input.val() != "") {
                                        items = optionsDataSource.data()
                                        item_ids = []
                                        for (i of items) {
                                            item_ids.push(i['_id'])
                                        }
                                        if (item_ids.includes(input.val())) {
                                            return true;
                                        } else {
                                            input.attr("validationMessage", "Items must be valid genes or SNPs");
                                            return false;
                                        }
                                    }
                                    return true;
                                }
                            }
                        },
                        two: {
                            type: "string", validation: {
                                twovalidation: function (input) {
                                    if (input.is("[name='two']") && input.val() != "") {
                                        items = optionsDataSource.data()
                                        item_ids = []
                                        for (i of items) {
                                            item_ids.push(i['_id'])
                                        }
                                        if (item_ids.includes(input.val())) {
                                            return true;
                                        } else {
                                            input.attr("validationMessage", "Items must be valid genes or SNPs");
                                            return false;
                                        }
                                    }
                                    return true;
                                }
                            }
                        },
                        three: {
                            type: "string", validation: {
                                threevalidation: function (input) {
                                    if (input.is("[name='three']") && input.val() != "") {
                                        items = optionsDataSource.data()
                                        item_ids = []
                                        for (i of items) {
                                            item_ids.push(i['_id'])
                                        }
                                        if (item_ids.includes(input.val())) {
                                            return true;
                                        } else {
                                            input.attr("validationMessage", "Items must be valid genes or SNPs");
                                            return false;
                                        }
                                    }
                                    return true;
                                }
                            }
                        },
                        four: {
                            type: "string", validation: {
                                fourvalidation: function (input) {
                                    if (input.is("[name='four']") && input.val() != "") {
                                        items = optionsDataSource.data()
                                        item_ids = []
                                        for (i of items) {
                                            item_ids.push(i['_id'])
                                        }
                                        if (item_ids.includes(input.val())) {
                                            return true;
                                        } else {
                                            input.attr("validationMessage", "Items must be valid genes or SNPs");
                                            return false;
                                        }
                                    }
                                    return true;
                                }
                            }
                        },
                        five: {
                            type: "string", validation: {
                                fivevalidation: function (input) {
                                    if (input.is("[name='five']") && input.val() != "") {
                                        items = optionsDataSource.data()
                                        item_ids = []
                                        for (i of items) {
                                            item_ids.push(i['_id'])
                                        }
                                        if (item_ids.includes(input.val())) {
                                            return true;
                                        } else {
                                            input.attr("validationMessage", "Items must be valid genes or SNPs");
                                            return false;
                                        }
                                    }
                                    return true;
                                }
                            }
                        },
                        status: {type: "string", editable: false, defaultValue: "draft"},
                        name: {
                            type: "string",
                            validation: {
                                required: true,
                                namevalidation: function (input) {
                                    if (input.is("[name='name']") && input.val() != "") {
                                        var a = $("#jobgrid").data("kendoGrid");
                                        if (!a) {
                                            setUpGrid();
                                        }
                                        var d = $("#jobgrid").data("kendoGrid").dataSource.data();
                                        var x = 0
                                        var cur_row = input.closest("tr").index()
                                        counter = 0
                                        for (s of d) {
                                            if (input.val() == s['name'] && cur_row != counter) {
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
        height: 500,
        width: "100%",
        sortable: true,
        pageable: true,
        toolbar: ["create"],
        editable: {
            confirmation: true,
            mode: "inline",
            confirmDelete: "Yes"
        },
        dataBound: function (e) {
            var grid = this;
            grid.tbody.find("tr[role='row']").each(function () {
                console.log("in databound");
                var model = grid.dataItem(this);
                if (model.isNew()) {
                    // Store a flag indicating that this row is new (being added)
                    model._isNewRow = true;
                }
                //
                if (model.status != 'draft') {
                    $(this).find(".k-grid-edit").remove();
                }
            });
        },
        edit: function (e) {
            var dataItem = e.model;
            console.log('editing now');

            if (dataItem.isNew()) {
                // Store a flag indicating that this row is new (being added)
                dataItem._isNewRow = true;
            }
        },
        cancel: function (e) {
            var grid = this;
            var dataItem = e.model;

            if (dataItem.isNew() || dataItem._isNewRow) {
                // If the row is new (being added), remove the entire new row
                grid.cancelRow();
            } else {
                var d = $("#jobgrid").data("kendoGrid").dataSource;
                d.cancelChanges(dataItem);
            }

        },
        columns: [
            {field: "name", title: "Name", width: "200px"},
            {field: "one", title: "1", width: "150px", sortable: false, editor: oneGeneAutoCompleteEditor},
            {field: "two", title: "2", width: "150px", sortable: false, editor: twoGeneAutoCompleteEditor},
            {field: "three", title: "3", width: "150px", sortable: false, editor: threeGeneAutoCompleteEditor},
            {field: "four", title: "4", width: "150px", sortable: false, editor: fourGeneAutoCompleteEditor},
            {field: "five", title: "5", width: "150px", sortable: false, editor: fiveGeneAutoCompleteEditor},
            {
                field: 'status',
                title: "Status",
                width: "115px",
                editable: false,
                filterable: true,
                nullable: true,
                defaultValue: "draft"
            },
            {
                command: [{
                    name: "Settings",
                    visible: function (dataItem) {
                        return dataItem.status == 'draft'
                    },
                    width: "100px",
                    click: function (e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        var job_id = dataItem.id;
                        console.log("jobid");
                        console.log(job_id);
                        mlWindow = $("#ml_window").data("kendoWindow");
                        if (!mlWindow) {
                            mlWindow = $("#ml_window").kendoWindow({
                                modal: false,
                                visible: false,
                                width: 700,
                                height: 750,
                            }).data("kendoWindow");
                        }
                        mlWindow.title('ML Configurations for ' + job_id);
                        mlWindow.refresh({
                            url: '/JobConfigurations/GetMLConfigurations/' + job_id + '/'
                        })
                        mlWindow.center().open();
                    }
                }],
                title: "ML Configurations",
                template: '<input type="button" class="k-button info" name="info" value="Settings" />',

                filterable: false, sortable: false, width: "160px"
            },
            {
                command: [{
                    name: "Submit",
                    visible: function (dataItem) {
                        return dataItem.status == 'draft'
                    },
                    click: function (e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        if (confirm("Are you sure you are ready to submit this job?")) {
                            console.log(dataItem);
                            $.ajax({
                                type: "POST",
                                url: "/submit_job/",
                                data: {'obj': JSON.stringify(dataItem)},
                                headers: {'X-CSRFToken': csrftoken},
                                contentType: "application/x-www-form-urlencoded",
                                success: function (response) {
                                    var grid = $("#jobgrid").data("kendoGrid");
                                    if (!grid) {
                                        setUpGrid();
                                    }
                                    $("#jobgrid").data("kendoGrid").dataSource.read();
                                }
                            });
                        }
                    }
                }],
                template: '<input type="button" class="k-button  k-rounded-md" name="details" value="Submit" />',
                filterable: false, sortable: false, width: "120px",
            },
            {command: "edit", width: "115px"},
            {command: "destroy", width: "150px"}
        ],
        beforeEdit: function (e) {
            editedItem = e.model.name;
        }
    });
}


$(document).ready(function () {
    setUpGrid();

    optionsDataSource = new kendo.data.DataSource.create({
        transport: {
            read: {
                url: "/SNPSearch/GetAllSNPNames/",
                dataType: "json",
                type: "GET"
            }
        }
    });

    var datalist = optionsDataSource.read();

    mlwindow = $("#ml_window").kendoWindow({
        modal: false,
        visible: false,
        width: 700,
        height: 750,
    }).data("kendoWindow");


});

function closeMLWindow(){
    console.log(mlWindow);
    mlWindow.close();
}

