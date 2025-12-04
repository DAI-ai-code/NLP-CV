from flask import Flask, request, render_template

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import joblib

app = Flask(__name__)

##############------- Preprocessing ---------#############
ps = PorterStemmer()
swords = stopwords.words('english')

def clean_text(sent):
    tokens = word_tokenize(sent)
    tokens = [token for token in tokens if token.isalpha()]
    tokens = [ps.stem(token.lower()) for token in tokens if token.lower() not in swords]
    return tokens

preprocessor = joblib.load('../day4/preprocessor.model')
classifier = joblib.load('../day4/classifier.model')
##############------- Preprocessing ---------#############

@app.route('/predict')
def input_msg():
    return render_template('spamdetector.html')



@app.route('/spamfinder', methods=['GET', "POST"])
def result():
    if request.method == 'POST':
        data = dict(request.form)
        message = preprocessor.transform([data['message']])
        data['result'] = classifier.predict(message)[0]
        return render_template('spamoutput.html', data=data)


if __name__=='__main__':
    app.run(debug=True)