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

    return new Blob(byteArrays, { type: contentType });
}

$(document).ready(function () {
    const csrftoken = getCookie('csrftoken');
    var jobId = document.getElementById("job_id").textContent;

    var response_data;
    $.ajax({
        url: "/JobConfigurations/GetResults/" + jobId,
        type: "GET",
        async: false,
        success: function (data) {
            console.log(data);
            const imageContainer = document.getElementById('image-container');

            data.images.forEach(imageInfo => {
                const image = document.createElement('img');
                const imageBlob = b64toBlob(imageInfo.image_data, imageInfo.content_type);
                const imageUrl = URL.createObjectURL(imageBlob);

                image.src = imageUrl;
                imageContainer.appendChild(image);
            });

        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });
});