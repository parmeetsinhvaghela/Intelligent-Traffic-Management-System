import os
from datetime import date, datetime

from flask import request, render_template, redirect, url_for
from flask import session
from werkzeug.utils import secure_filename

from project import app
from project.com.controller.LoginController import adminLoginSession, adminLogoutSession
from project.com.dao.CameraDAO import CameraDAO
from project.com.dao.VideoDAO import VideoDAO
from project.com.vo.CameraVO import CameraVO
from project.com.vo.VideoVO import VideoVO


@app.route('/user/loadVideo')
def userLoadVideo():
    try:
        if adminLoginSession() == 'user':
            videoDAO = VideoDAO()

            videoVOList = videoDAO.viewLocalData()
            
            return render_template('user/addVideo.html', videoVOList=videoVOList)
        
        else:
            adminLogoutSession()
    except Exception as ex:
        print(ex)


@app.route('/user/userProcessVideo', methods=['POST'])
def userProcessVideo():
    try:
        if adminLoginSession() == 'user':
            UPLOAD_FOLDER = 'project/static/userResources/inputVideo/'
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  
            file = request.files['file']  
            videoFilename = secure_filename(file.filename)  
            videoFilepath = os.path.join(app.config['UPLOAD_FOLDER'])  
            file.save(os.path.join(videoFilepath, videoFilename))  
            video_data = request.form['video_CameraId']
            cameraId = video_data.split(',')[0]
            cameraDAO = CameraDAO()
            cameraVO = CameraVO()
            cameraVO.cameraId = cameraId
            cameraVOList = cameraDAO.editCamera(cameraVO)
            
            return redirect(url_for("userInsertVideo", videoFilename=videoFilename, videoFilepath=videoFilepath,
                                    video_data=video_data, cameraVOList=cameraVOList))
        else:
            adminLogoutSession()
    except Exception as e:
        print(e)


@app.route('/user/insertVideo', methods=['GET'])
def userInsertVideo():
    try:
        if adminLoginSession() == 'user':

            inputvideoFilename = request.args.get('videoFilename')
            inputvideoFilepath = request.args.get('videoFilepath')
            video_data = request.args.get('video_data')
            videoVO = VideoVO()
            videoDAO = VideoDAO()
           
            todayDate = date.today() 
            nowTime = datetime.now() 
            inputvideoFilepath = inputvideoFilepath.replace("project", "..")
            videoVO.video_CameraId = video_data.split(',')[0]
            videoVO.video_CrossroadId = video_data.split(',')[1]
            videoVO.video_AreaId = video_data.split(',')[2]
            videoVO.video_LoginId = session['session_loginId']
            videoVO.inputVideoFilename = inputvideoFilename
            videoVO.inputVideoFilePath = str(inputvideoFilepath)
            videoVO.uploadTime = nowTime.strftime("%H:%M:%S")
            videoVO.uploadDate = todayDate
            videoDAO.insertVideo(videoVO)

            return redirect(url_for('userViewVideo'))
        else:
            adminLogoutSession()
    except Exception as ex:
        print(ex)


@app.route('/user/viewVideo', methods=['GET'])
def userViewVideo():
    try:
        if adminLoginSession() == 'user':
            videoDAO = VideoDAO()
            videoVOList = videoDAO.userViewVideo()
            return render_template('user/viewVideo.html', videoVOList=videoVOList)
        else:
            adminLogoutSession()
    except Exception as ex:
        print(ex)


@app.route('/admin/viewVideo', methods=['GET'])
def adminViewVideo():
    try:
        if adminLoginSession() == 'admin':
            videoDAO = VideoDAO()
            videoVOList = videoDAO.adminViewVideo()
            return render_template('admin/viewVideo.html', videoVOList=videoVOList)
        else:
            adminLogoutSession()
    except Exception as ex:
        print(ex)


@app.route('/admin/deleteVideo', methods=['GET'])
def adminDeleteVideo():
    try:
        if adminLoginSession() == 'admin':
            videoVO = VideoVO()

            videoDAO = VideoDAO()

            videoId = request.args.get('videoId')

            videoVO.videoId = videoId

            videoVOList = videoDAO.deleteVideo(videoVO)

            inputPath = videoVOList.inputVideoFilePath.replace('..', 'project') + videoVOList.inputVideoFilename

            try:
                os.remove(inputPath)


            except Exception as ex:
                print(ex)

            return redirect(url_for('adminViewVideo'))
        else:
            adminLogoutSession()
    except Exception as ex:
        print(ex)


@app.route('/user/deleteVideo', methods=['GET'])
def userDeleteVideo():
    try:
        if adminLoginSession() == 'user':
            videoVO = VideoVO()
            videoDAO = VideoDAO()

            videoId = request.args.get('videoId')
            videoVO.videoId = videoId
            videoVOList = videoDAO.deleteVideo(videoVO)

            inputPath = videoVOList.inputVideoFilePath.replace('..', 'project') + videoVOList.inputVideoFilename


            try:
                os.remove(inputPath)


            except Exception as ex:
                print(ex)

            return redirect(url_for('userViewVideo'))
        else:
            adminLogoutSession()
    except Exception as ex:
        print(ex)
