let messages = {
    "body": ["大坏蛋！你都多久没理人家了呀，嘤嘤嘤～", "嗨～快来逗我玩吧！", "拿小拳拳锤你胸口！", "不要动手动脚的！快把手拿开~~", "真…真的是不知羞耻！", "Hentai！", "再摸的话我可要报警了！⌇●﹏●⌇", "110吗，这里有个变态一直在摸我(ó﹏ò｡)"]
}


remind = (function () {
    console.log('1111')
    let text;
    var now = new Date().getHours()
    console.log(now)
    if (now > 23 || now <= 5) {
        text = '你是夜猫子呀？这么晚还不睡觉，明天起的来嘛？';
    } else if (now > 5 && now <= 7) {
        text = '早上好！一日之计在于晨，美好的一天就要开始了！';
    } else if (now > 7 && now <= 11) {
        text = '上午好！工作顺利嘛，不要久坐，多起来走动走动哦！';
    } else if (now > 11 && now <= 14) {
        text = '中午了，工作了一个上午，现在是午餐时间！';
    } else if (now > 14 && now <= 17) {
        text = '午后很容易犯困呢，今天的运动目标完成了吗？';
    } else if (now > 17 && now <= 19) {
        text = '傍晚了！窗外夕阳的景色很美丽呢，最美不过夕阳红~~';
    } else if (now > 19 && now <= 21) {
        text = '晚上好，今天过得怎么样？';
    } else if (now > 21 && now <= 23) {
        text = '已经这么晚了呀，早点休息吧，晚安~~';
    } else {
        text = '嗨~ 快来逗我玩吧！';
    }
    showMessage(text, 2000)
});

// 绑定默认事件
window.bindDefaultEvent = () => {
    window.time = window.setInterval(remind, 1800000);
    document.touchHeadHandler = () => {
        showMessage('嗯嗯~~~', 2000)
    }
    document.touchBodyHandler = () => {
        const msg = messages.body[Math.floor(Math.random() * messages.body.length)];
        showMessage(msg, 800)
    }
}
// 绑定配置事件
window.bindConfigEvent = (config) => {
    // 绑定可选按钮事件
    if (config.warmReminder) {
        window.time = window.setInterval(remind, 1800000);
    }
    for (let i = 1; i <= 3; i++) {
        console.log('绑定', i);
        if (config[`btn${i}`] && config[`btn${i}`].trigger && config[`btn${i}`].icon) {
            console.log('绑定可选按钮事件', i);
            $(`#option${i} span`).html(config[`btn${i}`].icon)
            $(`#option${i}`).show()
            $(`#option${i}`).click(() => {
                const data = {
                    type: 'notice',
                    trigger: config[`btn${i}`].trigger,
                    code: window.code
                }
                window.ws.send(JSON.stringify(data))
            })
        }
    }
    if (config['header'] && config['header'].trigger) {
        document.touchHeadHandler = () => {
            const data = {
                type: 'notice',
                trigger: config['header'].trigger,
                code: window.code
            }
            window.ws.send(JSON.stringify(data))
        }
    } else {
        document.touchHeadHandler = () => {
            showMessage('嗯嗯~~~', 2000)
        }

    }
    if (config['body'] && config['body'].trigger) {
        document.touchBodyHandler = () => {
            let data = {
                type: 'notice',
                trigger: config['body'].trigger,
                code: window.code
            }
            window.ws.send(JSON.stringify(data))
        }
    } else {
        document.touchBodyHandler = () => {
            const msg = messages.body[Math.floor(Math.random() * messages.body.length)];
            showMessage(msg, 800)
        }
    }
}
/**
 * 显示消息框
 * @param text 文本
 * @param timeout
 */
function showMessage(text, timeout) {
    if (Array.isArray(text)) text = text[Math.floor(Math.random() * text.length + 1) - 1];
    //console.log('showMessage', text);
    $('.message').stop();
    $('.message').html(text).fadeTo(200, 1);
    if (timeout === null) timeout = 5000;
    hideMessage(timeout);
}

/**
 * 隐藏消息框
 * @param timeout
 */
function hideMessage(timeout) {
    $('.message').stop().css('opacity', 1);
    if (timeout === null) timeout = 5000;
    $('.message').delay(timeout).fadeTo(200, 0);
}
// 设置宽度
window.adjustSize = (width, height) => {
    $("#landlord").height(height).width(width)
    document.getElementById("live2d").width = width;
    document.getElementById("live2d").height = height;
}
adjustSize(900, 1040)

// 信息框
window.receiveMsg = (msg, duration = 2000) => {
    showMessage(msg, duration)
}