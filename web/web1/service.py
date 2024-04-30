#-*- coding:utf-8 -*-s
# 基于传输层TCP/IP协议接口socket实现的TCP发送json格式数据功能-测试客户端-短连接
from socket import *
import time
from proto.message_pb2 import *
import Config
import struct

def SendSvrd(host, port, info):
    if not info:
        print('error not info')
        return 
    # 基础参数(这里填写要发送到的服务端地址端口)
    
    #BUFSIZ = 2048
    ADDR = (host, port)

    # 创建socket
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    # 试图连接到服务端
    tcpCliSock.connect(ADDR)

    if not info:
        print('error')

    # 消息头封装为字节流
    print(len(info))
    buf = struct.pack(">cccccccci", b'H', b'R', b'P', b'C', chr(1), b'\0', b'\0', b'\0', len(info)) + info

    # 客户端发送给服务端
    # print(info)
    tcpCliSock.send(buf)
    # data_receive = tcpCliSock.recv(BUFSIZ)
    # if not data_receive:
    #     print('error')
    # print('[client]: {}'.format(data_receive.decode('utf-8')))

    # 一次短连接,三次握手结束,任何一方都可以发起close
    tcpCliSock.close()



# calc1 = CalcParam()
# calc2 = CalcParam()
# calc1.num = 1
# calc2.num = 2
# reqproto = Request()
# reqproto.id = 1
# reqproto.method = 'add'
# reqproto.params.append(calc1.SerializeToString())
# reqproto.params.append(calc2.SerializeToString())
# reqproto.SerializeToString()

