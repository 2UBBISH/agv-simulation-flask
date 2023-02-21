import json
import time

import eventlet
import socketio

start = 0
end = 0
Mapinit = [None, "mapInitc++cbs", "mapInitc++ecbs", "mapInitc++ecbs"]
Algorithm = [None, "computeRoute_cbs", "computeRoute_ecbs", "computeRoute_ecbs"]
choice = 1
avg_time = 0
cnt = 0
def create_server():
    sio = socketio.Server(cors_allowed_origins="*")
    app = socketio.WSGIApp(sio, static_files={
        '/': {'content_type': 'text/html', 'filename': 'blank.html'}
    })

    @sio.event
    def connect(sid, environ):
        print('connect ', sid)
        # f = open("map.json")
        # data = json.dumps(json.load(f))
        # sio.emit('mapInitc++', data)
        #
        # f = open("robot.json")
        # data = json.dumps(json.load(f))
        # sio.emit('computeRoute_ecbs', data)

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)

    # ----------------------
    # 各种自定义监听事件
    # ----------------------

    @sio.on('mapInit')
    def on_mapInit(sid, data):
        # print('receive mapInit event', data)
        global choice
        # print('receive mapInit event', data)
        print("doing algorithm map_init...")
        choice = int(data["data"]["algorithm"])
        data = json.dumps(data)
        # print(data)
        sio.emit(Mapinit[choice], data)

    @sio.on('mapInitc++Response')
    def on_mapInit(sid, data):
        print("mapInitc++Response")
        mapInitResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
            "result": {}
        }
        sio.emit('mapInitResponse', {'data': mapInitResponse_data})

    @sio.on('computeRoute')
    def on_computeRoute(sid, data):
        # print('receive computeRoute event', data)
        print("doing algorithm compute_route...")
        global start
        start = time.clock()
        data = json.dumps(data)
        # print(data)
        sio.emit(Algorithm[choice], data)

    @sio.on('computeRoutec++Response')
    def on_computeRoute(sid, data):
        global avg_time
        global cnt

        data = json.loads(data)
        temp = time.clock() - start
        print("computeRoute {0}:".format(cnt))
        print("calc_time:", temp)
        avg_time += temp
        cnt = cnt + 1
        print("avg_time:", avg_time / cnt)
        computeRouteResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
            "result": data
        }
        sio.emit('computeRouteResponse', {'data': computeRouteResponse_data})

    @sio.on('errorRoute')
    def on_errorRoute(sid, data):
        print('receive errorRoute event', data)
        sio.disconnect(sid)
        print("doing algorithm error_route...")

        errorRouteResponse_data = {
            "errorCode": 0,
            "errorMessage": "",
            "result": {}
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
