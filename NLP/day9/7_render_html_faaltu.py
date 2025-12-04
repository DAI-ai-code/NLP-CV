from flask import Flask, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def hello_admin():
    return """
            <html>
            <title>My Web Page</title>
            <body>
            <h1> <center> Welcome to Flask </center> </h1>
            <h2> <center> The language of web </center> </h2>
            </body>
            </html>
            """

    

if __name__=='__main__':
    app.run(debug=True)