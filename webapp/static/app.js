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
var loginWindow;
var changePasswordWindow;

function centerWindowMain(window){
    window.center();
}


function sign_in() {
    //creates and populates window for logging in a user
    loginWindow = $("#login_window").show().kendoWindow({
        content: {
            url: 'login'
        },
        // width: 300,
        height: 400,
    });
    loginWindow = $("#login_window").data("kendoWindow");
    centerWindowMain(loginWindow);
    loginWindow.open();
    centerWindowMain(loginWindow);
}




function create_account() {
    //creates a populates a window that a user can create an account in
    $("#account_window").kendoWindow({
        content: {
            url: 'create'
        },
        height: 600,
    });
    var win = $("#account_window").data("kendoWindow");
    win.open();
    win.center();
}

function openSNPWindow(snp) {
    var snpdetails = $("#snpdetails_window").data("kendoWindow");
    if (snpdetails == null) {
        snpdetails = $('#snpdetails_window').kendoWindow({
            modal: true,
            visible: false,
            width: 950,
            height: 650,
        }).data("kendoWindow");
        centerWindowMain(snpdetails);
    }

    snpdetails.title('Details: ' + snp);
    snpdetails.refresh({
        url: '/SNPSearch/get_details/' + snp
    }).open();
    centerWindowMain(snpdetails);
    // snpdetails.center();
}

function logout() {
    //logs out the user
    $.ajax({
        type: "POST",
        url: "/logout/",
        headers: {'X-CSRFToken': csrftoken},
        contentType: "application/x-www-form-urlencoded",
        success: function (response) {
            location.reload();
        }
    });
}

$(window).resize(function () {
    //styling stuff
    $('.login-window').css({
        position: 'absolute',
        left: ($(window).width() -  $('.login-window').outerWidth()) / 2,
        top: ($(window).height() - $('.login-window').outerHeight()) / 2,
    });
});


$(document).ready(function () {
    //sets up buttons for particular actions on click events

    $('#account_creation').kendoButton({
        click: function (e) {
            e.preventDefault();
            create_account();
        }
    });
    $('#account_signin').kendoButton({
        click: function (e) {
            e.preventDefault();
            sign_in();
        }
    });

    $('#account_logout').kendoButton({
        click: logout
    })

    $('#change_pass').kendoButton({
        click: function (e) {
            e.preventDefault();
            showChangePasswordWindow();
        }
    })

    //load content for frontend tabs based on user permissions
    var tabStrip = $("#tabstrip").kendoTabStrip({
        animation: {
            open: {
                effects: "fadeIn"
            }
        },
        contentUrls: [
            'home',
            'glossary',
            'gene_search',
            'snp_search',
            'build',
            'run'
        ],
    }).data("kendoTabStrip");
    tabStrip.select(parseInt(document.getElementById("tabthatisactive").textContent));
    setTimeout(function () {
        tabStrip.tabGroup.on('click', 'li', function (e) {
            var index = $(this).index();
            if (!$(tabStrip.contentElement(index)).is(":empty")) {
                tabStrip.reload($(this));
            }
        })
    });
});

function showChangePasswordWindow(username) {
    console.log(username);
    $("#changePasswordWindow").kendoWindow({
        content: {
            url: "change_pass_window/" + username,
            data: {'username': username}
        },
        width: 300,
        height: 350,
    });
    var changePasswordWindow = $("#changePasswordWindow").data("kendoWindow");
    changePasswordWindow.open();
    changePasswordWindow.center();
}

function closeLoginWindow(){
    console.log(loginWindow);
    loginWindow.close();
}
