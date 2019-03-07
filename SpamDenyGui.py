#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SpamDenyLib import *

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
        self.icon = self.SD.root + 'icon.ico'
        self.winWidth = 400
        self.winHeight = 200
        self.winTop = 50
        self.winLeft = 50
        self.nameBtnStyle = 'font-size: 14px; color: #444444; font-weight: bold;'
        self.projdBtnStyle = 'font-size: 12px; color: #666666; font-weight: bold;'
        self.dwCheckBtnStyle = 'font-size: 14px; color: #444444; font-weight: bold;'
        self.addLocalBtnStyle = 'font-size: 14px; color: #444444; border: 0; font-weight: bold;'
        self.genBtnStyle = 'font-size: 14px; font-weight: bold; color: #ffffff; border: 2px solid #111111; background: #333333;'
        self.finishBtnStyle = 'font-size: 14px; font-weight: bold; color: #000000; border: 2px solid #00ff00; background: #00ff00;'
        self.resultStyle = 'font-size: 15px; font-weight: bold; color: #000000; border: 0; background: transparent;'
        self.dwCheck = None
        self.addFile = None
        self.result = None
        self.genBtn = None
        self.genStart = False

        # == Init Body & Show Window == #
        self.win_init()
        self.win_body()
        self.show()

    # == Init Window == #
    def win_init(self):
        self.setWindowIcon(QIcon(DirSep(self.icon)))
        self.setWindowTitle(self.SD.obj)
        self.setFixedSize(self.winWidth, self.winHeight)
        self.move(self.winLeft, self.winTop)

    # == Win Body == #
    def win_body(self):
        # Logo #
        logo = QLabel(self)
        logo.setPixmap(QPixmap(DirSep(self.icon)))
        logo.setGeometry(-10, -10, 120, 120)

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

        # Download Checkbox #
        self.dwCheck = QCheckBox(' Download Database', self)
        self.dwCheck.setStyleSheet(self.dwCheckBtnStyle)
        self.dwCheck.setGeometry(230, 20, 160, 20)
        self.dwCheck.setChecked(True)

        # File Picker Button #
        self.addFile = QPushButton('+ Local Database', self)
        self.addFile.setStyleSheet(self.addLocalBtnStyle)
        self.addFile.setGeometry(230, 60, 160, 20)
        self.addFile.clicked.connect(self.openFilePicker)

        # Generate Button #
        self.genBtn = QPushButton('Generate', self)
        self.genBtn.setStyleSheet(self.genBtnStyle)
        self.genBtn.setGeometry(230, 110, 160, 30)
        self.genBtn.clicked.connect(self.doGen)

        # Result #
        self.result = QLabel(self)
        self.result.setStyleSheet(self.resultStyle)
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setGeometry(5, 160, 390, 40)

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
        self.genBtn.setText('Processing ...')

        # Check Empty #
        if len(self.SD.local) < 1 and \
                self.dwCheck.isChecked() is False:
            self.result.setText('Database is empty')
            return

        # Disable Buttons #
        self.genBtn.disconnect()
        self.addFile.disconnect()
        self.dwCheck.setDisabled(True)

        # Download if checked #
        if self.dwCheck.isChecked():
            self.SD.download()

        # Start Filtering Process #
        fp = Process(target = self.SD.filter)
        fp.start()

    # == Result Progress == #
    def resultProgress(self):
        # Progress Feedback #
        if os.path.isfile(DirSep(self.SD.tmpObj + '/process.json')):
            logR = self.SD.file_read(DirSep(self.SD.tmpObj + '/process.json'))
            if len(logR) > 9:
                logR = json.loads(logR)
                resultT = 'Progress: {} % | Total: {} | Added: {}'.format(logR['percent'], logR['total'], logR['add'])
                self.result.setText(resultT)
                self.setWindowTitle('{} ({}%)'.format(self.SD.obj, round(logR['percent'])))
                self.genStart = [
                    logR['total'],
                    logR['add']
                ]

        # Complete #
        if self.genStart and os.path.isdir(DirSep(self.SD.tmpObj)) is False:
            self.genBtn.setText('Complete')
            self.genBtn.setStyleSheet(self.finishBtnStyle)
            r = 'Total: {} | Added: {}'.format(self.genStart[0], self.genStart[1])
            self.result.setText(r)
            self.setWindowTitle(self.SD.obj)
