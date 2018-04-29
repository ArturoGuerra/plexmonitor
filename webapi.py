from monitor import Monitor
from flask_cors import CORS
from flask import Flask, jsonify

app = Flask(__name__)
CORS(app)
mon = Monitor()

@app.route('/', methods=['GET'])
def index():
    raw = mon.check()
    json = {
        'error': raw[1],
        'running': raw[0]
    }
    return jsonify(json)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)

