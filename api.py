from flask import Flask,jsonify,request
import base64
import numpy as np
import graypy
import logging
import cv2
import pytesseract
import traceback
import sys
import json
import re
#from multiprocessing import queues
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

SERVICE_NAME = "THARACT_API"
handler_1 = graypy.GELFTCPHandler('localhost', 5556)
handler_1.setLevel(logging.INFO)
logger_1 = logging.getLogger("{}".format(SERVICE_NAME))
logger_1.propagate = False
logger_1.setLevel(logging.INFO)
logger_1.addHandler(handler_1)

SERVING_ADDRESS = "localhost"

def base64_to_image(img_b64):
    img = np.fromstring(base64.b64decode(img_b64), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
    #img[:,:,:3] = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2RGB)
    return img

@app.route("/", methods=["GET"])
def ping():
    return jsonify({'THANOS_API': {'Status': 'OK'}}), 200

@app.route("/check", methods=["GET"])
def ping_serving():
    data = {"THANOS_SERVING_HOST": SERVING_ADDRESS}
    try:
        img = cv2.imread("test1.png", cv2.IMREAD_UNCHANGED)
        #imgs = line_pred(imgs, line_model)
        #nums_img = len(imgs)
        #\print("line: ", nums_img))
        data['line'] = {'Status': 'OK', "pred": 1}
        
        texts = pytesseract.image_to_string(img,lang = 'eng',config="--psm 6")
        texts = normalize_text(texts)
        data['print'] = {'Status': 'OK', "pred": texts, "language_code": "eng"}

        #print("hw: ", texts)
        data['hw'] = {'Status': 'OK', "pred": None, "language_code": "eng"}
        
        data["THANOS_SERVING"] = {'Status': 'OK'}
        
    except Exception as e:
        print(traceback.format_exception(None, e, e.__traceback__), file=sys.stderr, flush=True)
        data["THANOS_SERVING"] = {'Status': 'not OK', "Error": str(traceback.format_exception(None, e, e.__traceback__))}
        return jsonify(data), 404
    
    return jsonify(data), 200



@app.route("/api/uet", methods = ["POST"])
def uet():
    data = {}
    data['text'] = None
    #data['scores'] = ''
    #data['time'] = ''
    #start = time.time()
    try:
        dataDict = json.loads(request.data.decode('utf-8'))
        #print(dataDict)
        try:
            img_b64 = dataDict.get("image", None)
            type = dataDict.get("text_type", "printed")
            try:
                imgs = base64_to_image(img_b64)            
                
                texts = ""
                lang = "eng"
                if type == "printed":
                    texts = pytesseract.image_to_string(imgs,lang = 'eng',config="--psm 6")
                    #texts = texts
                else :
                    texts = None
                        
                data['text'] = texts.split()                     
                data['language_code'] = "en"
 
            except Exception as e:
                return jsonify(data),204
        except Exception as e: 
            return jsonify(data),406
    except Exception as e:
        return jsonify(data),400 
        
    #cost_time = (time.time() - start)
    #print("cost time: {:.2f}s".format(cost_time)) 
   
    # print(data)
    return jsonify(data),200


def normalize_text(lines):
    #lines = lines.replace("\n"," \\n")
    new_str = lines.replace("."," .")
    new_str = re.sub('[^a-zA-Z0-9\n\.\(\)\~\!\@\#\$\%\^\&\*_\-+\\\|\{\}\:\;\"\'\<\>\,\?\/]', ' ', new_str)
    return new_str

if __name__ == "__main__" :
    app.run(debug=True)
