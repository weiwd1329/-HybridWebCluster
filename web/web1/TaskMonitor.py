#-*- coding:utf-8 -*-

import Config
import ActionCfg
import MessageCfg
import TaskCfg
from proto.message_pb2 import Message
from proto.general_pb2 import Sign

def TaskMonitor():
    while True:
        res = Config.grds.blpop(ActionCfg.KEY_ACTION_TASK_LIST)[1]
        msg = Message()
        msg.ParseFromString(res)
        msgid = int(msg.msgid) & MessageCfg.MSGID
        if msgid == MessageCfg.MSGID_SIGN:
            signinfo = Sign()
            signinfo.ParseFromString(msg.string)
            userid = int(signinfo.userid)
            date = signinfo.date
            print(userid)
            print(date)
            strKey = TaskCfg.KEY_TASK.format(userid=userid, date=date)
            for id in TaskCfg.TASK_LIST:
                taskinfo = TaskCfg.TASK_CFG[id]
                if taskinfo['action'] == ActionCfg.ACTION_SIGN:
                    countfield = 'count_' + str(id)
                    totalfield = 'total_' + str(id)
                    statefield = 'state_' + str(id)
                    count = Config.grds.hincrby(strKey, countfield, 1)
                    result = Config.grds.hmget(strKey, statefield, totalfield)
                    state = int(result[0])
                    total = int(result[1])
                    print(result)
                    if count >= total and state == TaskCfg.STATE_NOT_FINISH:
                        Config.grds.hset(strKey, statefield, TaskCfg.STATE_FINISH)
                        #通知客户端
                        #每周任务
                        #任务领奖接口
        elif msgid == MessageCfg.MSGID_LOGIN:
            pass

if __name__ == "__main__":
    TaskMonitor()