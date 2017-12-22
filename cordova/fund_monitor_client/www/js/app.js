var output = $("#output table tbody");
var error = $("#error table tbody");

var request_timeout = 60000;
var timeout = 0;
var timer = null;

function poll() {
    if (timer != null) {
        clearTimeout(timer);
    }
    $.ajax({
        type: "GET",
        url: "http://127.0.0.1:8888/long_poll_v3",
        timeout: request_timeout,
        success: function (data, textStatus) {
            output.append("<tr><td>" + textStatus + "</td><td>" + data + "</td><td>" + new Date() + "</td></tr>");
            timeout = 0;
            timer = setTimeout(poll, timeout);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            error.append("<tr><td>" + textStatus + "</td><td>" + errorThrown + "</td><td>" + new Date() + "</td></tr>");
            timeout += 5000;
            timer = setTimeout(poll, timeout);
        }
    });
}

$(document).ready(function () {
    poll();
});