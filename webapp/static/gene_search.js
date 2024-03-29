$(document).ready(function () {
    var snpdetails = $("#snpdetails_window").data("kendoWindow");

    if (snpdetails == null) {
        snpdetails = $('#snpdetails_window').kendoWindow({
            modal: true,
            visible: false,
            width: 950,
            height: 650,
        }).data("kendoWindow");
    }


    $("#information_window").kendoWindow({
        modal: false,
        visible: false,
        width: 900,
        height: 750,
    });

    $("#genes").kendoAutoComplete({
        dataTextField: "_id",
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
            var gene = item.text();
            $('#geneData').empty();
            info.title('Gene: ' + gene);
            info.refresh({
                url: '/GeneSearch/get_information/' + gene
            });
            info.center().open();
        },
    });

    info = $('#information_window').kendoWindow({
        modal: false,
        visible: false,
        width: 950,
        height: 900,
    }).data("kendoWindow");

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
                        _id: {type: "string"},
                        chromosome: {type: "string"},
                        type: {type: "string"},
                        description: {type: "string"},
                        mod_len: {type: "number"},
                        nm_len: {type: "number"}
                    }
                }
            },
            pageSize: 15,
            resizable: true,
            serverSorting: false,
        },
        height: 700,
        filterable: true,
        sortable: true,
        resizable: true,
        scrollable: {
            endless: true
        },
        columns: [
            {field: "_id", title: "Name", width: "150px"},
            {
                field: "chromosome",
                title: "Location",
                width: "250px",
                template: "#=chromosome#:#=range.begin# - #=range.end#",
                sortable: {
                    compare: function naturalSort(a, b) {
                        if (a.chromosome == null || a.range.begin == null) {
                            console.log(a);
                        }
                        a = a.chromosome.toString() + ':' + a.range.begin.toString() + '-' + a.range.end.toString()
                        b = b.chromosome.toString() + ':' + b.range.begin.toString() + '-' + b.range.end.toString()
                        var re = /(^([+\-]?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?(?=\D|\s|$))|^0x[\da-fA-F]+$|\d+)/g,
                            sre = /^\s+|\s+$/g,   // trim pre-post whitespace
                            snre = /\s+/g,        // normalize all whitespace to single ' ' character
                            dre = /(^([\w ]+,?[\w ]+)?[\w ]+,?[\w ]+\d+:\d+(:\d+)?[\w ]?|^\d{1,4}[\/\-]\d{1,4}[\/\-]\d{1,4}|^\w+, \w+ \d+, \d{4})/,
                            hre = /^0x[0-9a-f]+$/i,
                            ore = /^0/,
                            i = function (s) {
                                return (naturalSort.insensitive && ('' + s).toLowerCase() || '' + s).replace(sre, '');
                            },
                            // convert all to strings strip whitespace
                            x = i(a),
                            y = i(b),
                            // chunk/tokenize
                            xN = x.replace(re, '\0$1\0').replace(/\0$/, '').replace(/^\0/, '').split('\0'),
                            yN = y.replace(re, '\0$1\0').replace(/\0$/, '').replace(/^\0/, '').split('\0'),
                            // numeric, hex or date detection
                            xD = parseInt(x.match(hre), 16) || (xN.length !== 1 && Date.parse(x)),
                            yD = parseInt(y.match(hre), 16) || xD && y.match(dre) && Date.parse(y) || null,
                            normChunk = function (s, l) {
                                // normalize spaces; find floats not starting with '0', string or 0 if not defined (Clint Priest)
                                return (!s.match(ore) || l == 1) && parseFloat(s) || s.replace(snre, ' ').replace(sre, '') || 0;
                            },
                            oFxNcL, oFyNcL;
                        // first try and sort Hex codes or Dates
                        if (yD) {
                            if (xD < yD) {
                                return -1;
                            } else if (xD > yD) {
                                return 1;
                            }
                        }
                        // natural sorting through split numeric strings and default strings
                        for (var cLoc = 0, xNl = xN.length, yNl = yN.length, numS = Math.max(xNl, yNl); cLoc < numS; cLoc++) {
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
                            if (oFxNcL < oFyNcL) {
                                return -1;
                            } else if (oFxNcL > oFyNcL) {
                                return 1;
                            }
                        }
                    }
                }
            },
            {field: "type", title: "Type", width: "225px"},
            {field: "description", title: "Description"},
            {field: "mod_len", title: "Modifying SNPs", width: "175px"},
            {field: "nm_len", title: "Non-modifying SNPs", width: "200px"},
            {
                command: [{
                    name: "Details ",
                    width: "160px",
                    click: function (e) {
                        e.preventDefault();
                        var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
                        gene = dataItem._id;
                        info.title('Gene: ' + gene);
                        info.refresh({
                            url: '/GeneSearch/get_information/' + gene
                        });
                        info.center().open();
                        centerWindowMain(info);
                    }
                }],
                title: "More Information ",
                template: '<input type="button" class="k-button info" name="info" value="Details" />',

                filterable: false, sortable: false, width: "160px"
            }
        ]
    });
});
