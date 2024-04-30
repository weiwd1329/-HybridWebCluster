#-*- coding:utf-8 -*-

import TaskCfg
import datetime
import Lobby
import Config
import Action
from proto.general_pb2 import *
import MessageCfg
import json

def InitTaskCfg(userid):
    now = datetime.date.today()
    datestr = now.strftime("%Y_%m_%d")
    strKey = TaskCfg.KEY_TASK.format(userid = userid, date = datestr)
    taskinfo = {}
    for id in TaskCfg.TASK_LIST:
        if id in TaskCfg.TASK_CFG:
            cfg = TaskCfg.TASK_CFG[id]
            taskinfo['count_' + str(id)] = 0
            taskinfo['total_' + str(id)] = cfg['total']
            taskinfo['state_' + str(id)] = TaskCfg.STATE_NOT_FINISH
            # taskinfo['reward_' + str(id)] = json.dumps(cfg['rewardlist'])
    Config.grds.hset(strKey, mapping=taskinfo)
    

def GetTaskCfg(userid, version):
    task = TaskCfg.TASK_LIST
    tasklist = []
    now = datetime.date.today()
    datestr = now.strftime("%Y_%m_%d")
    strKey = TaskCfg.KEY_TASK.format(userid=userid, date=datestr)
    hasKey = Config.grds.exists(strKey)
    if not hasKey:
        InitTaskCfg(userid)
    for id in task:
        if id in TaskCfg.TASK_CFG:
            cfg = TaskCfg.TASK_CFG[id]
            if version < cfg['version']:
                continue
            taskdict = {
                'tid':cfg['tid'], 'type':cfg['type'], 'iconid':cfg['iconid'],
                'series':cfg['series'], 'name':cfg['name'], 'desc':cfg['desc'],
                'total':cfg['total'], 'version':cfg['version'],'rewardlist':cfg['rewardlist'],
                'count': 0, 'state': TaskCfg.STATE_INVALID,
            }

            if cfg['type'] == TaskCfg.TYPE_WEEK:
                datestr = Lobby.GetMonday(now)
            elif cfg['type'] == TaskCfg.TYPE_MONTH:
                datestr = str(now.year) + "_" + str(now.month) + "_1"
            elif cfg['type'] == TaskCfg.TYPE_YEAR:
                datestr = str(now.year) + "_1_1"
            strKey = TaskCfg.KEY_TASK.format(userid = userid, date = datestr)
            taskinfo = Config.grds.hgetall(strKey)
            if taskinfo:
                countfield = 'count_' + str(id)
                statefield = 'state_' + str(id)
                taskdict['count'] = taskinfo[countfield] if taskinfo.has_key(countfield) else 0
                taskdict['state'] = taskinfo[statefield] if taskinfo.has_key(statefield) else TaskCfg.STATE_INVALID
            tasklist.append(taskdict)
    return {'tasklist': tasklist}

def UserSign(userid, signtype, date):
    if signtype == TaskCfg.SIGN_TYPE_TODAY:
        date = datetime.datetime.today()
    else:
        date = datetime.datetime.strptime(str(date), '%Y_%m_%d')

    day = date.day
    date = date.strftime("%Y_%m_%d")
    strKey = TaskCfg.KEY_SIGN.format(userid = userid, date = date)
    Config.grds.setbit(strKey, day, 1)
    signproto = Sign()
    signproto.userid = int(userid)
    signproto.signtype = int(signtype)
    signproto.date = date
    Action.SendAction(userid, MessageCfg.MSGID_SIGN, signproto.SerializeToString())

def GetSignRecord(userid):
    date = datetime.date.today()
    strKey = TaskCfg.KEY_SIGN.format(userid=userid, date = date.strftime("%Y_%m_%d"))
    bitfield = Config.grds.bitfield(strKey, 'sat').get('u31', '1')
    signrecord = bitfield.execute()
    return signrecord[0]

def TaskReward(userid, taskid):
    pass