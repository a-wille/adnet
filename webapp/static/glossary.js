$(document).ready(function () {
    $(function () {
        $("#select-type").kendoButtonGroup({
            select: function (e) {
                var url = '/Glossary/GetAllTerms/'
                if (e.indices == 1) {
                    url = '/Glossary/GetGTerms/'
                }
                if (e.indices == 2) {
                    url = '/Glossary/GetMLTerms/'
                }
                var dataSource = new kendo.data.DataSource({
                    transport: {
                        read: {
                            url: url,
                            dataType: "json",
                            type: "GET"
                        }
                    }
                });

                var listView = $("#listView").data("kendoListView");
                listView.setDataSource(dataSource);

            },
        });
    })

    $("#terms").kendoAutoComplete({
        dataTextField: "name",
        filter: "contains",
        autoWidth: true,
        minLength: 1,
        dataSource: {
            transport: {
                read: {
                    url: "/Glossary/GetAllTerms/",
                    dataType: "json",
                    type: "GET"
                }
            }
        },
        select: function (e) {
            var item = e.item;
            var text = item.text();
            $('#searchDefinition').empty();
            $.ajax({
                type: 'POST',
                url: '/Glossary/GetTermDefinition/',
                headers: {'X-CSRFToken': csrftoken},
                dataType: 'json',
                data: {'name': text},
                success: function (result) {

                    $('#searchDefinition').append(
                        '<h3 class="k-h6" style="font-size: 24px;">' + result['term'] + '</h3>\n<p style="padding-left: 40px; font-size: 20px;">' +
                        result['definition'] + '</p>'
                    ).hide().fadeIn(800);
                }
            })
        },
    });

    $("#listView").kendoListView({
        template: "<div class='glossary-item' style='background-color: ${type == 'g' ? '\\#e9ffed' : '\\#e0f3fd'};'>" +
            "<h3 class='k-h6' style='padding-left: 20px; padding-top: 5px; padding-bottom: 0px;'>${name}</h3>" +
            "<p style='padding-left: 40px; padding-botton: 5px;'>${definition}</p>" +
            "</div>",
    });
});
