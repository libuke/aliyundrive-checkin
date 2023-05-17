import os
import re
import argparse

from message_send import MessageSend
from aliyundrive import Aliyundrive

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token_string', type=str, required=True)

    args= parser.parse_args()
    token_string = args.token_string
    pushplus_token = os.environ.get('PUSHPLUS_TOKEN', None)
    serverChan_sendkey = os.environ.get('SERVERCHAN_SENDKEY', None)
    weCom_webhook = os.environ.get('WECOM_WEBHOOK', None)
    bark_deviceKey = os.environ.get('BARK_DEVICEKEY', None)

    message_tokens = {
        'pushplus_token': pushplus_token,
        'serverChan_token': serverChan_sendkey,
        'weCom_webhook': weCom_webhook,
        'bark_deviceKey': bark_deviceKey
    }

    message_send = MessageSend()
    message_all = ''
    token_string = token_string.split(',')
    ali = Aliyundrive()

    for idx, token in enumerate(token_string):
        result = ali.aliyundrive_check_in(token)
        message_all = f'{message_all}(token {idx+1}){result}'

    title = '阿里云盘签到结果'
    message_all = f'{title}\n{message_all}'
    message_all = re.sub('\n+','\n', message_all)
    if message_all.endswith('\n'): message_all = message_all[:-1]

    message_send.send_all(message_tokens=message_tokens, title=title, content=message_all)

    print('finish')
