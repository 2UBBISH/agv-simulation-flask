import socketio
from debug.client.ui import UI
import schedule
import time


def create_client():
    sio = socketio.Client()

    @sio.event
    def connect():
        print('connection established')

        # ------ mapInit_data ------
        print("doing UI map_init...")
        mapInit_data = UI.map_init()

        sio.emit('mapInit', {'data': mapInit_data})

        # ------ computeRoute_data ------
        computeRoute_data = {}
        sio.emit('computeRoute', {'data': computeRoute_data})

        # ------ errorRoute_data ------
        errorRoute_data = {}
        sio.emit('errorRoute', {'data': errorRoute_data})

        # ------ finish_data ------
        finish_data = {}
        sio.emit('finish', {'data': finish_data})

        # ------ 测试固定每3秒时间发送一个消息 ------
        def emit_compute_route_msg():
            print()
            computeRoute_data = {}
            sio.emit('computeRoute', {'data': computeRoute_data})

        schedule.every(3).seconds.do(emit_compute_route_msg,)

        while True:
            schedule.run_pending()
            time.sleep(1)

    @sio.event
    def connect_error():
        print("The connection failed!")
        sio.disconnect()

    @sio.event
    def disconnect():
        print('disconnected from server')
        sio.disconnect()

    # ----------------------
    # 各种自定义监听事件
    # ----------------------
    @sio.on('mapInitResponse')
    def on_mapInitResponse(data):
        print('receive mapInitResponse event', data)

        UI.render_ui(data)

    @sio.on('computeRouteResponse')
    def on_computeRouteResponse(data):
        print('receive computeRouteResponse event', data)

        UI.render_ui(data)

    @sio.on('errorRouteResponse')
    def on_errorRouteResponse(data):
        print('receive errorRouteResponse event', data)

        UI.render_ui(data)

    @sio.on('finishResponse')
    def on_finishResponse(data):
        print('receive finishResponse event', data)

        UI.destroy_ui(data)

    sio.connect('http://localhost:5001/')
    sio.wait()


def main():
    create_client()


if __name__ == "__main__":
    main()
