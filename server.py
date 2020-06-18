from flask import Flask, request, jsonify
import s3_mongo_helper

app = Flask(__name__)


@app.route('/scs/health')
def health():
    return 'health'


@app.route('/scrape')
def start_job():
    return('job initiated')


@app.route('/scs/metadata', methods=['POST'])
def get_metadata():
    data = request.json
    # print(data)
    # print(data["doc_id"])

    filename = data["doc_id"]
    # print(filename)
    coll = s3_mongo_helper.initialize_mongo()
    print(coll)
    result = " "
    for i in coll.find({"filename": filename}):
        result = i
        result.pop('_id', None)
        print(result)
    return jsonify(result)
    # return("hi")
