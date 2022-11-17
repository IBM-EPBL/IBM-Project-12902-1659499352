import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, redirect, url_for, request, render_template
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
from cloudant.client import Cloudant
from sqlite3 import connect
import requests
import re
import ibm_db
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendmailer import *



# Upload model
model = load_model(r'Updated-Xception-diabetic-retinopathy.h5')


# Define a flask app   
app = Flask(__name__)

# Authenticate using an IAM API key.
client = Cloudant.iam('e0b548a4-365a-4c1b-83c5-504494b2a97c-bluemix', '6TODExgQLwDgTGDZCUY0TKUyMdQqI3gGVsn1WtCnUQsa', connect=True)

# Create a database using an initialized client.
my_database = client.create_database('my_database')

# configure the mail settings   
SENDGRID_API_KEY = "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 "
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
# app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('prasath123t@gmail.com')

mail = Mail(app)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30875;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=tmd49992;PWD=f8N7KQcnld7HlGKl",'','')  # type: ignore
print(conn)
print("connection successful...")


@app.route('/loginpage', methods=['POST','GET'])
def loginpage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email or not password:
            return render_template('login.html',error='Please fill all fields')
        
        query = "SELECT * FROM USERS WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, query) # type:ignore
        ibm_db.bind_param(stmt,1,email) # type:ignore
        ibm_db.bind_param(stmt,2,password) # type:ignore
        ibm_db.execute(stmt) # type:ignore
        isUser = ibm_db.fetch_assoc(stmt) # type:ignore
        print(isUser,password)

        if not isUser:
            return render_template('login.html',error='Invalid Credentials')
        sendemail(email,'Hey there!, Welcome Back!!')      
        return redirect(url_for('home'))

    return render_template('login.html',name='Home')
   
# @app.route('/loginpage', methods=['POST'])
# def loginpage():
#     if request.method == 'POST':
#         user = request.form['_id']
#         passw = request.form['psw']
#         print(user,passw)

#         query = {'_id': {'$eq': user}}

#         docs = my_database.get_query_result(query)
#         print(docs)
#         print(len(docs.all()))
#         print(len(list(docs)))

#         if(len(docs.all())==0):
#             return render_template('login.html', pred = "Login Failed, User not found, please register first!")
#         else:
#             if((user == docs[0][0]['_id']) and (passw == docs[0][0]['psw'])):
#                 return redirect(url_for('prediction'))
#             else:
#                 print("Invalid User, Login Failed, please check your credentials!")
#     return render_template('login.html',name='Home')


@app.route('/home')
def home():
    return render_template('index.html')

# registration page
@app.route('/signup')
def register():
    return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        sql ="INSERT INTO USERS VALUES (?,?,?,?)"
        stmt = ibm_db.prepare(conn,sql)  # type: ignore
        ibm_db.bind_param(stmt, 1, name)  # type: ignore
        ibm_db.bind_param(stmt, 2, email)  # type: ignore
        ibm_db.bind_param(stmt, 3, phone)  # type: ignore
        ibm_db.bind_param(stmt, 4, password)  # type: ignore
        ibm_db.execute(stmt)  # type: ignore
        sendemail(email,'')
        sendemail(email,'We have recieved your email! from your email address to reset the password, we will send you a link to reset your password')
        return redirect(url_for('home'))
    
    return render_template('signup.html')
##
@app.route('/prediction')
def prediction():
    return render_template('prediction.html')
##

# @app.route('/signup', methods=['POST'])
# def afterreg():
#     x = [x for x in request.form.values()]
#     print(x)
#     data = {
#         '_id': x[1], # setting _id is optional
#         'name': x[0],
#         'psw': x[2]
#         }
#     print(data)

#     query = {'_id': {'$eq': data['_id']}}

#     docs = my_database.get_query_result(query)
#     print(docs)
    
#     print(len(list(docs)))
#     print(len(docs.all()))

#     if(len(docs.all())==0):
#         url = my_database.create_document(data)

#         #response = requests.get(url)
#         return render_template('register.html', pred = "Registration Succussful, now please login with your details")
#     else:
#         return render_template('register.html', pred = "Registration Failed, User already exists, please login with your details")

# @app.route('/home')
# def base():
#     return render_template('index.html')

# default home page or route
# @app.route('/')
# def index():
#     return render_template('login.html')

# login page
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/contacts' ,methods=['POST'])
def contacts():
    email = request.form['email']
    sendemail(email,'We have recieved your email!')
    return render_template('contacts.html')



@app.route('/logout.html')
def logout():
    return render_template('logout.html')

# prediction page
@app.route('/result', methods=['GET','POST'])
def res():
    if request.method=='POST':
        f = request.files['image']
        basepath = os.path.dirname(__file__) # getting the current directory
        #print("current path", basepath)
        file_path = os.path.join(basepath, 'uploads', f.filename) # joining the current directory with the uploads folder
        #print("upload path", file_path)
        f.save(file_path) # saving the file to the uploads folder

        # predicting the image
        img = image.load_img(file_path, target_size=(299, 299))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        #print(x)
        img_data = preprocess_input(x)
        prediction = np.argmax(model.predict(img_data), axis=1)

        #prediction = model.predict(x)  # instead of predic_classes, use predict
        #print(prediction)
        index = ['No Diabetic Retinopathy', 'Mild DR', 'Moderate DR', 'Severe DR', 'Proliferative DR']
        #result = str(index[output[0]])
        result = str(index[prediction[0]])
        print(result)
        return render_template('stats.html', prediction = result)

    
@app.route('/features')
def features():
    return render_template('features.html')


@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/contacts')
def requester():
    return render_template('contacts.html')
    
@app.route('/forgot')
def reques():
    return render_template('forgotten-password.html')

@app.route('/forgot',methods=['POST','GET'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        query = "SELECT * FROM USERS WHERE EMAIL=?"
        stmt = ibm_db.prepare(conn, query) # type:ignore
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt) # type:ignore
        isUser = ibm_db.fetch_assoc(stmt) # type:ignore
        # print(isUser,password)
        print(isUser)
        print(stmt)
        sendemail(email,'We have recieved your email! from your email address to reset the password, we will send you a link to reset your password')
        return render_template('login.html')
    return render_template('forgotten-password.html')



if __name__ == '__main__':
    app.run(debug=True)