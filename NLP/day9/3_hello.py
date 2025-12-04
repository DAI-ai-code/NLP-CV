from flask import Flask

app = Flask(__name__)  # create application

# define route
@app.route('/') # root route
def hello_world():  # on this url route: / , this hello world function will be executed
    return 'Hello Guys'  

@app.route('/index') # root/index
def indexer():
    return 'Welcome to Index Page'

@app.route('/hello')
def hell():
    return ('hello world')

if __name__=='__main__':
    app.run(debug=True)