#-*- coding:utf-8 -*-

import Config
import ActionCfg
from proto.message_pb2 import Message
import MessageCfg

def DistributeAction(actiontype, actionmsg):
    for strKey in ActionCfg.ACTION_MAPPING[actiontype]:
        print("actiontype: " + str(actiontype))
        print("rpush msg to: " + strKey)
        Config.grds.rpush(strKey, actionmsg)

def ActionMonitor():
    while True:
        res = Config.grds.blpop(ActionCfg.KEY_ACTION_LIST)[1]
        print("--------- start ---------")
        msg = Message()
        msg.ParseFromString(res)
        msgid = int(msg.msgid) & MessageCfg.MSGID
        print('msgid: ' + str(msgid))
        if msgid == MessageCfg.MSGID_SIGN:
            DistributeAction(ActionCfg.ACTION_SIGN, res)
        elif msgid == MessageCfg.MSGID_LOGIN:
            DistributeAction(ActionCfg.ACTION_LOGIN, res)
        print("---------- end ----------")


if __name__ == "__main__":
    ActionMonitor()