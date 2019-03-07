#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SpamDenyGui import *

# Start Gui #
if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    win = Win()

    # == Result Display Timer == #
    rpTim = QTimer()
    rpTim.timeout.connect(win.resultProgress)
    rpTim.setInterval(100)
    rpTim.start()

    sys.exit(qapp.exec_())
