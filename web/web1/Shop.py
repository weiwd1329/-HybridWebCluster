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
    #判断商城版本号
    if shopversion < ShopCfg.SHOP_VERSION:
        return {'code': ErrorCfg.EC_SHOP_VERSION_LOW, 'reason': ErrorCfg.ER_SHOP_VERSION_LOW}
    
    #判断道具是否存在
    if not propid in ShopCfg.SHOP_CFG:
        return {'code': ErrorCfg.EC_SHOP_PROP_NOT_EXIST, 'reason': ErrorCfg.ER_SHOP_PROP_NOT_EXIST}
    
    #获取道具配置
    cfg = ShopCfg.SHOP_CFG[propid]
    if version < cfg['version']:
        return {'code': ErrorCfg.EC_SHOP_CLIENT_VERSION_LOW, 'result': ErrorCfg.ER_SHOP_CLIENT_VERSION_LOW}
    #计算实际所需金额
    needmoney = int(math.floor(cfg['money'] * cfg['discount']))

    #获取用户余额
    money = Lobby.GetMoney(userid)

    #判断余额是否足够
    if money < needmoney:
        return {'code': ErrorCfg.EC_SHOP_MONEY_NOT_ENOUGH, 'reason': ErrorCfg.ER_SHOP_MONEY_NOE_ENOUGH}
    
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    money = Config.grds.hincrby(strKey, 'money', -needmoney)
    if money < 0:
        Config.grds.hincrby(strKey, 'money', needmoney)
        return {'code': ErrorCfg.EC_SHOP_MONEY_NOE_ENOUGH, 'reason': ErrorCfg.ER_SHOP_MONEY_NOE_ENOUGH}
    
    #刷新更新时间
    now = datetime.datetime.now()
    Config.grds.hset(strKey, 'freshtime', str(now))

    #更新数据库money
    DBManage.UpdateMoney(userid, money, now)

    #发货
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