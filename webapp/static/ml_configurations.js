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
    var jobId = document.getElementById("job_id").textContent;
    var rowCounter = 0;
    // create ComboBox from input HTML element
    var activation_dataSource = new kendo.data.DataSource({
        data: [
            {Id: "sigmoid", name: "Sigmoid"},
            {Id: "relu", name: "ReLU (Rectified Linear Unit)"},
            {Id: "leaky_relu", name: "Leaky ReLU"},
            {Id: "tanh", name: "Hyperbolic Tangent"},
            {Id: "softmax", name: "Softmax"},
            {Id: "swish", name: "Swish"},
            {Id: "linear", name: "Linear"},
        ]
    });
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
                    $('<input class="k-input k-textbox" name="size" type="number" min="0" required data-bind="value:' + options.field + '"/>')
                        .appendTo(container);
                }
            },
            {
                field: "activation",
                title: "Activation Function",
                width: 120,
                template: function (dataItem) {
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
        // editable: true,
        edit: function (e) {
            e.preventDefault();
            rowCounter = 0;
            console.log("editing");
            if (!e.model.isNew()) {
                // Disable the editor of the "id" column when editing data items
                var numeric = e.container.find("input[name=id]").data("kendoNumericTextBox");
                numeric.enable(false);
            }
        }
    });


    $("#activation_combobox").kendoComboBox({
        dataTextField: "name",
        dataValueField: "Id",
        dataSource: activation_dataSource,
        filter: "contains",
        suggest: true,
        noDataTemplate: $("#noDataTemplate").html()
    });

    var culater = $("#activation_combobox").data("kendoComboBox");
    culater.value(response_data['final_activation']);
    culater.trigger("change");

    var optimizer_dataSource = new kendo.data.DataSource({
        data: [
            {Id: "sgd", name: "Stochastic Gradient Descent (SGD)"},
            {Id: "adam", name: "Adam"},
            {Id: "rmsprop", name: "RMSPropr"},
            {Id: "adagrad", name: "Adagrad"},
            {Id: "adadelta", name: "Adadelta"},
            {Id: "nadam", name: "Nadam"},
            {Id: "ftrl", name: "FTRL"},
            {Id: "proximaladagrad", name: "Proximal AdaGrad"}
        ]
    });

    $("#optimizer_combobox").kendoComboBox({
        dataTextField: "name",
        dataValueField: "Id",
        dataSource: optimizer_dataSource,
        filter: "contains",
        suggest: true,
        noDataTemplate: $("#noDataTemplate").html()
    });
    culater = $("#optimizer_combobox").data("kendoComboBox");
    culater.value(response_data['optimizer']);
    culater.trigger("change");

    var loss_dataSource = new kendo.data.DataSource({
        data: [
            {Id: "binary_crossentropy", name: "Binary Cross-Entropy"},
            {Id: "categorical_crossentropy", name: "Categorical Cross-Entropy"},
            {Id: "sparse_categorical_crossentropy", name: "Sparse Categorical Cross-Entropy"},
            {Id: "mean_squared_error", name: "Mean Squared Error"},
            {Id: "mean_absolute_error", name: "Mean Absolute Error"},
            {Id: "huber_loss", name: "Huber"},
            {Id: "hinge_loss", name: "Hinge"},
            {Id: "cosine_similarity", name: "Cosine Similarity"},
            {Id: "kl_divergence", name: "KL Divergence"},
        ]
    });

    $("#loss_combobox").kendoComboBox({
        dataTextField: "name",
        dataValueField: "Id",
        dataSource: loss_dataSource,
        filter: "contains",
        suggest: true,
        noDataTemplate: $("#noDataTemplate").html()
    });
    culater = $("#loss_combobox").data("kendoComboBox");
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
            }
        },
        messages: {
            range: function (input) {
                var min = parseFloat($(input).data("min"), 10);
                var max = parseFloat($(input).data("max"), 10);

                return kendo.format("Value should be between {0} and {1}!", min, max);
            }
        }
    }).data("kendoValidator");

    window.validator = validator;

    $("form").submit(function (event) {
        event.preventDefault();
        var grid = $("#layergrid").data("kendoGrid");
        grid.saveChanges();

        var status = $(".status");

        if (validator.validate()) {
            status.text(" ")
                .removeClass("invalid")
                .addClass("valid");
        } else {
            status.text("Oops! There is invalid data in the form.")
                .removeClass("valid")
                .addClass("invalid");
        }

        var final = {
            'job_id': job_id,
            'layers': layer_data,
            'final_activation': $("#activation_combobox").val(),
            'optimizer': $("#optimizer_combobox").val(),
            'loss': $("#loss_combobox").val(),
            'epochs': $("#epoch_size").val(),
            'batch_size': $("#batch_size").val()
        }

        $.ajax({
            url: "/JobConfigurations/SetMLConfigs/",
            type: "POST",
            headers: {'X-CSRFToken': csrftoken},
                            dataType: 'json',
            data: final,
            async: false,
            success: function (data) {
                alert("Changes saved successfully");
            },
            error: function (error) {
                console.log(`Error ${error}`);
            }
        });
    });
});