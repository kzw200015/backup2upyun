#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from config import *
import upyun
import zipfile
import os
from datetime import datetime, timedelta

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

print('uploading...')
with open(current_backup, 'rb') as f:
    res = up.put(current_backup, f, checksum=True)

print('deleting outdated backup...')
try:
    up.delete(outdated_backup)
except Exception as e:
    print('delete failed' + '\n' + str(e))

print('cleaning temp files...')
os.remove(current_backup)

print('done!')
