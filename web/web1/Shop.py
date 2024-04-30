#-*- coding:utf-8 -*-

import ShopCfg
import ErrorCfg
import Lobby
import math
import Config
import datetime
import DBManage

def GetShopCfg(version):
    shop = ShopCfg.SHOP_LIST
    shoplist = []
    for id in shop:
        if id in ShopCfg.SHOP_CFG:
            cfg = ShopCfg.SHOP_CFG[id]
            if version < cfg['version']:
                continue
            propdict = {
                'pid': cfg['pid'], 'ename': cfg['ename'], 'name': cfg['name'],
                'type': cfg['type'], 'money': cfg['money'], 'coin': cfg['coin'],
                'paytype': cfg['paytype'], 'iconid': cfg['iconid'], 'version': cfg['version'],
                'discount': cfg['discount'], 'inventory': cfg['inventory'], 'buylimittype': cfg['buylimittype'],
                'buylimitnum': cfg['buylimitnum'], 'proplist': cfg['proplist'],
            }
            shoplist.append(propdict)
    return {'shoplist': shoplist, 'shopversion': ShopCfg.SHOP_VERSION}

def ShopBuy(userid, propid, shopversion, version):
    #�ж��̳ǰ汾��
    if shopversion < ShopCfg.SHOP_VERSION:
        return {'code': ErrorCfg.EC_SHOP_VERSION_LOW, 'reason': ErrorCfg.ER_SHOP_VERSION_LOW}
    
    #�жϵ����Ƿ����
    if not propid in ShopCfg.SHOP_CFG:
        return {'code': ErrorCfg.EC_SHOP_PROP_NOT_EXIST, 'reason': ErrorCfg.ER_SHOP_PROP_NOT_EXIST}
    
    #��ȡ��������
    cfg = ShopCfg.SHOP_CFG[propid]
    if version < cfg['version']:
        return {'code': ErrorCfg.EC_SHOP_CLIENT_VERSION_LOW, 'result': ErrorCfg.ER_SHOP_CLIENT_VERSION_LOW}
    #����ʵ��������
    needmoney = int(math.floor(cfg['money'] * cfg['discount']))

    #��ȡ�û����
    money = Lobby.GetMoney(userid)

    #�ж�����Ƿ��㹻
    if money < needmoney:
        return {'code': ErrorCfg.EC_SHOP_MONEY_NOT_ENOUGH, 'reason': ErrorCfg.ER_SHOP_MONEY_NOE_ENOUGH}
    
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    money = Config.grds.hincrby(strKey, 'money', -needmoney)
    if money < 0:
        Config.grds.hincrby(strKey, 'money', needmoney)
        return {'code': ErrorCfg.EC_SHOP_MONEY_NOE_ENOUGH, 'reason': ErrorCfg.ER_SHOP_MONEY_NOE_ENOUGH}
    
    #ˢ�¸���ʱ��
    now = datetime.datetime.now()
    Config.grds.hset(strKey, 'freshtime', str(now))

    #�������ݿ�money
    DBManage.UpdateMoney(userid, money, now)

    #����
    PresentProp(userid, propid)
    return {'code': 0, 'money': money}

def PresentProp(userid, propid):
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    proplist = ShopCfg.SHOP_CFG[propid]['proplist']
    now = datetime.datetime.now()
    propdict = {}
    for prop in proplist:
        propid = "prop_" + str(prop['id'])
        propnum = Config.grds.hincrby(strKey, propid, prop['num'])
        propdict[propid] = propnum
    Config.grds.hset(strKey, 'freshtime', str(now))
    DBManage.UpdateProp(userid, propdict, now)