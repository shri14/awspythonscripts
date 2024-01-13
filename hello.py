from flask import Flask
app = Flask(__name__)
@app.route('/hello')
def hello():
    return "Hello to Batch 4!"
@app.route('/')
def hello_world():
    return 'Hello, World!'
if __name__ == '__main__':
    app.run(debug=True)
