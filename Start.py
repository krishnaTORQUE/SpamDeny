# -*- coding: utf-8 -*-

from SpamDenyGui import *

# Start Gui #
if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    win = Win()

    # == Result Display Timer == #
    win.rpTim = QTimer()
    win.rpTim.timeout.connect(win.resultProgress)
    win.rpTim.setInterval(1)
    win.rpTim.start()

    sys.exit(qapp.exec_())
