const {
    remote,
    app,
    ipcRenderer
} = require('electron')

const win = remote.getCurrentWindow()

window.switchAlwaysOnTop = () => {
    win.setAlwaysOnTop(!win.isAlwaysOnTop())
}
// 开启调试工具
// remote.getCurrentWebContents().openDevTools()
const ws = new WebSocket("ws://localhost:44446");
window.ws = ws
// 关闭 live2d
window.close = () => {
    win.close()
}
// 关闭 事件 释放资源
win.on('close', (e) => {
    document.live2d_release()
    $('#landlord').remove()
    window.Live2DCubismCore = null
    ws.send(JSON.stringify({
        code: window.code,
        type: 'love2d-death'
    }))
    window.time = null
});
// 传递配置参数
ipcRenderer.on('config', (event, config) => {
    console.log(event);
    console.log(config);
    res = {
        'code': config.code,
        'live2dWindow': true
    }
    if (config.type === 'default') {
        window.bindDefaultEvent()
        ws.send(JSON.stringify(res))
        window.code = 'default'
    } else {
        window.code = config.code
        window.bindConfigEvent(config)
        ws.send(JSON.stringify(res))
    }
})