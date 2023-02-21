class UI:
    def __init__(self):
        pass

    @classmethod
    def map_init(cls,):
        print("do map_init in UI")
        mapInit_data = {
            "time_in_sec":1,
            "algorithm":1,
            "state_graph":{
                "states":[
                    {
                        "state_id":"0",
                        "pos":{
                            "x":17.55,
                            "y":8.64,
                            "theta":1.57
                        }
                    },
                    {
                        "state_id":"1",
                        "pos":{
                            "x":17.55,
                            "y":9.49,
                            "theta":1.57
                        }
                    }
                ]
            }
        }
        return mapInit_data

    @classmethod
    def render_ui(cls, data):
        print("do render_ui in UI")
        render_ui_data = {}
        return render_ui_data

    @classmethod
    def destroy_ui(cls, data):
        print("do destroy_ui in UI")
        render_ui_data = {}
        return render_ui_data
