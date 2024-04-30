#-*- coding:utf-8 -*-s
import json

def ErrResult(code, reason):
    return json.dumps({'code':code, 'reason':reason})