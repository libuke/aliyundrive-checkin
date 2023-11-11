import os
import re
from aliyundrive import Aliyundrive
from qlapi.src.qlapi import qlenv

QINGLONG_HOST = "127.0.0.1"
QINGLONG_PORT = 5700
QINGLONG_ENV_NAME = "refreshToken"
QINGLONG_ENV_SPLIT = "&"

class Entry:
    def __init__(self):
        self.instance = None
        self._CLIENT_ID = os.environ.get('CLIENT_ID')
        self._CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        self._qinglong_login()
    
    def _qinglong_login(self):
        if (self._CLIENT_ID is not None) and (self._CLIENT_SECRET is not None):
            try:
                self.instance = qlenv(
                    url             = QINGLONG_HOST,
                    #Maybe a typo in api
                    post            = QINGLONG_PORT,
                    client_id       = self._CLIENT_ID,
                    client_secret   = self._CLIENT_SECRET,
                )
            except:
                print("QingLong login failed. Please check.")
    
    def getTokens(self):
        if self.instance is not None:
            try:
                allenv = self.instance.list()['data']
            except:
                print("List all env failed. Fallback to os.environ.")
                return self._getToken_osEnv()
            
            tokens = {}
            for item in allenv:
                if item['name'] == QINGLONG_ENV_NAME and item['status'] == 0:
                    tokens[item['value']] = {
                        "id": item['id'],
                        "remarks": item['remarks'],
                    }
            return tokens
        else:
            return self._getToken_osEnv()
    
    def updateToken(self, detail):
        if self.instance is None:
            print("instance is not initialized, skip to update.")
            return False
        try:
            result = self.instance.update(
                id      = detail['id'],
                name    = QINGLONG_ENV_NAME,
                value   = detail['newRefreshToken'],
                remarks = detail['remarks']
            )
            if result['code'] == 200:
                return True
            return False
        except:
            print(f"Update env {detail['id']}:{detail['remarks']} failed.")

    def _getToken_osEnv(self):
        print("!!! Use os.environ, automatic update function is not available.")
        token_string = os.environ.get(QINGLONG_ENV_NAME)
        return dict.fromkeys(token_string.split(QINGLONG_ENV_SPLIT))

def main():
    ali = Aliyundrive()
    message_all = []
    qinglong = Entry()

    tokens = qinglong.getTokens()
    for idx, token in enumerate(tokens):
        result = ali.aliyundrive_check_in(token)
        message_all.append(str(result))

        tokens[token].update({
            "newRefreshToken": result.refresh_token
        })
        message_all.append('自动更新token: ' + str(qinglong.updateToken(tokens[token])))

        if idx < len(tokens) - 1:
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
