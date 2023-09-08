$(function () {
    // 场景切换
    $('#nextScene').click(() => {
        document.nextScene()
    })
    $('#Fixed').click(() => {
        window.switchAlwaysOnTop()
    })
    window.ws.onmessage = function (event) {
        const msgObj = JSON.parse(event.data)
        if (msgObj.type === 'message') {
            const duration = msgObj.duration ? msgObj.duration : 2000
            window.receiveMsg(msgObj.message, duration)
        } else if (msgObj.type === 'death') {
            window.close()
        }
    };
})