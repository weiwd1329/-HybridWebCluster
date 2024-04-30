#-*- coding:utf-8 -*-
import web
import redis

USER_STATUS_NOLMAL = 0
USER_STATUS_FREEZE = 1

MAIL_HOST = '127.0.0.1'
MAIL_PORT = 1234

DB_HOST = '192.168.0.173'
DB_PORT = 3306
DB_USER = 'cjx'
DB_PW = '123456'
DB_NAME = 'game_test'

RDS_HOST = '127.0.0.1'
RDS_PORT = 6379
RDS_PW = '123456'

gdb = web.database(
    dbn='mysql', 
    host=DB_HOST, 
    port=DB_PORT,
    user=DB_USER, 
    pw=DB_PW, 
    db=DB_NAME
)

grds = redis.Redis(
    host=RDS_HOST,
    port=RDS_PORT,
    password=RDS_PW
)
#账号
DEFAULT_SECPASSWORD = '123456'
KEY_PACKAGE = "KEY_PACKAGE_{userid}"
NEWUSER_MONEY_DEFAULT = 10000

MONEY_ID = 800
COIN_ID = 900

#邮件
MAILTYPE_SYSTEM = 1
MAILTYPE_ACTIVITY = 2
MAILTYPE_OPERATION = 3
MAILBUTTON_DEFAULT = "确认"
KEY_MAIL_LIST = "KEY_MAIL_LIST_{userid}"
KEY_MAIL_DETAIL = "KEY_MAIL_DETAIL_{mailid}"
