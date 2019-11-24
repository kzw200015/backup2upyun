#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from config import *
from progressbar import Percentage, FileTransferSpeed, Bar, ETA, ProgressBar
import upyun
import zipfile
import os


class ProgressBarHandler(object):
    def __init__(self, totalsize, params):
        widgets = [params, Percentage(), ' ', Bar(marker='=', left='[', right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
        self.pbar = ProgressBar(widgets=widgets, maxval=totalsize).start()

    def update(self, readsofar):
        self.pbar.update(readsofar)

    def finish(self):
        self.pbar.finish()


current_backup = backup_mark + '-' + (datetime.now()).strftime('%Y-%m-%d') + '.zip'
outdated_backup = backup_mark + '-' + (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') + '.zip'


with zipfile.ZipFile(current_backup, 'w') as zf:

    for each_database in backup_database:
        print('dumping database[{}]...'.format(each_database))
        os.system('mysqldump -h{} --default-character-set={}  -u{} -p{} {} > {}.sql'.format(mysql_host, mysql_charset[each_database], mysql_user, mysql_passwd, each_database, each_database))
        print('taring sql file[{}]...'.format(each_database + '.sql'))
        zf.write(each_database + '.sql', compress_type=zipfile.ZIP_DEFLATED)
        print('cleaning temp sql file[{}]...'.format(each_database + '.sql'))
        os.remove(each_database + '.sql')

    for each_dir in backup_dir:
        print('taring dir[{}]'.format(each_dir))
        for root, dirs, files in os.walk(os.path.join(backup_pre_dir, each_dir)):
            for name in files:
                zf.write(os.path.join(root, name), os.path.join(root, name).replace(backup_pre_dir, ''), compress_type=zipfile.ZIP_DEFLATED)

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
