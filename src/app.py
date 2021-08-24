from flask import Flask
from flask import request
from flask_login import LoginManager
import bcrypt

app = Flask(__name__)
app.secret_key = "muicpeeps12345"

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if (username != None and password != None):
        passwordToByte = str.encode(password)
        passwordHash = bcrypt.hashpw(passwordToByte, bcrypt.gensalt(100))
        # excute to database
        return True
    return False



@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
