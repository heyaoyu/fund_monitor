var output = $("#msg_panel");

var request_timeout = 60000; // 60s
var interval = 0;
var timer = null;


// msg: gztime, name, fundcode, gsz, jzrq, dwjz, gszzl, bjtime, type
function processMsg(jsonstr) {
    try {
        json = $.parseJSON(jsonstr);
        ret =
            "北京时间：" + json['bjtime'] +
            ",基金代码：" + json['fundcode'] +
            ",基金名称：" + json['name'] +
            ",估值时间：" + json['gztime'] +
            ",下限：" + json['min'] +
            ",估算值：" + json['gsz'] +
            ",上限：" + json['max'] +
            ",净值日期：" + json['jzrq'] +
            ",单位净值：" + json['dwjz'] +
            ",估算增长率：" + json['gszzl'];
        if (json['type'] == 1) {
            ret = "日常更新：" + ret;
        }
        if (json['gsz'] <= json['min']) {
            printDangerMsg(ret);
        } else if (json['min'] < json['gsz'] && json['gsz'] < json['max']) {
            printPrimaryMsg(ret);
        } else if (json['max'] <= json['gsz']) {
            printSuccessMsg(ret);
        }
    } catch (err) {
        printPrimaryMsg(jsonstr);
    }
}

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
    var user = $("#current_user").html();
    $.ajax({
        type: "GET",
        url: "http://162.219.122.107:8888/pop_msgs?user=" + user,
        //url: "http://127.0.0.1:8888/pop_msgs?user=" + user,
        xhrFields: {
            withCredentials: true
        },
        timeout: request_timeout,
        success: function (data, textStatus) {
            if (typeof(data) == "object") {
                if (data.status == "ok") {
                    var msgs = data.datas;
                    for (var i = 0; i < msgs.length; i++) {
                        var msg = msgs[i];
                        processMsg(msg);
                    }
                } else {
                    if (data.code == 1) { // not login
                        printDangerMsg(data.datas);
                        return;
                    } else if (data.code == 2) {// timeout
                        // ignore
                    }
                }
            }
            interval = 0;
            timer = setTimeout(poll, interval);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //printPrimaryMsg(textStatus + '*' + errorThrown);
            interval += 5000;
            timer = setTimeout(poll, interval);
        }
    });
}

function login() {
    var user = $("#login-user").val();
    $.ajax({
        type: "GET",
        url: "http://162.219.122.107:8888/login?user=" + user,
        //url: "http://127.0.0.1:8888/login?user=" + user,
        xhrFields: {
            withCredentials: true
        },
        success: function (data) {
            $("#current_user").html(data.user);
            $("#login-form").hide();
            poll();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            printDangerMsg("和总部联系不上啊")
        }
    });
}

function init() {
    $("#login-btn").click(login);
}

$(document).ready(function () {
    init();
});