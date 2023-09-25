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
        dataTextField: "_id",
        filter: "contains",
        autoWidth: true,
        minLength: 3,
        dataSource: {
            transport: {
                read: {
                    url: "/SNPSearch/GetAllSNPNames/",
                    dataType: "json",
                    type: "GET"
                }
            }
        },
        select: function (e) {
            var item = e.item;
            var text = item.text();
            $('#searchSNPs').empty();
            openSNPWindow(text);
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
            pageSize: 15,
            resizable: true,
        },
        // height: 550,
        filterable: true,
        sortable: true,
        resizable: true,
        pageable: true,
        columns: [
            {field:"_id", title:"Name", width:"150px"},
            // {field:"region", title: "Region"},
            {field:"chr", title: "Chr", width:"100px"},
            {field:"chr_pos", title: "Chr. Index", width:"150px"},
            {field:"functional_class", title: "Class", width:"225px"},
            {field:"is_intergenic", title:"Intergenic", width:"150px"},
            // {field:"most_severe_consequence", title: "Potential Effect", width:"200px"},
            {field:"risk_level", title:"Risk Level", width:"150px"},
            {field:"genes", title:"Genes", template: "#= genes.join(', ') #"},
            {
                command:[{
                    name: "Details ",
                    width: "150px",
                    click: function(e) {
                        e.preventDefault();
                        var id = e.currentTarget.closest("tr").cells[0].textContent;
                        openSNPWindow(id);
                    }
                }],
                title: "More Information ",
                template: '<input type="button" class="k-button info" name="info" value="Details" />',
                filterable: false, sortable: false, width: "150px"
            }
        ]
    });
});
