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



# Upload model
model = load_model(r'Updated-Xception-diabetic-retinopathy.h5')


# Define a flask app   
app = Flask(__name__)

# Authenticate using an IAM API key.
client = Cloudant.iam('e0b548a4-365a-4c1b-83c5-504494b2a97c-bluemix', '6TODExgQLwDgTGDZCUY0TKUyMdQqI3gGVsn1WtCnUQsa', connect=True)

# Create a database using an initialized client.
my_database = client.create_database('my_database')



# default home page or route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

# registration page
@app.route('/register.html')
def register():
    return render_template('register.html')

##
@app.route('/prediction.html')
def prediction():
    return render_template('prediction.html')
##

@app.route('/afterreg', methods=['POST'])
def afterreg():
    x = [x for x in request.form.values()]
    print(x)
    data = {
        '_id': x[1], # setting _id is optional
        'name': x[0],
        'psw': x[2]
        }
    print(data)

    query = {'_id': {'$eq': data['_id']}}

    docs = my_database.get_query_result(query)
    print(docs)
    
    print(len(list(docs)))
    print(len(docs.all()))

    if(len(docs.all())==0):
        url = my_database.create_document(data)

        #response = requests.get(url)
        return render_template('register.html', pred = "Registration Succussful, now please login with your details")
    else:
        return render_template('register.html', pred = "Registration Failed, User already exists, please login with your details")

@app.route('/home')
def base():
    return render_template('base.html')

# login page
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/afterlogin', methods=['POST'])
def afterlogin():
    user = request.form['_id']
    passw = request.form['psw']
    print(user,passw)

    query = {'_id': {'$eq': user}}

    docs = my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    print(len(list(docs)))

    if(len(docs.all())==0):
        return render_template('login.html', pred = "Login Failed, User not found, please register first!")
    else:
        if((user == docs[0][0]['_id']) and (passw == docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
        else:
            print("Invalid User, Login Failed, please check your credentials!")


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
        return render_template('prediction.html', prediction = result)


if __name__ == '__main__':
    app.run(debug=True)