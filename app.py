from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Examination Management System</h1><p>Project Started Successfully</p>"

if __name__ == '__main__':
    app.run(debug=True)