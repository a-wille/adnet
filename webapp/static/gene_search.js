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

    $("#genes").kendoAutoComplete({
        dataTextField: "gene",
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
            $.ajax({
                type: 'POST',
                url: '/GeneSearch/GetGeneData/',
                headers: {'X-CSRFToken': csrftoken},
                dataType: 'json',
                data: {'name': text},
                success: function(result){
                    console.log(result)
                    // $('#searchDefinition').append(
                    //     '<h3 style="font-size: 24px;">' + result['term'] + '</h3>\n<p style="font-size: 20px;">' +
                    //     result['definition'] + '</p>'
                    // ).hide().fadeIn(1000);
                }
            })
        },
    });

});
