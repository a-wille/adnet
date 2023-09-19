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

function b64toBlob(b64Data, contentType) {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
        const slice = byteCharacters.slice(offset, offset + 512);
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    return new Blob(byteArrays, {type: contentType});
}

$(document).ready(function () {
    const csrftoken = getCookie('csrftoken');
    var jobId = document.getElementById("job_id").textContent;

    var result_response_data;
    $.ajax({
        url: "/JobConfigurations/GetResults/" + jobId,
        type: "GET",
        async: false,
        success: function (data) {
            console.log(data);
            const imageContainer = document.getElementById('image-container');

            data.images.forEach(imageInfo => {
                console.log(imageInfo);
                const image = document.createElement('img');
                const imageBlob = b64toBlob(imageInfo.image_data, imageInfo.content_type);
                const imageUrl = URL.createObjectURL(imageBlob);

                const title = document.createElement('h2');
                title.classList.add('k-h5');
                // Replace 'your-class-name' with your desired class name
                title.textContent = imageInfo.title; // Assuming title is an attribute in imageInfo

                // Create a caption element
                const caption = document.createElement('p');
                caption.classList.add('k-p-md');
                caption.textContent = imageInfo.caption; // Assuming caption is an attribute in imageInfo

                const br = document.createElement('br');

                image.src = imageUrl;

                imageContainer.appendChild(title);
                imageContainer.appendChild(image);
                imageContainer.appendChild(caption);
                imageContainer.appendChild(br);

            });

        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });

    var rowCounter = 0;

    $.ajax({
        url: "/JobConfigurations/GetMLForJob/" + jobId,
        type: "GET",
        async: false,
        success: function (data) {
            data = JSON.parse(data);
            layer_data = data['layers'];
            result_response_data = data

        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });

    var r_activation_names = new kendo.data.DataSource({
        data: [
            {Id: "sigmoid", name: "Sigmoid"},
            {Id: "relu", name: "ReLU (Rectified Linear Unit)"},
            {Id: "leaky_relu", name: "Leaky ReLU"},
            {Id: "tanh", name: "Hyperbolic Tangent"},
        ]
    });
    r_activation_names.read();


    $("#resultlayergrid").kendoGrid({
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
            },
            {
                field: "activation",
                title: "Activation Function",
                width: 120,
                template: function (dataItem) {
                    var activationItem = r_activation_names.data().find(function (item) {
                        return item.Id === dataItem.activation;
                    });
                    return activationItem ? activationItem.name : '';
                },
            }
        ],
        dataBound: function (e) {
            e.preventDefault();
            rowCounter = 0;
        }

    });

    var r_optimizer_names = new kendo.data.DataSource({
        data: [
            {Id: "sgd", name: "Stochastic Gradient Descent (SGD)"},
            {Id: "adam", name: "Adam"},
            {Id: "rmsprop", name: "RMSProp"},
            {Id: "adagrad", name: "Adagrad"},
            {Id: "adadelta", name: "Adadelta"},
            {Id: "nadam", name: "Nadam"}
        ]
    });
    r_optimizer_names.read();

    var r_loss_names = new kendo.data.DataSource({
        data: [
            {Id: "binary_crossentropy", name: "Binary Cross-Entropy"},
            {Id: "categorical_crossentropy", name: "Categorical Cross-Entropy"},
            {Id: "sparse_categorical_crossentropy", name: "Sparse Categorical Cross-Entropy"},
            {Id: "hinge_loss", name: "Hinge"},
        ]
    });
    r_loss_names.read();

    r_optimizer_names.data().forEach(function (item) {
    if (item.Id == result_response_data['optimizer']) {
            document.getElementById("r_optimizer").textContent = item.name;
            console.log(item.name); // Exit the loop when the item is found
        };
    });

    r_loss_names.data().forEach(function (item) {
    if (item.Id == result_response_data['loss']) {
            document.getElementById("r_loss").textContent = item.name;
            console.log(item.name); // Exit the loop when the item is found
        };
    });

    r_activation_names.data().forEach(function (item) {
    if (item.Id == result_response_data['final_activation']) {
            document.getElementById("r_activation").textContent = item.name;
            console.log(item.name); // Exit the loop when the item is found
        };
    });
    document.getElementById("r_epoch_size").textContent = result_response_data['epochs'];
    document.getElementById("r_batch_size").textContent = result_response_data['batch_size'];

    var filename = jobId + "_results.pdf"
    $(".export-pdf").click(function() {
        // Convert the DOM element to a drawing using kendo.drawing.drawDOM
        kendo.drawing.drawDOM($(".content-wrapper"))
        .then(function(group) {
            // Render the result as a PDF file
            return kendo.drawing.exportPDF(group, {
                paperSize: "auto",
                margin: { left: "1cm", top: "1cm", right: "1cm", bottom: "1cm" }
            });
        })
        .done(function(data) {
            // Save the PDF file
            kendo.saveAs({
                dataURI: data,
                fileName: filename,
                proxyURL: "https://demos.telerik.com/kendo-ui/service/export"
            });
        });
    });

});