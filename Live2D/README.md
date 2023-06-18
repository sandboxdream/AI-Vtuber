# CyberWaifu Server - <u>Live2D</u>

## Getting Started

```shell
cd CyberWaifu/Server/Live2D

python -m http.server
# http://127.0.0.1:8000
```

## Custom Live2D Model

Put your Live2D model in `live2d-model/` as a directory

Open `js/bundle.js`

```javascript
// At Line 1163 (You can also search "Hiyori" in this file to locate)
// ............
e.ModelDir = ["Hiyori"]
// ............
```

Modify it

```javascript
e.ModelDir = ["<Your Live2D model directory name>"]
```

Re-run the http server to check if it works properly

```shell
python -m http.server
# http://127.0.0.1:8000
```

## References

[Download Live2D Cubism SDK for Web - Live2D Cubism](https://www.live2d.com/en/download/cubism-sdk/download-web/)

[Live2D Sample Model Collection - Live2D Cubism](https://www.live2d.com/en/download/sample-data/)

......and more, thanks.

*I am because we are.*
