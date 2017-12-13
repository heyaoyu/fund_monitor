var output = $("#output");
var error = $("#error");

var timeout = 5000;

function poll() {
    $.ajax({
        type: "GET",
        url: "http://162.219.122.107:8888/long_poll",
        timeout: timeout,
        success: function (data, textStatus) {
            output.append("[state: " + textStatus + ", data: { " + data + "} ]<br/>");
            timeout = 5000;
            poll();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            error.append("[state: " + textStatus + ", error: " + errorThrown + " ]<br/>");
            timeout += 5000;
            poll();
        }
    });
}

$(document).ready(function () {
    poll();
});