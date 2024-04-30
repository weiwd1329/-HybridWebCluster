#-*- coding:utf-8 -*-
import Config
import datetime
from proto.general_pb2 import Mail
import ShopCfg
import json
import ErrorCfg
import service
import base64

def GetMoney(userid):
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    money = 0
    if Config.grds.exists(strKey):
        money = int(Config.grds.hget(strKey, 'money'))
    return money

def GetMonday(today):
    today = datetime.datetime.strptime(str(today), "%Y-%m-%d")
    return datetime.datetime.strftime(today - datetime.timedelta(today.weekday()), "%Y_%m_%d")

def SendMail(mailinfo):
    if not mailinfo:
        return 
    
    #校验
    #封装消息
    mailproto = Mail()
    for userid in mailinfo['useridlist']:
        mailproto.userid.append(userid)
    mailproto.title = mailinfo['title']
    mailproto.context = mailinfo['context']
    mailproto.type = mailinfo['type']
    attach = {}
    for propid, propnum in mailinfo['attach'].items():
        if int(propid) in ShopCfg.SHOP_LIST:
            attach[propid] = propnum
    mailproto.attach = json.dumps(attach)
    mailproto.buttontext = base64.b64encode(mailinfo['buttontext'])
    if mailinfo['attach']:
        mailproto.hasattach = 1
    else:
        mailproto.hasattach = 0
    mailproto.getattach = 0

    service.SendSvrd(Config.MAIL_HOST, Config.MAIL_PORT, mailproto.SerializeToString())

def GetGlobalMail(userid):
    #1.全服邮件列表中获取邮件id
    #2.获取最后一次登录时间
    #3.遍历id，获取邮件信息，比较最后一次登录时间
    #4. 如果最后一次登录时间 小于 全服邮件发送时间 发送全服邮件给该用户
    pass

def GetMailList(userid):
    GetGlobalMail(userid)
    strKeylist = Config.KEY_MAIL_LIST.format(userid=userid)
    mailidlist = Config.grds.lrange(strKeylist, 0, -1)
    mailinfolist = []
    for mailid in mailidlist:
        strKey = Config.KEY_MAIL_DETAIL.format(mailid = mailid)
        #优化为hmget
        result = Config.grds.hgetall(strKey)
        # 可以优化为获取部分数据，因为邮件列表中仅需要展示部分信息
        if not result:
            Config.grds.lrem(strKeylist, mailid, 0)
            continue
        mailinfo = dict()
        mailinfo['mailid'] = mailid
        mailinfo['title'] = result['title']
        mailinfo['type'] = result['type']
        mailinfo['getattach'] = result['getattach']
        mailinfolist.append(mailinfo)
    return mailinfolist

def GetMailDetail(mailid):
    strKey = Config.KEY_MAIL_DETAIL.format(mailid = mailid)
    result = Config.grds.hgetall(strKey)
    if not result:
        return {'code': ErrorCfg.EC_MAIL_NOT_EXISTS, 'reason': ErrorCfg.ER_MAIL_NOT_EXISTS}
    mailinfo = dict()
    mailinfo['mailid'] = mailid
    mailinfo['title'] = result['title']
    mailinfo['context'] = result['context']
    mailinfo['type'] = result['type']
    mailinfo['attach'] = result['attach']
    mailinfo['buttontext'] = result['buttontext']
    mailinfo['hasattach'] = result['hasattach']
    mailinfo['getattach'] = result['getattach']
    return {'code': 0, 'mailinfo': mailinfo}

def GetMailAttach(userid, mailid):
    strKey = Config.KEY_MAIL_DETAIL.format(mailid = mailid)
    

def MailDelete(userid, mailid):
    strKeylist = Config.KEY_MAIL_LIST.format(userid=userid)
    # 优化：如果发现这封邮件有附件且未领取则不删除
    Config.grds.lrem(strKeylist, mailid, 0)
    strKey = Config.KEY_MAIL_DETAIL.format(mailid = mailid)
    Config.grds.delete(strKey)

def DeleteAllMail(userid, mailid):
    strKeylist = Config.KEY_MAIL_LIST.format(userid=userid)
    mailidlist = Config.grds.lrange(strKeylist, 0, -1)
    for mailid in mailidlist:
        Config.grds.lrem(strKeylist, mailid, 0)
        # 优化：如果发现这封邮件(有附件且未领取/未读)则不删除
        strKey = Config.KEY_MAIL_DETAIL.format(mailid = mailid)
        Config.grds.delete(strKey)
    return {'code': 0}

def GetMonday(today):
    today = datetime.datetime.strptime(str(today), "%Y-%m-%d")
    print(today)
    return datetime.datetime.strftime(today - datetime.timedelta(today.weekday()), "%Y_%m_%d")

# mailinfo = dict()
# mailinfo['useridlist'] = [123456]
# mailinfo['title'] = 'test'
# mailinfo['context'] = 'context'
# mailinfo['type'] = Config.MAILTYPE_SYSTEM
# mailinfo['attach'] = {'1001':5, '1002':10}
# mailinfo['buttontext'] = Config.MAILBUTTON_DEFAULT
# mailinfo['hasattach'] = 1
# mailinfo['getattach'] = 0
# SendMail(mailinfo)