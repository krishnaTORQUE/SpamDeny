#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import tempfile
import re
import json
import requests
import zipfile


# OS Directory Separator #
def DirSep(path):
    return path.replace('/', os.sep).replace('\\', os.sep)


# == Main Class == #
class SpamDeny:
    def __init__(self):
        #
        # == IP Database == #
        self.ips = {
            # IPv4 #
            'v4': [
                'https://www.stopforumspam.com/downloads/toxic_ip_cidr.txt',
                'https://www.stopforumspam.com/downloads/bannedips.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_1.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_7.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_30.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_90.zip'
            ],
            # Ipv6 #
            'v6': [
                'https://www.stopforumspam.com/downloads/listed_ip_1_ipv6.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_7_ipv6.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_30_ipv6.zip',
                'https://www.stopforumspam.com/downloads/listed_ip_90_ipv6.zip'
            ]
        }

        # == Constants == #
        self.root = os.path.dirname(os.path.realpath(__file__)) + '/'
        self.tmp = tempfile.gettempdir() + '/'
        self.desktop = os.path.normpath(os.path.expanduser("~/Desktop")) + '/'
        self.projectUrl = 'https://github.com/krishnaTORQUE/SpamDeny'
        self.obj = __class__.__name__
        self.version = 1.2
        self.status = 'Beta'
        self.tmpObj = self.tmp + self.obj
        self.stdOut = True
        self.local = []

        # == Check Temp Directory == #
        self.clear()
        os.makedirs(DirSep(self.tmpObj))
        os.makedirs(DirSep(self.tmpObj + '/D'))
        os.makedirs(DirSep(self.tmpObj + '/F'))

    # == Get File Name == #
    def file_name(self, file):
        return file.split('/')[-1]

    # == File Read == #
    def file_read(self, file):
        data = ''
        file = open(file, 'r')
        for line in file:
            data += line
        return data

    # == File Write == #
    def file_write(self, file, content):
        file = open(file, 'w')
        file.write(content)
        file.close()

    # == Download ZIP == #
    def down_zip(self, url):
        r = requests.get(url)
        with open(DirSep(self.tmpObj + '/D/' + self.file_name(url)), 'wb') as z:
            z.write(r.content)

    # == Unzip Download Zip File == #
    def down_unzip(self, file):
        zip_ref = zipfile.ZipFile(file, 'r')
        zip_ref.extractall(DirSep(self.tmpObj + '/F/'))
        zip_ref.close()
        os.remove(file)

    # == Ips Download == #
    def download(self):
        # Print to Console #
        if self.stdOut:
            print('\nDownloading ...')
        #
        # Ip list Loop #
        for k, v in self.ips.items():
            #
            # Ip Version Loop #
            for ipv in v:
                fname = self.file_name(ipv)
                if re.search(r'\.txt', ipv, flags = re.I | re.S):
                    # TXT File #
                    data = requests.get(ipv).text
                    self.file_write(DirSep(self.tmpObj + '/F/' + fname), data)

                else:
                    # ZIP File #
                    self.down_zip(ipv)
                    self.down_unzip(DirSep(self.tmpObj + '/D/' + fname))

    # == Filter & Make == #
    def filter(self):
        ip_lst = ''
        count = 0
        add = []
        txt = ''
        nginx = ''
        apache = ''
        logD = {}

        # Search #
        search_v4 = [
            r'[\r\n|\r|\n|\t| |,]',
            r'[^0-9.\n]'
        ]
        search_v6 = [
            r'[\r|\n|\r\n|\t| |,|\.]',
            r'[^a-z0-9:\n]'
        ]

        # Replace #
        replace = [r'\n', '']

        files = os.listdir(DirSep(self.tmpObj + '/F'))

        # From Local #
        for l in self.local:
            ip_lst += self.file_read(l)

        # From Download #
        for f in files:
            ip_lst += self.file_read(DirSep(self.tmpObj + '/F/' + f))
            os.remove(DirSep(self.tmpObj + '/F/' + f))

        ###
        ip_lst = re.split(r'\n', ip_lst.strip(), flags = re.I | re.S)
        total = len(ip_lst)

        # Filtering #
        for ip in ip_lst:
            ip = re.sub(r'\/.*', '', ip)
            new = None

            # Valid IP #
            if len(ip) > 4:
                if re.search(r':', ip, flags = re.I | re.S):
                    # IPv6 #
                    for sr in range(0, len(search_v4)):
                        new = re.sub(search_v6[sr], replace[sr], ip)

                else:
                    # IPv4 #
                    for sr in range(0, len(search_v6)):
                        new = re.sub(search_v4[sr], replace[sr], ip)

            #
            # Add / Marge
            # Filter Duplicate
            #
            if new is not None and \
                    new not in add and \
                    len(new) > 4:
                add.append(new)
                txt += new + '\n'
                nginx += 'deny ' + new + ';\n'
                apache += 'deny from ' + new + '\n'

            # Status #
            percent = round((count / total) * 100, 4)
            if percent > 99.1:
                percent = 100

            logD['percent'] = percent
            logD['total'] = total
            logD['add'] = len(add)
            self.file_write(DirSep(self.tmpObj + '/process.json'), json.dumps(logD))

            # Print to Console #
            if self.stdOut:
                os.system('clear')
                print('Progress: {} % | Total: {} | Added: {}'.format(logD['percent'], logD['total'], logD['add']))

            count += 1

        # Save Text File #
        self.file_write(DirSep(self.desktop + 'spamips.txt'), txt)

        # Save Nginx Config #
        self.file_write(DirSep(self.desktop + 'blockips.conf'), nginx)

        # Save Apache Config #
        apache = 'order allow,deny\n' + apache + 'allow from all'
        self.file_write(DirSep(self.desktop + 'denyips.conf'), apache)

        # Clear #
        self.clear(False)

    # == Clear Temp == #
    def clear(self, gen = True):
        # Check Temp Directory #
        if os.path.isdir(DirSep(self.tmpObj)):
            shutil.rmtree(DirSep(self.tmpObj))

        # Clean Generate Files #
        if gen and \
                os.path.isfile(DirSep(self.desktop + 'spamips.txt')):
            os.remove(DirSep(self.desktop + 'spamips.txt'))
            os.remove(DirSep(self.desktop + 'blockips.conf'))
            os.remove(DirSep(self.desktop + 'denyips.conf'))
