

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

//creates form for logging in a user to the frontend
    $("#login-form").kendoForm({
        orientation: "vertical",
        items: [{
            type: "group",
            label: "Login",
            items: [
                {field: "username", label: "Username", validation: {required: true}},
                {field: "password", label: "Password", validation: {required: true},
                    hint: "Hint: enter alphanumeric characters only.",
                    editor: function(container, options) {
                        container.append($("<input type='password' class='k-textbox k-valid' id='Password' name='Password' title='Password' required='required' autocomplete='off' aria-labelledby='Password-form-label' data-bind='value:Password' aria-describedby='Password-form-hint'>"));
                    }
                }
            ]
        }],
        validateField: function(e) {
            alert("checking field")
        },
        submit: function(e) {
            alert("my submitted")
            e.preventDefault();
            var user = e.username
            var pass = e.password
            $.ajax({
                type: "POST",
                url: "/client/check_login/",
                data: "{username: " + user + ", password: " + pass + "}",
                contentType: "application/json:",
                success: function(result) {
                    alert(result.d);
                }
            })
        },
        clear: function(ev) {
            alert("clear")
        }
    });