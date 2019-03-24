# -*- coding: utf-8 -*-

import os

run = '''
pip install --upgrade --user PyQt5 requests pywin32
pip freeze --local > list.txt
pip install --upgrade -r list.txt
rm ./list.txt
'''

os.system(run)
