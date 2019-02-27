from flask import Flask,request,make_response, jsonify,session,send_file
from flask_cors import CORS
import json
import time
import gevent

from breath_detect import BreathDetector

app = Flask(__name__, static_url_path='')

app.config['SECRET_KEY'] ='secret!'
cors = CORS(app, resources={r"/*":{"origins":"*"}})


detectorList = {}

@app.route("/api/algorithm/breath_detect", methods=['POST'])
def req_breath_detect():
    json_obj = request.get_json()
    data = json_obj['data']
    id = json_obj['id']

    if not id in detectorList:
        detectorList[id] = BreathDetector()

    br = detectorList[id].detect(data)

    return make_response(jsonify({'id':id, 'br_list':br}), 200)

@app.route("/api/algorithm/test", methods=['GET'])
def req_test():
    return make_response(jsonify({'id':'123456', 'msg':'hello'}), 200)


def gtask_start_flask():
    app.run(port=8799, host='0.0.0.0')

def main():
    pass

if __name__ == '__main__':
    main()

    gevent.joinall([
        gevent.spawn(gtask_start_flask)
    ])
    while True:
        time.sleep(10)
