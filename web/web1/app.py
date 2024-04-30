#-*- coding:utf-8 -*-

import web
import json
import Config
import Error
import ErrorCfg
import Account
import logging
import logging.config
import Shop
import Lobby
import Task
#导入web.py

#为了使用非调试模式下的session
#session在调试模式下不能正常工作，因为session于调试模式下的重调用相冲突（比如可能会在一次对接口的访问中同时访问两次）
web.config.debug = False

#url映射
urls = (
    '/', 'hello',
    '/register', 'register',
    '/login', 'login',
    '/shop/cfg', 'shop_cfg',
    '/shop/buy', 'shop_buy',
    '/task/cfg', 'task_cfg',
    '/task/reward', 'task_reward',
    '/sign', 'sign',
    '/sign/record', 'sign_record',
    '/mail/send', 'mail_send',
    '/mail/list', 'mail_list',
    '/mail/detail', 'mail_detail',
    '/mail/getattach', 'mail_getattach',
    '/mail/delete', 'mail_delete',
    '/mail/delete/all', 'mail_delete_all',
)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('webpy')
# logging.basicConfig(
#         level=logging.DEBUG,#控制台打印的日志级别
#         filename='log/webpy.log',
#         filemode='a',#模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
#         #a是追加模式，默认如果不写的话，就是追加模式
#         format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'#日志格式
#     )

# session = requests.Session()
app = web.application(urls, globals())
application = app.wsgifunc()

#避免二次创建session，使得session可以在调试模式下正常使用
if web.config.get('_session') is None:
    #initializer参数决定了session初始化的值
    #web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count': 0})
    session = web.session.Session(app, web.session.DiskStore('sessions'))
    session._config.__dict__['ignore_expiry'] = False
    session._config.__dict__['timeout'] = 2 * 60 * 60
    web.config._session = session
else:
    session = web.config._session

#还可以使用数据库对session进行存储
# db = web.database(dbn='', db='', user='', pw='')
# store = web.session.DBStore(db, 'sessions') DBStore被创建需要两个参数，db对象和session的表名
# session = web.session.Session(app, store, initializer={'count': 0})


#装饰器
#由于函数也是一个对象，而且函数对象可以被赋值给变量，所以通过变量也能调用函数
#假设我们要增强函数的功能，比如在函数调用前后自动打印日志，对函数捕获异常等，但又不希望修改函数的定义
#这种在代码运行期间动态增加功能的方式，称之为装饰器
def CatchError(func):
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as e:
            logger.exception(e)
    return wrapper

def CheckLogin(func):
    def wrapper(*args, **kw):
        if session.__dict__.has_key('userid'):
            return func(*args, **kw)
        else:
            return Error.ErrResult(ErrorCfg.EC_LOGIN_INVALID, ErrorCfg.ER_LOGIN_INVALID)
    return wrapper

#和url映射中同名的类，也就是根据url映射到具体的类中处理
class hello:
    def GET(self):
        req = web.input(name='')
        userid = 123456
        strKey = Config.KEY_PACKAGE.format(userid=userid)
        info = {
            'test1': 1,
            'test2': 2,
        }
        Config.grds.hmset(strKey, info)
        name = req.name
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'
    
class login:
    @CatchError
    def POST(self):
        req = web.input(userid = '', password = '')
        userid = req.userid
        password = req.password
        result = Account.VerifyAccount(userid, password)
        if result['code'] != 0:
            return Error.ErrResult(result['code'], result['reason'])
        result = Account.HandleLogin(session, userid)
        if result['code'] != 0:
            return Error.ErrResult(result['code'], result['reason'])
        return json.dumps({'code': 0})
    
