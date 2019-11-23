## 又拍云备份脚本

自动上传网站文件到又拍云，并删除三天前的旧备份

用python实现，需要依赖库`upyun`~~，以及用来打包的`zip`~~

## 食用方法

直接使用git clone整个库

`git clone https://github.com/kzw200015/backup2upyun.git`

安装 python 环境

`apt install -y python3`

进入脚本目录

`cd /root/backup2upyun`

安装依赖

`apt install -y python3-pip`

`pip3 install upyun`

把配置文件复制一份

`cp config.py.example config.py`

按照`config.py`内的说明进行配置

赋予执行权限

`chmod +x main.py`

执行脚本

`./main.py`

## 定时任务
用`cron`实现
执行`crontab -e`，加入以下内容
```
LANG='en_US.UTF-8'
LC_ALL='en_US.UTF-8'
0 2 * * * /root/backup2upyun/main.py
```
保存退出即可，这样每天凌晨两点就会自动执行一次任务
