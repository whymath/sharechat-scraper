from google.cloud import vision
from google.protobuf.json_format import MessageToJson
import requests
import sys,os,json
import logging

def initialize_googleapi():
    return vision.ImageAnnotatorClient()


def extract_text(client, img_url):
    def image_from_url(img_url):
        resp = requests.get(img_url)
        img_bytes = resp.content 
        return img_bytes

    def detect_text(img_bytes):
        image_data = vision.types.Image(content=img_bytes)
        resp = client.text_detection(image=image_data)
        resp = json.loads(MessageToJson(resp))
        text = resp.get('fullTextAnnotation',{}).get('text','')
        return text

    try:
        img_bytes = image_from_url(img_url)
        text = detect_text(img_bytes)
        return text
    except:
        print(logging.traceback.format_exc())
        pass