class register:
    @CatchError
    def POST(self):
        req = web.input(phonenum = '', password = '', nick = '', sex = '1', idcard = '')
        #logger.info(self.__class__ + req)
        phonenum = req.phonenum
        password = req.password
        nick = req.nick
        sex = req.sex
        idcard = req.idcard

        #检测手机号格式
        if not Account.CheckPhonenum(phonenum):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_PHONENUM_TYPE_ERROR, ErrorCfg.ER_REGISTER_PHONENUM_TYPE_ERROR)

        #检测账号重复
        if not Account.CheckUserIdNotRepeat(phonenum):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_USERID_REPEAT, ErrorCfg.ER_REGISTER_USERID_REPEAT)
        
        #检测身份证号格式
        if not Account.CheckIdCard(idcard):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_IDCARD_ERROR, ErrorCfg.ER_REGISTER_IDCARD_ERROR)

        #检测密码格式
        if not Account.CheckPassword(password):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_PASSWORD_ERROR, ErrorCfg.ER_REGISTER_PASSWORD_ERROR)

        #注册账号
        Account.InitUser(phonenum,password,nick,sex,idcard)
        return json.dumps({'code':0})

class shop_cfg:
    @CatchError
    @CheckLogin
    def GET(self):
        req = web.input(version = "10000")
        version = int(req.version)
        shopcfg = Shop.GetShopCfg(version)
        return json.dumps({'code': 0, 'shopcfg': shopcfg})

class shop_buy:
    @CatchError
    @CheckLogin
    def POST(self):#处理POST请求
        req = web.input(userid = '', propid = '', shopversion = '', version = '')
        userid = int(req.userid)
        propid = int(req.propid)
        shopversion = int(req.shopversion)
        version = int(req.version)
        dictInfo = Shop.ShopBuy(userid, propid, shopversion, version)
        return json.dumps(dictInfo)
    
class task_cfg:
    @CatchError
    @CheckLogin
    def GET(self):
        req = web.input(userid = '', version = '')
        userid = req.userid
        version = req.version
        taskcfg = Task.GetTaskCfg(userid, version)
        return json.dumps({'code': 0, 'taskcfg': taskcfg})
    
class sign:
    @CatchError
    @CheckLogin
    def POST(self):
        req = web.input(userid = '', signtype = '0', date = '')
        userid = int(req.userid)
        signtype = int(req.signtype)
        date = req.date
        Task.UserSign(userid, signtype, date)
        return json.dumps({'code': 0})
    
class task_reward:
    @CatchError
    @CheckLogin
    def POST(self):
        req = web.input(userid = '', taskid = '')
        
    
class sign_record:
    @CatchError
    @CheckLogin
    def GET(self):
        req = web.input(userid = '')
        userid = req.userid
        signrecord = Task.GetSignRecord(userid)
        return json.dumps({'code': 0, 'signrecord': signrecord})

class mail_send:
    @CatchError
    @CheckLogin
    def POST(self):
        req = web.input(
            useridlist = [], title = '', context = '', type = Config.MAILTYPE_SYSTEM,
            attach = {}, isglobal = 0, fromuserid = 0, buttontext = Config.MAILBUTTON_DEFAULT,
        )
        Lobby.SendMail(req)
        return json.dumps({'code': 0})
    
class mail_list:
    @CatchError
    @CheckLogin
    def GET(self):
        req = web.input(userid = '')
        userid = int(req.userid)
        mailinfolist = Lobby.GetMailList(userid)
        return json.dumps({'code': 0, 'mailinfolist': mailinfolist})
    
class mail_detail:
    @CatchError
    @CheckLogin
    def GET(self):
        req = web.input(mailid = '')
        mailid = req.mailid
        dictInfo = Lobby.GetMailDetail(mailid)
        return json.dumps(dictInfo)

class mail_getattach:
    @CatchError
    @CheckLogin
    def POST(self):
        req = web.input(userid = '', mailid = '')
        

class mail_delete:
    @CatchError
    @CheckLogin
    def POST(self):
        req = web.input(userid = '', mailid = '')
        userid = int(req.userid)
        mailid = req.mailid
        Lobby.MailDelete(userid, mailid)
        return json.dumps({'code': 0})

class mail_delete_all:
    @CatchError
    @CheckLogin
    def POST(self):
        req = web.input(userid = '')
        dictInfo = Lobby.DeleteAllMail(req.userid)
        return json.dumps(dictInfo)




# if __name__ == "__main__":
#     app.run()#启用web应用