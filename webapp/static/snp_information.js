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

function make_grid(strongest_alleles) {
    console.log(strongest_alleles)
    var localDataSource = new kendo.data.DataSource({ data: strongest_alleles })
    $("#allele_grid").kendoGrid({
        dataSource: localDataSource,
        filterable: true,
        sortable: true,
        columns: [
            {field: "risk_allele_name", title: "Risk Allele"},
            {field: "risk_allele_value", title: "Allele Value"},
            {field: "risk_freq", title: "Frequency"}
        ]
    });
}


$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');
    var snpId = document.getElementById("snp").textContent
    $.ajax({
        url: "/SNPSearch/GetSNPInfo/" + snpId.toString(),
        type: "GET",
        success: function (data) {
            data = JSON.parse(data)
            document.getElementById("location").innerHTML = data.location;
            document.getElementById("functional_class").innerHTML = data.functional_class;
            document.getElementById("region").innerHTML = data.region;
            document.getElementById("risk_level").innerHTML = data.risk_level;
            document.getElementById("p-value").innerHTML = data.pvalue;
            document.getElementById("maf").innerHTML = data.MAF;
            document.getElementById("is_intergenic").innerHTML = data.is_intergenic;
            document.getElementById("minor_allele").innerHTML = data.minor_allele;
            document.getElementById("genes").innerHTML = data.genes;
            document.getElementById("most_severe_consequence").innerHTML = data.most_severe_consequence;
            document.getElementById("values").innerHTML = data.values;
            make_grid(data.strongest_risk_alleles);
        },
        error: function (error) {
            console.log(`Error ${error}`);
        }
    });
});