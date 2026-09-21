from flask import Flask, request, jsonify, render_template,redirect,session
from flask_cors import CORS
import mysql.connector
import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from urllib.parse import urlparse

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Add this line
# CORS(app)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Add this line

CORS(app)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="hv110904",
    database="sentiment_analysis"
)
cursor = db.cursor()
0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        db.commit()
        return redirect('/login')
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        if user:
            session['username'] = user[1]  # Store username in session
            return redirect('/result')
        else:
            return "Invalid Credentials!"
    return render_template('login.html')

# Preprocessing Function
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def textProcess(sent):
    try:
        sent = re.sub('[][)(]', ' ', sent)
        sent = [word for word in sent.split() if not urlparse(word).scheme]
        sent = ' '.join(sent)
        sent = re.sub(r'\@\w+', '', sent)
        sent = re.sub(re.compile("<.*?>"), '', sent)
        sent = re.sub("[^A-Za-z0-9]", ' ', sent)
        sent = sent.lower()
        sent = [word.strip() for word in sent.split()]
        sent = ' '.join(sent)
        tokens = word_tokenize(sent)
        tokens = [word for word in tokens if word not in stop_words]
        sent = [lemmatizer.lemmatize(word) for word in tokens]
        sent = ' '.join(sent)
        return sent
    except Exception as ex:
        print("Error:", ex)
        return sent

# Load Model and CountVectorizer
model = joblib.load(r'D:\Mini Project\trainreview\random_forest_model.joblib')
df1 = pd.read_csv(r'D:\Mini Project\trainreview\modified.csv')
cv = CountVectorizer(min_df=1)
cv.fit(df1['processed_text'])



# @app.route('/result')
# def result():
#     return render_template('result.html')



@app.route('/result')
def result():
    if 'username' in session:
        return render_template('result.html', username=session['username'])
    else:
        return redirect('/login')


# # Route to Submit Review and Predict Sentiment
# @app.route('/submit_review', methods=['POST'])
# def submit_review():
#     data = request.json
#     username = data['username']
#     college = data['college']
#     review = data['review']

#     # Preprocess Review
#     processed_review = textProcess(review)
#     text_feature = cv.transform([processed_review])
#     prediction = model.predict(text_feature)[0]

#     # Insert into Database
#     cursor.execute("INSERT INTO reviews (username, college, review, sentiment) VALUES (%s, %s, %s, %s)", 
#                    (username, college, review, prediction))
#     db.commit()

#     return jsonify({"message": "Review submitted successfully!", "prediction": prediction})


@app.route('/submit_review', methods=['POST'])
def submit_review():
    try:
        data = request.json
        
        if not all(key in data for key in ['username', 'college', 'review']):
            return jsonify({"error": "All fields are required!"}), 400
        
        username = data['username']
        college = data['college']
        review = data['review']

        if username.strip() == "" or college.strip() == "" or review.strip() == "":
            return jsonify({"error": "Fields cannot be empty!"}), 400

        # Preprocess Review
        processed_review = textProcess(review)
        text_feature = cv.transform([processed_review])
        prediction = model.predict(text_feature)[0]

        # Insert into Database
        cursor.execute("INSERT INTO reviews (username, college, review, sentiment) VALUES (%s, %s, %s, %s)", 
                       (username, college, review, prediction))
        db.commit()

        return jsonify({"message": "Review submitted successfully!", "prediction": prediction})

    except Exception as e:
        db.rollback()  # Rollback in case of any error
        return jsonify({"error": "Something went wrong!", "details": str(e)}), 500


# Route to Fetch Recent Reviews
@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    cursor.execute("SELECT username, college, review, sentiment FROM reviews ORDER BY id DESC LIMIT 10")
    reviews = cursor.fetchall()
    review_list = []
    for review in reviews:
        review_list.append({
            "username": review[0],
            "college": review[1],
            "review": review[2],
            "sentiment": review[3]
        })
    return jsonify(review_list)

if __name__ == '__main__':
    app.run(debug=True)


