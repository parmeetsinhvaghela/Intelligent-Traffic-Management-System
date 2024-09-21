from flask import request, render_template, redirect, url_for, session
from project import app
from project.com.dao.LoginDAO import LoginDAO
from project.com.vo.LoginVO import LoginVO
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



#
@app.route('/', methods=['GET'])
def adminLoadLogin():
    try:
        session.clear()
        print("in /")
        return render_template('admin/Login.html')
    except Exception as ex:
        print(ex)


#


@app.route("/admin/validateLogin", methods=['POST'])
def adminValidateLogin():
    loginUsername = request.form['loginUsername']
    loginPassword = request.form['loginPassword']

    loginVO = LoginVO()
    loginDAO = LoginDAO()

    loginVO.loginUsername = loginUsername
    loginVO.loginPassword = loginPassword
    loginVO.loginStatus = "active"

    loginVOList = loginDAO.validateLogin(loginVO)

    loginDictList = [i.as_dict() for i in loginVOList]

    print(loginDictList)

    lenLoginDictList = len(loginDictList)

    if lenLoginDictList == 0:

        msg = 'Username Or Password is Incorrect !'

        return render_template('admin/Login.html', error=msg)

    else:

        for row1 in loginDictList:

            loginId = row1['loginId']

            loginUsername = row1['loginUsername']

            loginRole = row1['loginRole']

            session['session_loginId'] = loginId

            session['session_loginUsername'] = loginUsername

            session['session_loginRole'] = loginRole

            session.permanent = False

            if loginRole == 'admin':
                return redirect(url_for('adminLoadDashboard'))

            else:
                return render_template('user/Index.html ')


@app.route('/admin/loadDashboard', methods=['GET'])
def adminLoadDashboard():
    try:
        if adminLoginSession() == 'admin':
            return render_template('admin/Index.html')
        else:
            return adminLogoutSession()
    except Exception as ex:
        print(ex)


@app.route('/user/loadDashboard', methods=['GET'])
def userLoadDashboard():
    try:
        return render_template('user/Index.html')
    except Exception as ex:
        print(ex)


@app.route('/admin/loginSession')
def adminLoginSession():
    if 'session_loginId' and 'session_loginRole' in session:

        if session['session_loginRole'] == 'admin':

            return 'admin'

        elif session['session_loginRole'] == 'user':

            return 'user'

        print("<<<<<<<<<<<<<<<<True>>>>>>>>>>>>>>>>>>>>")

    else:

        print("<<<<<<<<<<<<<<<<False>>>>>>>>>>>>>>>>>>>>")

        return False


@app.route("/admin/logoutSession", methods=['GET'])
def adminLogoutSession():
    print('In adminLogoutSession')
    session.clear()

    return redirect(url_for('adminLoadLogin'))


@app.route('/admin/forgotPassword', methods=['GET'])
def adminForgotPassword():
    try:
        return render_template('admin/forgotPassword.html')
    except Exception as ex:
        print(ex)


@app.route('/admin/validateEmail', methods=['POST'])
def adminValidateEmail():

    try:
        loginUsername = request.form['loginUsername']
        loginRole =request.form['loginRole']

        loginVO = LoginVO()
        loginDAO = LoginDAO()

        loginVO.loginUsername = loginUsername
        loginVO.loginRole = loginRole

        loginVOList = loginDAO.validateEmail(loginVO)

        loginDictList = [i.as_dict() for i in loginVOList]

        print(loginDictList)

        lenLoginDictList = len(loginDictList)

        if lenLoginDictList == 0:

            msg = 'Username is Incorrect !'

            return render_template('admin/forgotPassword.html', error=msg)

        elif loginDictList[0]['loginStatus'] == "inactive":

            blkmsg = 'User is temporary blocked by Admin !'

            return render_template('admin/login.html', error_blk=blkmsg)

        else:

            for row1 in loginDictList:

                loginId = row1['loginId']

                loginUsername = row1['loginUsername']

                loginRole = row1['loginRole']

                session['session_loginId'] = loginId

                session['session_loginUsername'] = loginUsername

                session['session_loginRole'] = loginRole

                session.permanent = True

                loginOTP = ''.join((random.choice(string.digits)) for x in range(4))
                print("<<loginOTP>>",loginOTP)

                session['session_loginOTP']=loginOTP

                sender = "trafficeasesignaltimer@gmail.com"

                receiver = loginUsername

                msg = MIMEMultipart()

                msg['From'] = sender

                msg['To'] = receiver

                msg['Subject'] = "TRAFFIC POLICE STATION LOGIN PASSWORD"

                msg.attach(MIMEText(loginOTP, 'plain'))


                server = smtplib.SMTP('smtp.gmail.com', 587)

                server.starttls()

                server.login(sender, "trafficease123")

                text = msg.as_string()

                server.sendmail(sender, receiver, text)

                server.quit()

                return render_template('admin/validateOTP.html')
    except Exception as ex:
        print(ex)


@app.route('/admin/validateOTP', methods=['POST'])
def adminValidateOTP():
    try:
        if request.form['loginOTP'] == session["session_loginOTP"]:

            loginUsername = session['session_loginUsername']
            loginPassword = ''.join((random.choice(string.ascii_letters + string.digits)) for x in range(8))

            print("loginPassword=" + loginPassword)

            sender = "trafficeasesignaltimer@gmail.com"

            receiver = loginUsername

            msg = MIMEMultipart()

            msg['From'] = sender

            msg['To'] = receiver

            msg['Subject'] = "TRAFFIC POLICE STATION LOGIN PASSWORD"

            msg.attach(MIMEText(loginPassword, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)

            server.starttls()

            server.login(sender, "trafficease123")

            text = msg.as_string()

            server.sendmail(sender, receiver, text)

            server.quit()

            loginDAO = LoginDAO()
            loginVO = LoginVO()

            loginId = session['session_loginId']

            loginVO.loginId = loginId
            loginVO.loginPassword = loginPassword

            loginDAO.UpdatePassword(loginVO)

            return render_template('admin/login.html')

        else:
            blockmsg = 'OTP is incorrect, Please enter valid OTP !'

            return render_template('admin/validateOTP.html', error_blk=blockmsg)
    except Exception as ex:
        print(ex)


@app.route("/admin/loadResetPassword", methods=['GET'])
def adminLoadResetPassword():
    try:
        return render_template('admin/resetPassword.html')
    except Exception as ex:
        print(ex)

@app.route("/admin/ResetPassword", methods=['POST'])
def adminResetPassword():
    try:
        loginDAO = LoginDAO()
        loginVO = LoginVO()

        loginId = session['session_loginId']

        loginVO.loginId = loginId
        print("<<loginId>>",loginId)

        loginVOList = loginDAO.validateId(loginVO)
        loginDictList = [i.as_dict() for i in loginVOList]
        print("<<<loginList>>>",loginDictList)

        if loginDictList[0]['loginPassword'] != request.form['oldPassword']:
            msg = 'Old Password is not correct, Please enter again !'

            return render_template('admin/resetPassword.html', error=msg)

        elif request.form['newPassword'] != request.form['confirmPassword']:
            msg2 = 'New Password and confirm new password does not match !'

            return render_template('admin/resetPassword.html', error2=msg2)

        elif loginDictList[0]['loginPassword'] == request.form['oldPassword'] and \
                        request.form['newPassword'] == request.form['confirmPassword'] :

            loginPassword=request.form['newPassword']

            loginVO.loginPassword = loginPassword

            loginDAO.UpdatePassword(loginVO)

            return render_template('admin/login.html')

    except Exception as ex:
        print(ex)







