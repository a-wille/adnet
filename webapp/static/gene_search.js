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
                        var id = e.currentTarget.closest("tr").cells[0].textContent;
                        console.log(id)
                    }
                }],
                title: "More Information ",
                template: '<input type="button" class="k-button info" name="info" value="Details" />',
            filterable: false, sortable: false, width: "150px"}

            // "MAF",
            // {field:"minor_allele", title: "Minor Allele"},
            // {field:"values", title:"Allele Values"},
        ]
    });

});
