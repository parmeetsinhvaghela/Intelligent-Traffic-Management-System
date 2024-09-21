from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package.imageproc import ImageProc
from package.videoframegrabber import VideoFrameGrabber


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.frame = {}
        self.videoFrame = {}
        self.mediaPlayer = {}
        self.mediaPlaylist = {}
        self.toolPanel = {}
        self.tool = {}
        self.light = {'R': {}, 'Y': {}, 'G': {}}
        self.digit = {}
        self.grabber = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TEST')
        self.setGeometry(0, 0, 1260, 840)
        self.createMainFrame()
        self.createImageProcessThread()
        self.show()

    def createMainFrame(self):
        self.mainFrame = QFrame(self)
        self.mainFrame.setGeometry(QRect(0, 0, 1260, 840))
        self.mainFrame.setFrameShape(QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QFrame.Raised)
        self.createFrame('A', (0, 0, 630, 420))
        self.createFrame('B', (630, 0, 630, 420))
        self.createFrame('C', (0, 420, 630, 420))
        self.createFrame('D', (630, 420, 630, 420))

    def createFrame(self, side, geometry):
        self.frame[side] = QFrame(self.mainFrame)
        self.frame[side].setGeometry(QRect(*geometry))
        self.frame[side].setFrameShape(QFrame.WinPanel)
        self.frame[side].setFrameShadow(QFrame.Raised)
        self.createVideoFrame(side)
        self.createMediaPlayer(side)
        self.createToolPanel(side)
        self.createTool(side)
        self.createLight('R', side)
        self.createLight('Y', side)
        self.createLight('G', side)
        self.createDigit(side)

    def createVideoFrame(self, side):
        self.videoFrame[side] = QVideoWidget(self.frame[side])
        self.videoFrame[side].setGeometry(QRect(0, 0, 630, 360))

    def createMediaPlayer(self, side):
        self.mediaPlayer[side] = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer[side].setVideoOutput(self.videoFrame[side])
        self.mediaPlayer[side].setMuted(True)
        self.mediaPlaylist[side] = QMediaPlaylist(self.mediaPlayer[side])
        self.mediaPlaylist[side].setPlaybackMode(QMediaPlaylist.Loop)
        self.mediaPlaylist[side].addMedia(
            QMediaContent(QUrl.fromLocalFile("C:\\Users\\Darshan\\Desktop\\Proj TEST\\videos\\" + side + ".mp4")))
        self.mediaPlayer[side].setPlaylist(self.mediaPlaylist[side])
        self.mediaPlayer[side].pause()

    def createToolPanel(self, side):
        self.toolPanel[side] = QFrame(self.frame[side])
        self.toolPanel[side].setGeometry(QRect(0, 360, 630, 60))
        self.toolPanel[side].setFrameShape(QFrame.StyledPanel)
        self.toolPanel[side].setFrameShadow(QFrame.Raised)

    def createTool(self, side):
        self.tool[side] = QFrame(self.toolPanel[side])
        self.tool[side].setGeometry(QRect(225, 15, 180, 30))
        self.tool[side].setFrameShape(QFrame.StyledPanel)
        self.tool[side].setFrameShadow(QFrame.Raised)

    def createLight(self, type, side):
        color = {'R': 'red', 'Y': 'orange', 'G': 'green'}
        geometryX = {'R': 0, 'Y': 40, 'G': 80}
        self.light[type][side] = LightWidget(self.tool[side], color[type])
        self.light[type][side].setGeometry(QRect(geometryX[type], 0, 30, 30))

    def createDigit(self, side):
        self.digit[side] = LCDNumber(self.tool[side])
        self.digit[side].setGeometry(QRect(120, 0, 60, 30))

    def createImageProcessThread(self):
        self.imageProcessThread = ImageProcessThread()
        self.imageProcessThread.timeSet.connect(self.timeSet)
        self.imageProcessThread.screenshotCall.connect(self.screenshotCall)
        self.imageProcessThread.start()

    @pyqtSlot(list, int)
    def timeSet(self, countdownTimes, cycleTime):
        timeA, timeB, timeC, timeD = countdownTimes
        self.createStatemachine('A', timeA, 0, cycleTime)
        self.createStatemachine('B', timeB, timeA + 2, cycleTime)
        self.createStatemachine('C', timeC, timeA + timeB + 4, cycleTime)
        self.createStatemachine('D', timeD, timeA + timeB + timeC + 6, cycleTime)

    def createStatemachine(self, side, greenTime, redTime, cycleTime):
        machine = QStateMachine(self)
        redGoingYellow = self.createLightState(side, 'R', redTime)
        redGoingYellow.entered.connect(lambda: self.mediaPlayer['A'].pause())
        redGoingYellow.entered.connect(lambda: self.mediaPlayer['B'].pause())
        redGoingYellow.entered.connect(lambda: self.mediaPlayer['C'].pause())
        redGoingYellow.entered.connect(lambda: self.mediaPlayer['D'].pause())
        redGoingYellow.entered.connect(lambda: self.digit[side].countdown(redTime))
        yellowGoingGreen = self.createLightState(side, 'Y', 1)
        greenGoingYellow = self.createLightState(side, 'G', greenTime)
        greenGoingYellow.entered.connect(lambda: self.mediaPlayer[side].play())
        greenGoingYellow.entered.connect(lambda: self.digit[side].countdown(greenTime, 'green'))
        yellowGoingRed = self.createLightState(side, 'Y', 1)
        remainingRedTime = (cycleTime - redTime - greenTime - 2)
        finalRed = self.createLightState(side, 'R', remainingRedTime)
        finalRed.entered.connect(lambda: self.mediaPlayer[side].pause())
        finalRed.entered.connect(lambda: self.digit[side].countdown(remainingRedTime))
        redGoingYellow.addTransition(redGoingYellow.finished, yellowGoingGreen)
        yellowGoingGreen.addTransition(yellowGoingGreen.finished, greenGoingYellow)
        greenGoingYellow.addTransition(greenGoingYellow.finished, yellowGoingRed)
        yellowGoingRed.addTransition(yellowGoingRed.finished, finalRed)
        finalRed.addTransition(finalRed.finished, machine.stop())
        machine.addState(redGoingYellow)
        machine.addState(yellowGoingGreen)
        machine.addState(greenGoingYellow)
        machine.addState(yellowGoingRed)
        machine.addState(finalRed)
        machine.setInitialState(redGoingYellow)
        machine.start()

    def createLightState(self, side, type, duration, parent=None):
        light = self.light[type][side]
        lightState = QState(parent)
        timer = QTimer(lightState)
        timer.setInterval(duration * 1000)
        timer.setSingleShot(True)
        timingState = QState(lightState)
        timingState.entered.connect(light.turn_on)
        timingState.entered.connect(timer.start)
        timingState.exited.connect(light.turn_off)
        timingState.addTransition(timer.timeout, QFinalState(lightState))
        lightState.setInitialState(timingState)
        return lightState

    @pyqtSlot()
    def screenshotCall(self):
        self.takeScreenshot('A')
        self.takeScreenshot('B')
        self.takeScreenshot('C')
        self.takeScreenshot('D')

    def takeScreenshot(self, side):
        self.grabber[side] = VideoFrameGrabber(self.videoFrame[side], side, self.videoFrame[side])
        self.grabber[side].frameAvailable.connect(self.processFrame)
        self.mediaPlayer[side].play()
        self.mediaPlayer[side].setVideoOutput(self.grabber[side])


    @pyqtSlot(QImage, str)
    def processFrame(self, image, side):
        image.save('C:\\Users\\Darshan\\Desktop\\proj TEST\\images\\' + side + '.jpg')
        self.mediaPlayer[side].setVideoOutput(self.videoFrame[side])
        self.mediaPlayer[side].pause()


