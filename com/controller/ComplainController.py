import os
from datetime import datetime,date

from flask import render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from project import app
from project.com.dao.ComplainDAO import ComplainDAO
from project.com.vo.ComplainVO import ComplainVO


@app.route('/admin/viewComplain', methods=['GET'])
def adminViewComplain():
    try:
        complainDAO = ComplainDAO()
        ComplainVOList = complainDAO.adminViewComplain()
        print("__________________", ComplainVOList)
        return render_template('admin/viewComplain.html', ComplainVOList=ComplainVOList)
    except Exception as ex:
        print(ex)


@app.route('/admin/loadReply', methods=['GET'])
def adminLoadReply():
    try:
        complainVO = ComplainVO()
        complainId = request.args.get("complainId")
        complainVO.complainId = complainId
        return render_template('admin/addComplainReply.html', complainId=complainVO.complainId)
    except Exception as ex:
        print(ex)


@app.route('/admin/insertReply', methods=['POST'])
def adminInsertReplay():
    try:
        UPLOAD_FOLDER = 'project/static/userResources/reply/'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        complainVO = ComplainVO()
        complainDAO = ComplainDAO()
        complainId = request.form['complainId']
        replySubject = request.form['replySubject']
        replyMessage = request.form['replyMessage']

        now = datetime.now()
        replyDate = now.strftime("%d/%B/%Y")
        replyTime = now.strftime("%I:%M:%S %p")
        replyFile = request.files['replyFile']
        replyFileName = secure_filename(replyFile.filename)
        replyFilePath = os.path.join(app.config['UPLOAD_FOLDER'])
        replyFile.save(os.path.join(replyFilePath, replyFileName))

        complainVO.complainId = complainId
        complainVO.replySubject = replySubject
        complainVO.replyMessage = replyMessage
        complainVO.replyFileName = replyFileName
        complainVO.replyFilePath = replyFilePath.replace("project", "..")
        complainVO.replyDate = replyDate
        complainVO.replyTime = replyTime
        complainVO.complainTo_LoginId = session['session_loginId']
        complainVO.complainStatus = 'replied'

        complainDAO.adminInsertReply(complainVO)
        return redirect(url_for('adminViewComplain'))
    except Exception as ex:
        print(ex)

#user side

@app.route('/user/loadComplain', methods=['GET'])
def userLoadComplain():
    try:
        return render_template('user/addComplain.html')
    except Exception as ex:
        print(ex)

@app.route('/user/insertComplain', methods=['POST'])
def userInsertComplain():
    try:
        UPLOAD_FOLDER = 'project/static/userResources/complain/'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        complainVO = ComplainVO()
        complainDAO = ComplainDAO()
        complainSubject = request.form['complainSubject']
        complainDescription = request.form['complainDescription']

        now = datetime.now()
        complainDate = now.strftime("%d/%B/%Y")
        complainTime = now.strftime("%I:%M:%S %p")
        complainFile = request.files['complainFile']
        complainFileName = secure_filename(complainFile.filename)
        complainFilePath = os.path.join(app.config['UPLOAD_FOLDER'])
        complainFile.save(os.path.join(complainFilePath, complainFileName))

        complainVO.complainSubject = complainSubject
        complainVO.complainDescription = complainDescription
        complainVO.complainDate = complainDate
        complainVO.complainTime = complainTime
        complainVO.complainStatus = "pending"
        complainVO.complainFileName = complainFileName
        complainVO.complainFilePath = complainFilePath.replace("project", "..")
        complainVO.complainFrom_LoginId = session['session_loginId']

        complainDAO.insertComplain(complainVO)
        return redirect(url_for('userViewComplain'))

    except Exception as ex:
        print(ex)


@app.route('/user/viewComplain', methods=['GET'])
def userViewComplain():
    try:
        complainVO = ComplainVO()
        complainDAO = ComplainDAO()
        complainVO.complainFrom_LoginId = session['session_loginId']
        complainList = complainDAO.viewComplain(complainVO)
        print("++++++++++++", complainList)
        return render_template('user/viewComplain.html', complainList=complainList)
    except Exception as ex:
        print(ex)


@app.route('/user/deleteComplain', methods=['GET'])
def userDeleteComplain():
    try:
        complainVO = ComplainVO()
        complainDAO = ComplainDAO()
        complainId = request.args.get('complainId')
        complainVO.complainId = complainId
        complainList = complainDAO.deleteComplain(complainVO)
        path = complainList.complainFilePath.replace("..", "project") + complainList.complainFileName
        os.remove(path)
        return redirect(url_for('userViewComplain'))
    except Exception as ex:
        print(ex)

@app.route("/user/viewComplainReply")
def userViewComplainReply():
    try:
        complainVO = ComplainVO()
        complainDAO = ComplainDAO()
        complainId = request.args.get("complainId")
        print("++++++++++++++",complainId)
        complainVO.complainId = complainId
        complainReplyList = complainDAO.viewComplainReply(complainVO)
        print("+++++++-------",complainReplyList)
        return render_template("user/viewComplainReply.html", complainReplyList=complainReplyList)
    except Exception as ex:
        print(ex)

