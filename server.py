from flask import Flask
app = Flask(__name__)

@app.route('/scs/health')
def health():
    return 'health'