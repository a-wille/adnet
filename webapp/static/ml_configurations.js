$(document).ready(function () {
    var jobId = document.getElementById("job_id").textContent;
    var rowCounter = 0;
    // create ComboBox from input HTML element

    var response_data;
    $.ajax({
        url: "/JobConfigurations/GetMLForJob/" + jobId,
        type: "GET",
        async: false,
        success: function (data) {
            data = JSON.parse(data);
            layer_data = data['layers'];
            response_data = data

        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });

    var activation_dataSource = new kendo.data.DataSource({
        data: [
            {Id: "sigmoid", name: "Sigmoid"},
            {Id: "relu", name: "ReLU (Rectified Linear Unit)"},
            {Id: "leaky_relu", name: "Leaky ReLU"},
            {Id: "tanh", name: "Hyperbolic Tangent"},
        ]
    });
    activation_dataSource.read();


    $("#layergrid").kendoGrid({
        dataSource: new kendo.data.DataSource({
            data: layer_data,
            schema: {
                model: {
                    id: "number",
                    fields: {
                        size: {type: "number", defaultValue: 10},
                        activation: {type: "string", defaultValue: "relu"}
                    }
                }
            },
        }),
        editable: {
            createAt: "bottom"
        },
        toolbar: ["create", "cancel"],
        columns: [
            {
                title: "#",
                template: function (dataItem) {
                    rowCounter++;
                    console.log("rowCounter # " + rowCounter);
                    return rowCounter;
                },
                width: 50,
                editable: false // Disable editing for this column
            },
            {
                field: "size",
                title: "Number of Neurons",
                width: 120,
                editor: function (container, options) {
                    // Create an input element for editing "size"
                    $('<input class="k-input k-textbox" name="size" type="number" min="1" max="200" required data-bind="value:' + options.field + '"/>')
                        .appendTo(container);
                }
            },
            {
                field: "activation",
                title: "Activation Function",
                width: 120,
                template: function (dataItem) {
                    console.log("okay");
                    var activationItem = activation_dataSource.data().find(function (item) {
                        return item.Id === dataItem.activation;
                    });
                    return activationItem ? activationItem.name : '';
                },
                editor: function (container, options) {
                    // Create a dropdown list for editing "activation"
                    $('<input name="activation" required data-bind="value:' + options.field + '"/>')
                        .appendTo(container)
                        .kendoDropDownList({
                            dataTextField: "name",
                            dataValueField: "Id",
                            dataSource: activation_dataSource,
                        });
                }
            },

            {
                command: "destroy",
                title: "&nbsp;",
                width: 150
            }
        ],
        edit: function (e) {
            e.preventDefault();
            rowCounter = 0;

        },
        dataBound: function (e) {
            e.preventDefault();
            rowCounter = 0;
            $("#layergrid tbody tr .k-grid-delete").each(function () {
                var currentDataItem = $("#layergrid").data("kendoGrid").dataItem($(this).closest("tr"));
                if (currentDataItem.id == 1 || currentDataItem.id == 2){
                    $(this).remove();
                }
            });
        }

    });


    $("#activation_combobox").kendoDropDownList({
        dataTextField: "name",
        dataValueField: "Id",
        dataSource: activation_dataSource,
        filter: "contains",
        suggest: true,
    });

    var culater = $("#activation_combobox").data("kendoDropDownList");
    culater.value(response_data['final_activation']);
    culater.trigger("change");

    var optimizer_dataSource = new kendo.data.DataSource({
        data: [
            {Id: "sgd", name: "Stochastic Gradient Descent (SGD)"},
            {Id: "adam", name: "Adam"},
            {Id: "rmsprop", name: "RMSProp"},
            {Id: "adagrad", name: "Adagrad"},
            {Id: "adadelta", name: "Adadelta"},
            {Id: "nadam", name: "Nadam"}
        ]
    });

    $("#optimizer_combobox").kendoDropDownList({
        dataTextField: "name",
        dataValueField: "Id",
        dataSource: optimizer_dataSource,
        filter: "contains",
        suggest: true,
    });
    culater = $("#optimizer_combobox").data("kendoDropDownList");
    culater.value(response_data['optimizer']);
    culater.trigger("change");


    var loss_dataSource = new kendo.data.DataSource({
        data: [
            {Id: "binary_crossentropy", name: "Binary Cross-Entropy"},
            {Id: "categorical_crossentropy", name: "Categorical Cross-Entropy"},
            {Id: "sparse_categorical_crossentropy", name: "Sparse Categorical Cross-Entropy"},
            {Id: "hinge_loss", name: "Hinge"}
        ]
    });

    $("#loss_combobox").kendoDropDownList({
        dataTextField: "name",
        dataValueField: "Id",
        dataSource: loss_dataSource,
        filter: "contains",
        suggest: true
    });
    culater = $("#loss_combobox").data("kendoDropDownList");
    culater.value(response_data['loss']);
    culater.trigger("change");

    $("#batch_size").kendoNumericTextBox({
        value: response_data['batch_size'],
        format: "#"
    });
    $("#epoch_size").kendoNumericTextBox({
        value: response_data['epochs'],
        format: "#"
    });
    var validator = $("#batch_form").kendoValidator({
        rules: {
            range: function (input) {
                var min = parseFloat($(input).data("min"), 10);
                var max = parseFloat($(input).data("max"), 10);
                var value = parseFloat($(input).val(), 10);

                if (isNaN(min) || isNaN(max) || isNaN(value)) {
                    return true;
                }

                return min <= value && value <= max;
            },
        },
        messages: {
            range: function (input) {
                var min = parseFloat($(input).data("min"), 10);
                var max = parseFloat($(input).data("max"), 10);
                return kendo.format("Value should be between {0} and {1}!", min, max);
            },
        }
    }).data("kendoValidator");

    window.validator = validator;

    $("form").submit(function (event) {
        event.preventDefault();
        var grid = $("#layergrid").data("kendoGrid");
        grid.saveChanges();
        if (validator.validate()) {
            layers = $("#layergrid").data("kendoGrid").dataSource.data().toJSON();
            var count = 0;
            layers.forEach(function (dict) {
                // Access dictionary keys and values
                count++;
                dict['number'] = count;
            });
            console.log(layers);
            var final = {
                'job_id': jobId,
                'ml_configs': {
                    'layers': layers,
                    'final_activation': $("#activation_combobox").val(),
                    'optimizer': $("#optimizer_combobox").val(),
                    'loss': $("#loss_combobox").val(),
                    'epochs': $("#epoch_size").val(),
                    'batch_size': $("#batch_size").val()
                }

            }

            $.ajax({
                url: "/JobConfigurations/SetMLConfigs/",
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                dataType: 'json',
                data: JSON.stringify(final),
                async: false,
                success: function (data) {
                    console.log(data);
                    if ('error' in data && (data.error) == 'invalid_configuration') {
                        alert("Invalid configuration. Please try again valid form values.")
                    } else {
                        alert("Changes saved successfully");
                        closeMLWindow();
                    }
                },
                error: function (error) {
                    console.log(`Error ${error}`);
                }
            });

        } else {
            alert("There are errors in this configuration. Please correct the red-highlighted fields, then submit your changes again.");
        }
    });
});