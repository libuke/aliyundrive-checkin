import requests
import json


class MessageSend:
    def __init__(self):
        self.sender = {}

        self.register("pushplus_token", self.pushplus)
        self.register("serverChan_token", self.serverChan)
        self.register("weCom_tokens", self.weCom)
        self.register("weCom_webhook", self.weCom_bot)
        self.register("bark_deviceKey", self.bark)
        self.register("feishu_deviceKey", self.feishu)

    def register(self, token_name, callback):
        assert token_name not in self.sender, "Register fails, the token name exists."
        self.sender[token_name] = callback

    def send_all(self, message_tokens, title, content):
        def check_valid_token(token):
            if isinstance(token, type(None)):
                return False
            if isinstance(token, str) and len(token) == 0:
                return False
            if isinstance(token, list) and (token.count(None) != 0 or token.count("") != 0):
                return False
            return True

        for token_key in message_tokens:
            token_value = message_tokens[token_key]
            if token_key in self.sender and check_valid_token(token_value):
                try:
                    ret = self.sender[token_key](token_value, title, content)
                except:
                    print(f"[Sender]Something wrong happened when handle {self.sender[token_key]}")

    def pushplus(self, token, title, content):
        assert type(token) == str, "Wrong type for pushplus token."
        content = content.replace("\n", "\n\n")
        payload = {
            'token': token,
            "title": title,
            "content": content,
            "channel": "wechat",
            "template": "markdown"
        }
        resp = requests.post("http://www.pushplus.plus/send", data=payload)
        resp_json = resp.json()
        if resp_json["code"] == 200:
            print(f"[Pushplus]Send message to Pushplus successfully.")
        if resp_json["code"] != 200:
            print(f"[Pushplus][Send Message Response]{resp.text}")
            return -1
        return 0

    def serverChan(self, sendkey, title, content):
        assert type(sendkey) == str, "Wrong type for serverChan token."
        content = content.replace("\n", "\n\n")
        payload = {
            "title": title,
            "desp": content,
        }
        resp = requests.post(f"https://sctapi.ftqq.com/{sendkey}.send", data=payload)
        resp_json = resp.json()
        if resp_json["code"] == 0:
            print(f"[ServerChan]Send message to ServerChan successfully.")
        if resp_json["code"] != 0:
            print(f"[ServerChan][Send Message Response]{resp.text}")
            return -1
        return 0

    def weCom(self, tokens, title, content):
        proxy_url = None
        to_user = None
        tokens = tokens.split(",")
        if len(tokens) == 3:
            weCom_corpId, weCom_corpSecret, weCom_agentId = tokens
        elif len(tokens) == 4:
            weCom_corpId, weCom_corpSecret, weCom_agentId, to_user = tokens
        elif len(tokens) == 5:
            weCom_corpId, weCom_corpSecret, weCom_agentId, to_user, proxy_url = tokens
        else:
            return -1

        qy_url = proxy_url or "https://qyapi.weixin.qq.com"
        get_token_url = f"{qy_url}/cgi-bin/gettoken?corpid={weCom_corpId}&corpsecret={weCom_corpSecret}"
        resp = requests.get(get_token_url)
        resp_json = resp.json()
        if resp_json["errcode"] != 0:
            print(f"[WeCom][Get Token Response]{resp.text}")
        access_token = resp_json.get('access_token')
        if access_token is None or len(access_token) == 0:
            return -1
        send_msg_url = f'{qy_url}/cgi-bin/message/send?access_token={access_token}'
        data = {
            "touser": to_user or "@all",
            "agentid": weCom_agentId,
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": content,
                        "picurl": "https://raw.githubusercontent.com/libuke/aliyundrive-checkin/main/aliyunpan.jpg",
                        "url": ''
                    }
                ]
            },
            "duplicate_check_interval": 600
        }
        resp = requests.post(send_msg_url, data=json.dumps(data))
        resp_json = resp.json()
        if resp_json["errcode"] == 0:
            print(f"[WeCom]Send message to WeCom successfully.")
        if resp_json["errcode"] != 0:
            print(f"[WeCom][Send Message Response]{resp.text}")
            return -1
        return 0

    def weCom_bot(self, webhook, title, content):
        assert type(webhook) == str, "Wrong type for WeCom webhook token."
        assert "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?" in webhook, "Please use the whole webhook url."
        headers = {
            'Content-Type': "application/json"
        }
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        resp = requests.post(webhook, headers=headers, data=json.dumps(data))
        resp_json = resp.json()
        if resp_json["errcode"] == 0:
            print(f"[WeCom]Send message to WeCom successfully.")
        if resp_json["errcode"] != 0:
            print(f"[WeCom][Send Message Response]{resp.text}")
            return -1
        return 0

    def bark(self, device_key, title, content):
        assert type(device_key) == str, "Wrong type for bark token."

        url = "https://api.day.app/push"
        headers = {
            "content-type": "application/json",
            "charset": "utf-8"
        }
        data = {
            "title": title,
            "body": content,
            "device_key": device_key
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data))
        resp_json = resp.json()
        if resp_json["code"] == 200:
            print(f"[Bark]Send message to Bark successfully.")
        if resp_json["code"] != 200:
            print(f"[Bark][Send Message Response]{resp.text}")
            return -1
        return 0

    def feishu(self, device_key, title, content):
        assert type(device_key) == str, "Wrong type for feishu token."

        url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{device_key}'
        headers = {
            "content-type": "application/json",
            "charset": "utf-8"
        }

        data = {"msg_type": "post", "content": {"post": {"zh_cn": {"title": title, "content": [[{"tag": "text", "text": content}]]}}}}

        resp = requests.post(url, headers=headers, json=data)
        resp_json = resp.json()
        if resp_json["code"] == 0:
            print(f"[Bark]Send message to Bark successfully.")
        if resp_json["code"] != 0:
            print(f"[Bark][Send Message Response]{resp.text}")
            return -1
        return 0
