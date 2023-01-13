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

function fill_feature_grid(features){
    $("#featuregrid").kendoGrid({
        dataSource: {
            data: features,
            pageSize: 10,
        },
        filterable: true,
        sortable: true,
        resizable: true,
        pageable: true,
        columns: [
            {field:"location", title: "Location", width:"200px", template:"#=location.start.value# - #=location.end.value#",
            sortable: {
                    compare: function naturalSort (a, b) {
                        a = a.location.start.value.toString() + '-' + a.location.end.value.toString()
                        b = b.location.start.value.toString() + '-' + b.location.end.value.toString()
                        var re = /(^([+\-]?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?(?=\D|\s|$))|^0x[\da-fA-F]+$|\d+)/g,
                            sre = /^\s+|\s+$/g,   // trim pre-post whitespace
                            snre = /\s+/g,        // normalize all whitespace to single ' ' character
                            dre = /(^([\w ]+,?[\w ]+)?[\w ]+,?[\w ]+\d+:\d+(:\d+)?[\w ]?|^\d{1,4}[\/\-]\d{1,4}[\/\-]\d{1,4}|^\w+, \w+ \d+, \d{4})/,
                            hre = /^0x[0-9a-f]+$/i,
                            ore = /^0/,
                            i = function(s) {
                                return (naturalSort.insensitive && ('' + s).toLowerCase() || '' + s).replace(sre, '');
                            },
                        // convert all to strings strip whitespace
                        x = i(a),
                        y = i(b),
                        // chunk/tokenize
                        xN = x.replace(re, '\0$1\0').replace(/\0$/,'').replace(/^\0/,'').split('\0'),
                        yN = y.replace(re, '\0$1\0').replace(/\0$/,'').replace(/^\0/,'').split('\0'),
                        // numeric, hex or date detection
                        xD = parseInt(x.match(hre), 16) || (xN.length !== 1 && Date.parse(x)),
                        yD = parseInt(y.match(hre), 16) || xD && y.match(dre) && Date.parse(y) || null,
                        normChunk = function(s, l) {
                            // normalize spaces; find floats not starting with '0', string or 0 if not defined (Clint Priest)
                            return (!s.match(ore) || l == 1) && parseFloat(s) || s.replace(snre, ' ').replace(sre, '') || 0;
                        },
                        oFxNcL, oFyNcL;
                        // first try and sort Hex codes or Dates
                        if (yD) {
                            if (xD < yD) { return -1; }
                            else if (xD > yD) { return 1; }
                        }
                        // natural sorting through split numeric strings and default strings
                        for(var cLoc = 0, xNl = xN.length, yNl = yN.length, numS = Math.max(xNl, yNl); cLoc < numS; cLoc++) {
                            oFxNcL = normChunk(xN[cLoc] || '', xNl);
                            oFyNcL = normChunk(yN[cLoc] || '', yNl);
                            // handle numeric vs string comparison - number < string - (Kyle Adams)
                            if (isNaN(oFxNcL) !== isNaN(oFyNcL)) {
                                return isNaN(oFxNcL) ? 1 : -1;
                            }
                            // if unicode use locale comparison
                            if (/[^\x00-\x80]/.test(oFxNcL + oFyNcL) && oFxNcL.localeCompare) {
                                var comp = oFxNcL.localeCompare(oFyNcL);
                                return comp / Math.abs(comp);
                            }
                            if (oFxNcL < oFyNcL) { return -1; }
                            else if (oFxNcL > oFyNcL) { return 1; }
                        }
                    }
                }
            },
            {field:"type", title: "Type", width:"225px"},
            {field:"description", title:"Description"},
        ]
    });
}

function fill_effect_grid(effects) {
     $("#effectgrid").kendoGrid({
         dataSource: {
             data: effects
         },
         filterable: true,
         sortable: true,
         resizable: true,
         pageable: true,
         columns: [
             {field: "snp", title: "SNP", width: "225px"},
             {field: "amino_acid_index", title: "Amino Acid Index"},
             {field: "affected_features", title: "Affected Features"},
         ]
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
            document.getElementById("authority").innerHTML = "<a href='https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/" + data.identifier + "'>" + data.authority + "</a>"
            createSNPPanel(data.mod, data.nonmod)
            createChart(data.expression)

            if(data.type == "PROTEIN_CODING"){
                document.getElementById("protein-header").removeAttribute("hidden")
                document.getElementById("protein-features-header").removeAttribute("hidden")
                document.getElementById("protable").style.visibility="visible"
                document.getElementById("p_description").innerHTML = data.protein_description
                document.getElementById("p_sequence").innerHTML = data.sequence
                document.getElementById("locations").innerHTML = data.locations
                document.getElementById("cofactors").innerHTML = data.cofactors
                document.getElementById("catalytic_activity").innerHTML = data.catalytic_activity
                fill_feature_grid(data.protein_features);
                createPanel(data.rna_sequences)
                if(data.nm_len > 0) {
                    fill_effect_grid(data.snp_effects)
                } else {
                    $("#effectgrid").hide()
                }
            } else {
                $("#effectgrid").hide()
                $("#protable").hide();
                $("#featuregrid").hide();
                createPanel(data.rna_sequences)
            }
        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });
});