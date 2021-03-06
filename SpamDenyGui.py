# -*- coding: utf-8 -*-
# !/usr/bin/python3

from SpamDenyLib import *

import signal
import webbrowser
from multiprocessing import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# == Main Window == #
class Win(QMainWindow):
    def __init__(self):
        super(Win, self).__init__()

        # == SpamDeny Object == #
        self.SD = SpamDeny()
        self.SD.stdOut = False

        # == Datas == #
        self.icon = DirSep(self.SD.root + 'icon.ico')
        self.winWidth = 400
        self.winHeight = 200
        self.winTop = 50
        self.winLeft = 50
        self.nameBtnStyle = 'font-size: 14px; color: #333333; font-weight: bold;'
        self.projdBtnStyle = 'font-size: 12px; color: #555555; font-weight: bold;'
        self.dwCheckBtnStyle = 'font-size: 14px; color: #333333; font-weight: bold;'
        self.addLocalBtnStyle = 'font-size: 14px; color: #333333; font-weight: bold; border: 0;'
        self.genBtnStyle = 'font-size: 14px; font-weight: bold; color: #ffffff; background: #333333; border: 0;'
        self.finishBtnStyle = 'font-size: 14px; font-weight: bold; color: #000000; background: #00ee00; border: 0;'
        self.resultStyle = 'font-size: 15px; font-weight: bold; color: #000000; background: transparent; border: 0;'
        self.progressbarStyle = '''
        QProgressBar,
        QProgressBar::chunk{
            background: transparent; 
            border: 0; 
            margin: 0; 
            padding: 0; 
            border-radius: none;
        }
        
        QProgressBar::chunk {
            background: #00dd00;
            width: 4px;
        }
        '''
        self.dwCheck = None
        self.addFile = None
        self.qprog = None
        self.result = None
        self.genBtn = None
        self.genStart = False
        self.rpTim = False
        self.procs = []

        # == Init Body & Show Window == #
        self.win_init()
        self.win_body()
        self.show()

    # == Init Window == #
    def win_init(self):
        self.setWindowIcon(QIcon(self.icon))
        self.setWindowTitle(self.SD.obj)
        self.setFixedSize(self.winWidth, self.winHeight)
        self.move(self.winLeft, self.winTop)
        self.setStyleSheet('background: #ffffff;')

    # == Win Body == #
    def win_body(self):
        # Icon #
        icon = QLabel(self)
        icon.setPixmap(QPixmap(self.icon))
        icon.setGeometry(-10, -10, 120, 120)

        # Name #
        name = QLabel(self.SD.obj, self)
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(self.nameBtnStyle)
        name.setGeometry(0, 100, 120, 20)

        # Status #
        projd = QLabel('v{} ({})'.format(self.SD.version, self.SD.status), self)
        projd.setAlignment(Qt.AlignCenter)
        projd.setStyleSheet(self.projdBtnStyle)
        projd.setGeometry(0, 120, 120, 20)

        # Project Link #
        projd = QLabel('Go to Project Page', self)
        projd.setAlignment(Qt.AlignCenter)
        projd.setStyleSheet(self.projdBtnStyle)
        projd.setGeometry(0, 140, 120, 20)
        projd.mousePressEvent = self.project_url
        projd.setCursor(QCursor(Qt.PointingHandCursor))

        # Download Checkbox #
        self.dwCheck = QCheckBox(' Download Database', self)
        self.dwCheck.setStyleSheet(self.dwCheckBtnStyle)
        self.dwCheck.setGeometry(230, 20, 160, 20)
        self.dwCheck.setCursor(QCursor(Qt.PointingHandCursor))
        self.dwCheck.setChecked(True)

        # File Picker Button #
        self.addFile = QPushButton('+ Local Database', self)
        self.addFile.setStyleSheet(self.addLocalBtnStyle)
        self.addFile.setGeometry(230, 60, 160, 20)
        self.addFile.setCursor(QCursor(Qt.PointingHandCursor))
        self.addFile.clicked.connect(self.openFilePicker)

        # Generate Button #
        self.genBtn = QPushButton('Generate', self)
        self.genBtn.setStyleSheet(self.genBtnStyle)
        self.genBtn.setGeometry(230, 110, 160, 30)
        self.genBtn.clicked.connect(self.doGen)

        # Progressbar #
        self.qprog = QProgressBar(self)
        self.qprog.setGeometry(5, 165, 390, 4)
        self.qprog.setStyleSheet(self.progressbarStyle)
        self.qprog.setFormat('')
        self.qprog.setVisible(False)

        # Result #
        self.result = QLabel(self)
        self.result.setStyleSheet(self.resultStyle)
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setGeometry(5, 170, 390, 25)

    # == Open Project Url into Browser == #
    def project_url(self, event):
        webbrowser.open_new_tab(self.SD.projectUrl)

    # == File Picker == #
    def openFilePicker(self):
        files = QFileDialog.getOpenFileNames(self, 'Local Database')
        # Check Added Files #
        if len(files[0]) > 0:
            # Add Files Path #
            self.SD.local = files[0]
            # Change Label #
            self.addFile.setText('+ Local Database ({})'.format(len(files[0])))

    # == Generate / Filter == #
    def doGen(self):
        # Check Empty #
        if len(self.SD.local) < 1 and \
                self.dwCheck.isChecked() is False:
            self.result.setText('Select Database')
            return

        # Disable Buttons #
        self.dwCheck.setDisabled(True)
        self.addFile.disconnect()
        self.genBtn.setDisabled(True)
        self.genBtn.setText('Job Started')

        # Start Process for Filter #
        startPF = Process(target = self.startPF())
        self.procs.append(startPF)
        startPF.start()

    # == Start Process & Filter == #
    def startPF(self):
        # Download if checked #
        dp = False
        if self.dwCheck.isChecked():
            dp = Process(target = self.SD.download)
            self.procs.append(dp)
            dp.start()

        # Start Filtering Process #
        while 1:
            if dp is False or dp.is_alive() is False:
                fp = Process(target = self.SD.filter)
                self.procs.append(fp)
                fp.start()
                break

    # == Result Progress == #
    def resultProgress(self):
        # Progress & Feedback Loop #
        if os.path.isfile(DirSep(self.SD.tmpObj + '/process.json')):
            logR = self.SD.file_read(DirSep(self.SD.tmpObj + '/process.json'))
            if len(logR) > 20:
                logR = json.loads(logR)

                # Download / Unzip #
                if logR['status'] == 'download' or \
                        logR['status'] == 'unzip':
                    self.genBtn.setText(logR['status'].title() + 'ing ..')

                # Error #
                elif logR['status'] == 'error':
                    self.genBtn.setVisible(False)
                    self.qprog.setVisible(False)
                    self.result.setText('* ERROR : Reached Download Limit *')
                    self.setWindowTitle(self.SD.obj)
                    self.SD.clear()
                    self.genStart = False

                # Filter #
                elif logR['status'] == 'filter':
                    # Pretty Precentage #
                    percentage = round(logR['percent'], 2)
                    if len(str(logR['total'])) > 5:
                        percentage = round(logR['percent'], 3)
                    elif len(str(logR['total'])) > 6:
                        percentage = round(logR['percent'], 4)

                    # Result Progress Format and Percentage #
                    self.qprog.setVisible(True)
                    self.qprog.setValue(percentage)
                    resultT = 'Progress: {} % | Total: {} | Added: {}'.format(percentage,
                                                                              logR['total'],
                                                                              logR['add'])
                    # Progress in Button & Titlebar #
                    self.genBtn.setText('Filtering ...')
                    self.result.setText(resultT)
                    self.setWindowTitle('{} ({}%)'.format(self.SD.obj, percentage))
                    self.genStart = [
                        percentage,
                        logR['total'],
                        logR['add']
                    ]

        # Complete #
        if self.genStart and \
                (os.path.isdir(DirSep(self.SD.tmpObj)) is False or \
                 os.path.isfile(DirSep(self.SD.desktop + 'spamips.txt'))):
            self.qprog.setVisible(False)
            self.genBtn.setText('Job Complete')
            self.genBtn.setStyleSheet(self.finishBtnStyle)
            r = 'Total: {} | Added: {}'.format(self.genStart[1], self.genStart[2])
            self.result.setText(r)
            self.setWindowTitle(self.SD.obj)
            self.rpTim.stop()

    # == Close App == #
    def closeEvent(self, QCloseEvent):
        self.genBtn.setVisible(False)
        self.qprog.setVisible(False)
        self.result.setText('* STOPPED *')
        self.setWindowTitle(self.SD.obj)
        # Kill Parent & Child Process #
        for p in self.procs:
            if p.pid != os.getpid() and p.is_alive():
                p.terminate()
        try:
            os.killpg(os.getpid(), signal.SIGTERM)
        except:
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
        sys.exit()
