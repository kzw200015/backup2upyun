#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from config import *
from progressbar import Percentage, FileTransferSpeed, Bar, ETA, ProgressBar
import upyun
import tarfile
import os
import shutil


class ProgressBarHandler(object):
    def __init__(self, totalsize, params):
        widgets = [params, Percentage(), ' ', Bar(marker='=', left='[', right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
        self.pbar = ProgressBar(widgets=widgets, maxval=totalsize).start()

    def update(self, readsofar):
        self.pbar.update(readsofar)

    def finish(self):
        self.pbar.finish()


current_backup = backup_mark + '-' + (datetime.now()).strftime('%Y-%m-%d') + '.tar.gz'
outdated_backup = backup_mark + '-' + (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') + '.tar.gz'

with tarfile.open(current_backup, 'w:gz') as tf:

    for each_database in backup_database:
        print('dumping database [{}]...'.format(each_database))
        os.system('mysqldump -h{} --default-character-set={}  -u{} -p{} {} > {}.sql'.format(mysql_host, mysql_charset[each_database], mysql_user, mysql_passwd, each_database, each_database))
        print('taring sql file [{}]...'.format(each_database + '.sql'))
        tf.add(each_database + '.sql')
        os.remove(each_database + '.sql')

    for each_dir in backup_dir:
        print('taring dir [{}]'.format(each_dir))
        tarFileName = shutil.make_archive(each_dir, 'gztar', root_dir=backup_pre_dir, base_dir=each_dir)
        tf.add(tarFileName, os.path.basename(tarFileName))
        os.remove(tarFileName)

up = upyun.UpYun(service_name, operator_user, operator_passwd)

with open(current_backup, 'rb') as f:
    res = up.put(current_backup, f, checksum=True, handler=ProgressBarHandler, params="uploading ")

print('deleting outdated backup...')

try:
    up.delete(outdated_backup)
except Exception as e:
    print('delete failed' + '\n' + str(e))

print('cleaning temp files...')

os.remove(current_backup)

print('done!')
