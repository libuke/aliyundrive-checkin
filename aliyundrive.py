import json
import requests

from aliyundrive_info import AliyundriveInfo

def aliyundrive_check_in(token):
    token_url = 'https://auth.aliyundrive.com/v2/account/token'
    check_in_url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'

    result = AliyundriveInfo(success=True, user_name='', msg='签到成功')

    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        'grant_type': 'refresh_token',
        'refresh_token': token
    })
    req = requests.Session()
    resp = req.post(token_url, data=data, headers=headers).text
    token_resp_json = json.loads(resp)
    
    if ('code' in token_resp_json and token_resp_json['code'] == 'InvalidParameter.RefreshToken'):
        result.success = False
        result.msg = (token_resp_json['message'])
        return result

    result.user_name = token_resp_json['user_name']
    access_token = token_resp_json['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    resp = req.post(check_in_url, data=data, headers=headers)
    check_in_resp_json = json.loads(resp.text)
    result.success = check_in_resp_json['success']
    
    return result
