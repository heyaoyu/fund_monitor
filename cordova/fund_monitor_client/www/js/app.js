var output = $("#output ul");
var error = $("#error ul");

var request_timeout = 60000;
var timeout;
var timer = null;

function poll() {
    if (timer != null) {
        clearTimeout(timer);
    }
    $.ajax({
        type: "GET",
        //url: "http://162.219.122.107:8888/long_poll",
        url: "http://127.0.0.1:8888/long_poll",
        timeout: request_timeout,
        success: function (data, textStatus) {
            output.append("<li>[state: " + textStatus + ", data: { " + data + "} ]</li>");
            timeout = 0;
            timer = setTimeout(poll, timeout);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            error.append("<li>[state: " + textStatus + ", error: " + errorThrown + " ]</li>");
            timeout += 5000;
            timer = setTimeout(poll, timeout);
        }
    });
}

$(document).ready(function () {
    poll();
});