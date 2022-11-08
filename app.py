from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import time
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import CountVectorizer
import pickle
cv = CountVectorizer(max_features = 1500)

app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mini_project'

# Intialize MySQL
mysql = MySQL(app)


model = pickle.load(open('new_model.pkl','rb'))
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
corpus = []
dataset = pd.read_csv('IFND.csv',encoding = 'unicode_escape')
for i in range(0, 56714):
  review = re.sub('[^a-zA-Z]', ' ', dataset['Statement'][i])
  review = review.lower()
  review = review.split()
  ps = PorterStemmer()
  all_stopwords = stopwords.words('english')
  all_stopwords.remove('not')
  review = [ps.stem(word) for word in review if not word in set(all_stopwords)]
  review = ' '.join(review)
  corpus.append(review)
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features = 1500)
X = cv.fit_transform(corpus).toarray()
y = dataset.iloc[:, -1].values


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM signin WHERE email = %s AND password = %s', [email, password])
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes            
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    # Output message if something goes wrong...
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # Create variables for easy access
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM signin WHERE email = %s AND password=%s', [email, password])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', first_name):
            msg = 'Username must contain only letters!'
        elif not first_name or not last_name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO signin VALUES(%s, %s, %s, %s)', (first_name, last_name, email, password))
            mysql.connection.commit()
            msg = 'Successfully registered! Please Sign-In'
            return render_template('index.html')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html',msg=msg)

@app.route('/fake-news', methods=['GET', 'POST'])
def fakenews():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM fakenews;')
    entries=cursor.fetchall()
    return render_template('fake-news.html',entries=entries)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgotpassword():
    # Output message if something goes wrong...
    return render_template('forgot-password.html')

@app.route('/verified', methods=['GET', 'POST'])
def verified():
    return render_template('verified.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    result = ''
    if request.method == 'POST':
        new_review = request.form['news']
        og_news = request.form['news']
        new_review = re.sub('[^a-zA-Z]', ' ', new_review)
        new_review = new_review.lower()
        new_review = new_review.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        new_review = [ps.stem(word) for word in new_review if not word in set(all_stopwords)]
        new_review = ' '.join(new_review)
        new_corpus = [new_review]
        new_X_test = cv.transform(new_corpus).toarray()
        new_y_pred = model.predict(new_X_test)

        str1 = "" 
        for ele in new_y_pred: 
            str1 += ele 
        
        result = 'The news: ' + str(og_news) + ' is ' + str(str1)

        
    return render_template('verify.html', result = result)


if __name__=="__main__":
    app.run(debug=True)