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

    $("#snps").kendoAutoComplete({
        dataTextField: "snp",
        filter: "contains",
        autoWidth: true,
        minLength: 3,
        dataSource: {
            transport: {
                read: {
                    url: "/SNPSearch/GetAllSNPs/",
                    dataType: "json",
                    type: "GET"
                }
            }
        },
        select: function (e) {
            var item = e.item;
            var text = item.text();
            console.log(text)
            $('#searchSNPs').empty();
            $.ajax({
                type: 'POST',
                url: '/SNPSearch/GetSNPData/',
                headers: {'X-CSRFToken': csrftoken},
                dataType: 'json',
                data: {'name': text},
                success: function(result){
                    console.log(result)
                    // $('#searchSNPs').append(
                    //     '<h3 style="font-size: 24px;">' + result['term'] + '</h3>\n<p style="font-size: 20px;">' +
                    //     result['definition'] + '</p>'
                    // ).hide().fadeIn(1000);
                }
            })
        },
    });

    $("#snpgrid").kendoGrid({
        dataSource: {
            transport: {
                read: {
                    url: "/SNPSearch/GetAllSNPs/",
                    dataType: "json",
                    type: "GET"
                }
            },
            schema: {
                model: {
                    fields: {
                        chr: { type: "string" },
                        chr_pos: { type: "number" },
                        region: { type: "string" },
                        functional_class: { type: "string" },
                        snp_name: { type: "string" },
                        MAF: {type: "number"},
                        most_severe_consequence: {type: "string"},
                        minor_allele: {type: "string"},
                        allele_string: {type: "string"},
                        is_intergenic: {type: "boolean"},
                        risk_level: {type: "string"}
                        }
                    }
                },
            pageSize: 20,
            serverPaging: true,
            serverFiltering: true,
            serverSorting: true
        },
        height: 550,
        sortable: true,
        pageable: true,
        columns: [
            {field:"snp_name", title:"Name"},
            {field:"region", title: "Region"},
            {field:"chr", title: "Chromosome"},
            {field:"chr_pos", title: "Chr. Index"},
            {field:"functional_class", title: "Class"},
            {field:"is_intergenic", title:"Intergenic"},
            {field:"genes", title:"Genes", template: '{{ dataItem.genes.join(", ") }}'},
            {field:"most_severe_consequence", title: "Potential Effect"},
            {field:"risk_level", title:"Risk Level"},
            "MAF",
            {field:"minor_allele", title: "Minor Allele"},
            {field:"values", title:"Allele Values"},
        ]
    });
});
