import firebase_admin
from firebase_admin import auth,credentials,firestore
#from math import sin, cos, sqrt, atan2, radians
import flask
from flask import abort, jsonify, request, render_template
#import geopy
#from geopy.geocoders import Nominatim
import json
import random
import emails

#--------------------------FIREBASE INITIALIZATION----------------------#
cred = credentials.Certificate("virtual-doctor.json")
firebase_admin.initialize_app(cred)
store=firestore.client()
#-----------------------------------------------------------------------#


#--------------------------FLASK INITIALIZATION-------------------------#
app = flask.Flask(__name__)
#-----------------------------------------------------------------------#

@app.route('/signup',methods = ['POST','GET'])
def signin():
    uid=""
    message=""
    if request.method == 'POST':
        EmailOfUser=request.form["email"]
        PasswordOfUser=request.form["psw"]
        try:
            user=auth.create_user(
            email=EmailOfUser,
            email_verified=False,
            password=PasswordOfUser)
            message="Succesfully created user"
            uid=user.uid
        except:
            message="User already exists"

    #return jsonify("uid:",uid,"message:",message)
    return render_template("signup.html",info = message)


@app.route('/log',methods = ['POST','GET'])
def login():
    dit = {}
    message = ""
    print(f"method is {request.method}")
    if request.method == 'POST':
        EmailOfUser=request.form["email"]
        PasswordOfUser=request.form["psw"]
        message=""
        uid=""
        try:
            user=auth.get_user_by_email(EmailOfUser)
            message="Woohooo, succesfully logged in"
            uid=user.uid
        except:
            message="User authentication failed"

    return render_template("login.html",info = message)

    #return josnify("uid:",uid,"message:",message)

@app.route('/firstpage',methods = ['POST','GET'])
def first():
    return render_template("FirstPage.html")


@app.route('/doc',methods = ['POST','GET'])
def doc():
    return render_template("Doc.html")

@app.route('/pat',methods = ['POST','GET'])
def pat():
    return render_template("Pat.html")

@app.route('/doctordata',methods = ['POST','GET'])
def doctor():
    #docs = store.collection("DOCTORS").stream()

    slot_lst = []
    date_lst = []
    disease_lst = []
    doctor_dit = {}
    if request.method == 'POST':
        doctor_dit["name"] = request.form["Name"]
        doctor_dit["contact"] = request.form["Contact"]
        doctor_dit["address"] = request.form["add"]
        doctor_dit["email"] = request.form["email"]
        disease_lst = request.form["spl"].split(",")
        doctor_dit["specialization"] = disease_lst
        slot_lst = request.form["slot"].split(",")
        doctor_dit["slots"] = slot_lst
        date_lst = request.form["date"].split(",")
        doctor_dit["Dates"] = date_lst
        doctor_dit["clinic"] = request.form["clinic"]
        store.collection("DOCTORS").add(doctor_dit)
    
    return render_template("Docdetail.html")


@app.route('/patient', methods = ['GET','POST'])
def find_doctors():
    count = 0
    lst = []
    doc_lst = []
    patient = {}
    info = {}
    disease_lst = []
    if request.method == 'POST':
        patient["name"] = request.form["Name"]
        patient["age"] = request.form["Age"]
        patient["email"] = request.form["email"]
        disease_lst = request.form["dis"].split(",")
        patient["disease"] = disease_lst
        patient["Applied At"] = firestore.SERVER_TIMESTAMP

        store.collection("PATIENTS").add(patient)

        docs = store.collection("DOCTORS").stream()
        for doc in docs:
            lst = doc.to_dict().get("specialization")
            for each in lst:
                if each in patient["disease"]:
                    doc_lst.append(doc.to_dict)
                    info["doctor_name"] = doc.to_dict().get("name")
                    info["patient_name"] = patient["name"]
                    info["Disease"] = each
                    info["demail"] = doc.to_dict().get("email")
                    info["pemail"] = patient["email"]
                    info["daddress"] = doc.to_dict().get("address")
                    info["slot_assigned"] = random.choice(doc.to_dict().get("slots"))
                    info["date_assigned"] = random.choice(doc.to_dict().get("Dates"))
                    info["clinic"] = doc.to_dict().get("clinic")
                    store.collection("confirmed_sessions").add(info)
    
    return render_template("Patdetail.html")


@app.route('/docapp',methods = ['GET','POST'])
def patient_data():
    patient_lst = []
    docs = store.collection("confirmed_sessions").stream()
    if request.method == 'POST':
        name = request.form["Name"]
        email = request.form["email"]
        for doc in docs:
            if doc.to_dict().get("doctor_name") == name and doc.to_dict().get("demail") == email:
                patient_lst.append(doc.to_dict())
    
    return render_template("Docapp.html",patients = patient_lst)


@app.route('/patapp',methods = ['GET','POST'])
def doctor_data():
    doctor_lst = []
    docs = store.collection("confirmed_sessions").stream()
    if request.method == 'POST':
        name = request.form["Name"]
        email = request.form["email"]
        for doc in docs:
            if doc.to_dict().get("patient_name") == name and doc.to_dict().get("pemail") == email:
                doctor_lst.append(doc.to_dict())
    
    return render_template("Patapp.html",doctors = doctor_lst)


# @app.route('/report',methods = ['POST','GET'])
# def sendmail():
#     if request.method == 'POST':
#        doctor_name = request.form["Name"] 
#        patient_mail = request.form["email"]
#        medicines = request.form["medicine"]
#        symptoms = request.form["symptoms"]
#        html_msg='''<p>'''doctor_name'''</p>'''
#                 '''<p>Symptoms:'''symptoms'''</p>'''
#                 '''<p>medicines:''' medicines'''</p>'''
#                 '''<p><br></p>'''

#         message = emails.html(html=html_msg,
#                           subject="Trial mail",
#                           mail_from=('Technoguy', 'pythonmailsender447@gmail.com'))



#         mail_via_python = message.send(to=patient_mail,
#                                smtp={'host': 'smtp.gmail.com', 
#                                     'timeout': 5,
#                                     'port':587,
#                                     'user':'pythonmailsender447@gmail.com',
#                                     'password':'mailsender',
#                                     'tls':True})

#     return render_template("LastPage.html")

@app.route('/about',methods = ['POST','GET'])
def about():
    return render_template("About.html")



@app.route('/contact',methods = ['POST','GET'])
def contact():
    return render_template("Contact.html")


if __name__ == '__main__':
    app.run(debug=True)

