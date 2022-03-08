import json
import time
import boto3
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = "hello"
token = None
session_token = ""
secret_key = ""
access_key= ""
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/id', methods=['POST'])
def getid():
    dict_send=request.get_json(force=True)
    global token
    token = dict_send['id_token']
    session['token'] = dict_send['id_token']
    #print (token)
    return token

@app.route('/loggedin')
def loggedin():
    return render_template('loggedin.html')

@app.route('/accesskey')
def accesskey():
    token = session.get('token')
    response,keys = getbuckets(token)
    key1=keys[0]
    key2=keys[1]
    key3=keys[2]
    return render_template('accesskeys.html', key1 = key1 ,key2 = key2 ,key3 = key3)

@app.route('/files')
def buck():
    token = session.get('token')
    response,keys = getbuckets(token)
    # file1=response[0]
    # file2=response[1]
    # file3=response[2]
    # file4=response[3]
    # file5=response[4]
    total = []
    for files in response:
       
        total.append(files)
    
    # file1 = file1,file2 = file2,file3 = file3,file4 = file4,file5 = file5
    return render_template('files.html', files=total )

@app.route('/upload')
def home():
    return render_template("upload.html")

@app.route('/uploading', methods=['post'])
def upload():
    uploading()
    msg = "Upload Done ! You can check by going to /files !!!"
    return render_template("uploaded.html", msg =msg)

@app.route('/loggedout')
def loggedout():
    return render_template('loggedout.html')

def getbuckets(token):
    client = boto3.client('cognito-identity' , region_name="ap-south-1")

    response=client.get_id( IdentityPoolId='ap-south-1:ddd186ee-2b93-4023-bebd-0d7c4d15c819', Logins ={
        "cognito-idp.ap-south-1.amazonaws.com/ap-south-1_leXbHfpyb":token
        })

    identityId = response["IdentityId"]


    client = boto3.client('cognito-identity' , region_name="ap-south-1")
    credentials = client.get_credentials_for_identity(IdentityId=identityId, Logins ={
        "cognito-idp.ap-south-1.amazonaws.com/ap-south-1_leXbHfpyb":token
    }) 

    global session_token,secret_key,access_key

    access_key = credentials['Credentials']['AccessKeyId']
    secret_key = credentials['Credentials']['SecretKey']
    session_token = credentials['Credentials']['SessionToken']
    identity_id = credentials['IdentityId']

    #global keys

    keys = [ access_key , secret_key , session_token ]

    session = boto3.Session( aws_access_key_id=access_key, aws_secret_access_key=secret_key, aws_session_token=session_token, region_name='ap-south-1')

    s3 = session.resource('s3')

    testBucket = s3.Bucket('testingforcognito')

    buckets = list()
    #print("!!! 🎇✨🎇 Congratulations We Did It 🎇✨🎇 !!! ")
    #print("Files in the bucket are :--")
    for objects in testBucket.objects.all():
        buckets.append(objects.key)
    #print("!!! 🎇✨🎇 Congratulations We Did It 🎇✨🎇 !!!" )
    return buckets,keys


def uploading():

   
    
    s3 = boto3.client('s3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token
                    )

    if request.method == 'POST':
        img = request.files['file']
        if img:
                filename = secure_filename(img.filename)
                img.save(filename)
                s3.upload_file(
                    Bucket = "testingforcognito",
                    Filename=filename,
                    Key = filename
                )
if __name__="__main__"():
	app.run(host='0.0.0.0')
