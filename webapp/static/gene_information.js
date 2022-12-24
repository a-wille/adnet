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

function createSNPPanel(mod, nonmod) {
    var inlineDefault = new kendo.data.HierarchicalDataSource({
            data: [
                { text: "Modifying SNPs", items: mod},
                { text: "Non-modifying SNPs", items: nonmod }
            ]
        });
    $("#snpbar").kendoPanelBar({
        // template: "<h1> #= item.text # </h1>",
        dataSource: inlineDefault
    });
    $("#snpbar").data("kendoPanelBar").expand(">li:first")
}

function createPanel(data) {
    $("#panelbar").kendoPanelBar({
        template: "<span> #= item.text # </span>",
        dataSource: [
            {
                'text': "RNA Sequences",
                'items': data
            },
        ],
    });
    $("#panelbar").data("kendoPanelBar").expand(">li:first")
}

function createChart(data) {
    $("#chart").kendoChart({
        dataSource: {
            data: data
        },
        title: {
            text:"Expression by Tissue (RPKM)",
            size:"15px"
        },
        seriesDefaults: {
            type: "bar",
        },
        series: [{
            field: "value",
            categoryField: "tissue",
            color: "#0277bd",
            overlay: {
                gradient: "none"
            }
        }],
        valueAxis: {
            line: {
                visible: false
            },
            title: {
                text: "reads per kilobase of transcript per million reads mapped",
                size: "12px"
            }
        },
        categoryAxis: {
            majorGridLines: {
                visible: false
            }
        },
    });
}

$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');
    var geneId = document.getElementById("gene").textContent
    var url = "/GeneSearch/GetGeneInfo/" + geneId.toString()
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            data = JSON.parse(data)
            document.getElementById("description").innerHTML = data.description;
            document.getElementById("chr").innerHTML = data.chromosome;
            document.getElementById("range").innerHTML = data.range.begin + '-' + data.range.end;
            document.getElementById("orientation").innerHTML = data.range.orientation
            document.getElementById("type").innerHTML = data.type
            createSNPPanel(data.mod, data.nonmod)
            createChart(data.expression)
            createPanel(data.rna_sequences)
        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });
});