class LightWidget(QLabel):
    def __init__(self, parent=None, color='green'):
        super(LightWidget, self).__init__(parent=parent)
        self.setStyleSheet("background-color: " + color + "; border-radius: 15px;")
        self.turn_off()

    def setOpacity(self, i=0):
        op = QGraphicsOpacityEffect(self)
        op.setOpacity(i)
        self.setGraphicsEffect(op)

    @pyqtSlot()
    def turn_on(self):
        self.status = True
        self.setOpacity(0.9)

    @pyqtSlot()
    def turn_off(self):
        self.status = False
        self.setOpacity(0.2)


class LCDNumber(QLCDNumber):
    def __init__(self, parent=None):
        super(LCDNumber, self).__init__(parent=parent)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.countdownTime = 0
        self.color = 'red'

    def setColor(self, color):
        palette = self.palette()
        palette.setColor(palette.WindowText, QColor(color))
        self.setPalette(palette)

    @pyqtSlot(int)
    @pyqtSlot(int, str)
    def countdown(self, countdownTime, color='red'):
        self.countdownTime = countdownTime
        self.setColor(color)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerTimeout)
        self.timer.start(1000)

    def timerTimeout(self):
        if self.countdownTime == 0:
            self.timer.stop()
        self.display(int(self.countdownTime))
        self.countdownTime = self.countdownTime - 1


class ImageProcessThread(QThread):
    timeSet = pyqtSignal(list, int)
    screenshotCall = pyqtSignal()

    def __init__(self):
        super(ImageProcessThread, self).__init__()

    def run(self):
        while True:
            self.screenshotCall.emit()
            self.sleep(2)
            imageProc = ImageProc()
            countdownTimes, cycleTime = imageProc.run()
            print(countdownTimes, cycleTime)
            self.timeSet.emit(countdownTimes, cycleTime)
            self.sleep(cycleTime)
