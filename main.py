#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import upyun
import os
from datetime import datetime, timedelta
from config import *


class backup2upyun(object):

    def __init__(self, service_name, operator_user, operator_passwd, backup_mark, backup_dir, backup_pre_dir, backup_database, mysql_host, mysql_user, mysql_passwd, mysql_charset):
        self.up = upyun.UpYun(service_name, operator_user, operator_passwd)
        self.backup_mark = backup_mark
        self.backup_dir = backup_dir
        self.backup_pre_dir = backup_pre_dir
        self.backup_database = backup_database
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_passwd = mysql_passwd
        self.mysql_charset = mysql_charset

    def __start(self):
        self.cwd = os.getcwd()
        self.old_key = self.backup_mark + '-' + \
            (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') + '.zip'
        self.current_key = self.backup_mark + '-' + \
            (datetime.now()).strftime('%Y-%m-%d') + '.zip'
        self.local_file_path = os.path.join(
            self.backup_pre_dir, self.current_key)
        os.chdir(self.backup_pre_dir)

    def __tarFiles(self):
        for each_dir in self.backup_dir:
            os.system(' '.join(['zip -q -r', each_dir + '.zip', each_dir]))

    def __dumpMysql(self):
        for each_database in self.backup_database:
            os.system(' '.join(['mysqldump -h', self.mysql_host, '-u' + self.mysql_user,
                                '-p' + self.mysql_passwd, '--default-character-set=' + self.mysql_charset[each_database], each_database, '>', each_database + '.sql']))

    def __uploadFile(self):
        os.system(' '.join(['zip -q -r', self.current_key, '*.zip *.sql']))
        with open(self.local_file_path, 'rb') as f:
            self.up.put(self.current_key, f, checksum=True)

    def __end(self):
        try:
            self.up.delete(self.old_key)
        except Exception as e:
            print('删除旧备份失败，可能是由于不存在旧备份\n错误信息：' + str(e))
        os.system('rm -rf *.zip *.sql')
        os.chdir(self.cwd)

    def do(self):
        self.__start()
        print('正在打包文件')
        self.__tarFiles()
        self.__dumpMysql()
        print('正在上传')
        self.__uploadFile()
        print('正在删除临时文件以及旧备份')
        self.__end()


if __name__ == '__main__':
    bak = backup2upyun(service_name, operator_user, operator_passwd, backup_mark,
                       backup_dir, backup_pre_dir, backup_database, mysql_host, mysql_user, mysql_passwd, mysql_charset)
    bak.do()
