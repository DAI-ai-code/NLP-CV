from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def first():
    return render_template('subjects.html')

@app.route('/result', methods=['post'])
def fun_result():
    name = request.form['name']
    phy = int(request.form['phy'])
    che = int(request.form['che'])
    
    mat = int(request.form['mat'])
    per = (phy + che + mat) / 3
    return render_template('rizz.html', value=per)

    

if __name__=='__main__':
    app.run(debug=True) 