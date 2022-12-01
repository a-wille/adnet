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
    $(function(){
        $("#select-type").kendoButtonGroup({
             select: function (e) {
                 console.log(e.indices);
                 var url = '/Glossary/GetAllTerms/'
                 if (e.indices==1) {
                     url = '/Glossary/GetGTerms/'
                 }
                 if (e.indices==2) {
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
        dataTextField: "term",
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
            console.log(text)
            $('#searchDefinition').empty();
            $.ajax({
                type: 'POST',
                url: '/Glossary/GetTermDefinition/',
                headers: {'X-CSRFToken': csrftoken},
                dataType: 'json',
                data: {'name': text},
                success: function(result){
                    console.log(result)
                    $('#searchDefinition').append(
                        '<h3 style="font-size: 24px;">' + result['term'] + '</h3>\n<p style="font-size: 20px;">' +
                        result['definition'] + '</p>'
                    ).hide().fadeIn(1000);
                }
            })
        },
    });

    $("#listView").kendoListView({
        template: "<h3>${term}</h3> \n<p>       ${definition}</p>",
    });

});
