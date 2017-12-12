var output = $("#output");
var error = $("#error");

var timeout = 5000;

function poll() {
    $.ajax({
        type: "GET",
        url: "http://127.0.0.1:8888/long_poll",
        timeout: timeout,
        success: function (data, textStatus) {
            output.append("[state: " + textStatus + ", data: { " + data + "} ]<br/>");
            poll();
            timeout = 5000;
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            error.append("[state: " + textStatus + ", error: " + errorThrown + " ]<br/>");
            poll();
            timeout += 5000;
        }
    });
}

$(document).ready(function () {
    poll();
});