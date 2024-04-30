#-*- coding:utf-8 -*-

import ActionCfg
import Config
from proto.message_pb2 import Message

def SendAction(userid, msgid, protoinfo):
    strKey = ActionCfg.KEY_ACTION_LIST
    msg = Message()
    msg.userid = userid
    msg.msgid = msgid
    msg.string = protoinfo
    Config.grds.rpush(strKey, msg.SerializeToString())