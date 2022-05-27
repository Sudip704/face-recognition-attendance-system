''' images : image array 
    cam : camera
    Known_Students_names: only the name without extenton array
    Known_Students_filenames: filenames array
    Known_Students_encodings : image encoding array
'''
import cv2
import numpy as np
import face_recognition
import os
import csv
from datetime import datetime
from flask import Flask, render_template, Response, request, redirect
app = Flask(__name__)
cam=cv2.VideoCapture(0)
path='Train'
images=[]
Known_Students_names=[]
Known_Students_rolls=[]
Known_Students_filenames=os.listdir(path)  # get the filenames inside train folder
for cl in Known_Students_filenames:
    curImg=cv2.imread(f'{path}/{cl}')
    images.append(curImg)    #putting images in a list
    Known_Students_names.append(cl.split('_')[0])  # putting filenames without extension in a list
    Known_Students_rolls.append(cl.split('_')[1].split('.')[0])
def findEncodings(images):    # returns list of face encodings
    encodeList=[]
    for img in images:
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
def markAttendance(name,roll): # notes down the name, roll, and time in the table.html
    with open('Attendance.csv','r+') as f:
        myDataList=f.readlines()
        nameList=[]
        rollList=[]
        for line in myDataList:
            entry=line.split(',')
            nameList.append(entry[0])
        for line in myDataList:
            entry=line.split(',')
            rollList.append(entry[1])
        if roll not in rollList :
            now=datetime.now()
            dtString=now.strftime('%I:%M %p')
            f.writelines(f'{name},{roll},{dtString}\n')
Known_Students_encodings=findEncodings(images)
def generate_frames(): # checks whether the face detected in webcam matches with any of the faces in the uploaded images
    cam.open(0)
    while True:
        success, img=cam.read()
        if not success:
            break
        else:
            try:
                imgS=cv2.resize(img,(0,0),None,0.25,0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                facesCurFrame = face_recognition.face_locations(imgS)
                encodesCurFrame=face_recognition.face_encodings(imgS,facesCurFrame)
                for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
                    matches=face_recognition.compare_faces(Known_Students_encodings,encodeFace,0.5)
                    faceDis=face_recognition.face_distance(Known_Students_encodings,encodeFace)
                    matchIndex=np.argmin(faceDis)
                    if matches[matchIndex]:
                        name=Known_Students_names[matchIndex].upper()
                        roll=Known_Students_rolls[matchIndex]
                        y1,x2,y2,x1=faceLoc
                        y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4
                        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                        cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                        cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                        markAttendance(name,roll)
                ret, buffer = cv2.imencode('.jpg', img)
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(buffer) + b'\r\n')
                cv2.waitKey(1)
            except:
                break;
    cam.release()
@app.route('/')
def index():
    cam.release()
    return render_template('home.html')
@app.route('/attendance')
def attendance():
    return render_template('attendance.html')
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/table')
def table():
    cam.release()
    with open('Attendance.csv', 'r') as csvfile:
        datareader = csv.reader(csvfile)
        csvRows=[]
        for row in datareader:
            csvRows.append(row)     
    return render_template('table.html',data=csvRows)
@app.route('/upload',methods=['GET','POST'])
def upload(): #uploads a new entry (name, email and roll)
    if request.method == 'POST':
        file = request.files['image']
        name=request.form['name']
        roll=request.form['roll']
        ext = (file.filename).split('.')[1]
        stfilename= name+'_'+roll+'.'+ext
        if file and name and roll:
            try:
                file.save(os.path.join('./Train/',stfilename))
                newImg= cv2.imread(f'{path}/{stfilename}')
                newEncode=face_recognition.face_encodings(cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB))[0]
                Known_Students_encodings.append(newEncode)
                Known_Students_names.append(name)
                Known_Students_rolls.append(roll)
                return redirect("/")
            except:
                os.remove('./Train/'+stfilename)
                return render_template('upload.html',badImage=True)
    cam.release()
    return render_template('upload.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=80)