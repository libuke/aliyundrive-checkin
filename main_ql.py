import os
import re
from aliyundrive import Aliyundrive



def main():
    token_string = os.environ.get('refreshToken')
    token_string = token_string.split('&')

    ali = Aliyundrive()
    message_all = []

    for idx, token in enumerate(token_string):
        result = ali.aliyundrive_check_in(token)
        message_all.append(str(result))

        if idx < len(token_string) - 1:
            message_all.append('--')

    #TODO: 发送通知
    title = '阿里云盘签到结果'
    message_all = '\n'.join(message_all)
    message_all = re.sub('\n+', '\n', message_all).rstrip('\n')

    print(title)
    print(message_all)

    print('finish')


if __name__ == '__main__':
    main()
