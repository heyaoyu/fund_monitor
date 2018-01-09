var output = $("#msg_panel");

var request_timeout = 60000; // 60s
var interval = 0;
var timer = null;

function printPrimaryMsg(msg) {
    var element = $('<div/>', {
        class: 'alert alert-primary',
        role: 'alert',
        text: msg
    });
    output.prepend(element)
}

function printSuccessMsg(msg) {
    var element = $('<div/>', {
        class: 'alert alert-success',
        role: 'alert',
        text: msg
    });
    output.prepend(element)
}

function printDangerMsg(msg) {
    var element = $('<div/>', {
        class: 'alert alert-danger',
        role: 'alert',
        text: msg
    });
    output.prepend(element)
}

function poll() {
    if (timer != null) {
        clearTimeout(timer);
    }
    $.ajax({
        type: "GET",
        url: "http://127.0.0.1:8888/pop_msgs?user=ludi",
        timeout: request_timeout,
        success: function (data, textStatus) {
            if (typeof(data) == "string") { // TimeoutError
                printPrimaryMsg(data);
            } else if (typeof(data) == "object") { // msgs
                var msgs = data.datas;
                for (var i = 0; i < msgs.length; i++) {
                    var msg = msgs[i];
                    printPrimaryMsg(msg);
                }
                interval = 0;
                timer = setTimeout(poll, interval);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            printPrimaryMsg(textStatus + '*' + errorThrown);
            interval += 5000;
            timer = setTimeout(poll, interval);
        }
    });
}

$(document).ready(function () {
    poll();
});