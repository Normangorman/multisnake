import json

class MovementRequest():
    def create(idNum, x, y, direction):
        request = {
            "idNum": idNum,
            "grid_x": x,
            "grid_y": y,
            "direction": direction
            }
        request_string = json.dumps(request)
        print("Movement request string: " + request_string)
        return request_string

request = MovementRequest.create(1, 2, 2, 0)
