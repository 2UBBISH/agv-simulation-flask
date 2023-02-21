import time

import eventlet
import socketio

# # 如果调试算法1，请打开下面注释
from debug.server.algorithm1 import Algorithm1

# 如果调试算法2，请打开下面注释
from debug.server.algorithm2 import Algorithm2

# 如果调试算法3，请打开下面注释
from debug.server.algorithm3 import Algorithm3
Algorithm = [None, Algorithm1, Algorithm2, Algorithm3]

choice = 1
def create_server():
    sio = socketio.Server(cors_allowed_origins="*")
    app = socketio.WSGIApp(sio, static_files={
        '/': {'content_type': 'text/html', 'filename': 'blank.html'}
    })

    @sio.event
    def connect(sid, environ):
        print('connect ', sid)

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)

    # ----------------------
    # 各种自定义监听事件
    # ----------------------

    @sio.on('mapInit')
    def on_mapInit(sid, data):
        global choice
        global Algorithm
        # print('receive mapInit event', data)
        print("从前端传过来的数据")
        print(data["data"]["algorithm"])
        print("doing algorithm map_init...")

        choice = int(data["data"]["algorithm"])
        result = Algorithm[choice].map_init(data)

        mapInitResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
            "result": result,
        }
        sio.emit('mapInitResponse', {'data': mapInitResponse_data})


    @sio.on('computeRoute')
    def on_computeRoute(sid, data):
        print('receive computeRoute event', data)
        print("doing algorithm compute_route...")
        # print(data)
        global choice
        global Algorithm
        start = time.time()
        result = Algorithm[choice].compute_route(data)
        end = time.time()
        print(end - start)
        computeRouteResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
            "result": result
        }
        sio.emit('computeRouteResponse', {'data': computeRouteResponse_data})

    @sio.on('errorRoute')
    def on_errorRoute(sid, data):
        print('receive errorRoute event', data)
        sio.disconnect(sid)
        print("doing algorithm error_route...")
        global choice
        global Algorithm
        result = Algorithm[choice].error_route(data)

        errorRouteResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
            "result": result
        }
        sio.emit('errorRouteResponse', {'data': errorRouteResponse_data})

    @sio.on('finish')
    def on_finish(sid, data):
        print('receive finish event', data)
        finishResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
        }
        sio.emit('finishResponse', {'data': finishResponse_data})

        # 断开与客户端的连接，看情况以下注释
        # sio.disconnect(sid)

    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)


def main():
    create_server()


if __name__ == "__main__":
    main()
