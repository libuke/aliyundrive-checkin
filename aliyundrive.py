import json
import requests

from aliyundrive_info import AliyundriveInfo


class Aliyundrive:
    """
    阿里云盘签到（自动领取奖励）

    :param token: 阿里云盘token
    :return AliyundriveInfo: 
    """
    def aliyundrive_check_in(self, token: str) -> AliyundriveInfo:
        info = AliyundriveInfo(
                success=False, 
                user_name='', 
                signin_count=-1, 
                message='', 
                reward_notice='')

        flag, user_name, access_token, message = self._get_access_token(token)
        
        if not flag:
            info.message = f'get_access_token error: {message}'
            return info
        
        flag, signin_count, message = self._check_in(access_token)
        if not flag:
            info.message = f'check_in error: {message}'
            return info
        
        flag, message = self._get_reward(access_token, signin_count)
        if not flag:
            info.message = f'get_reward error: {message}'
            return info
        
        info.success = True
        info.user_name = user_name
        info.signin_count = signin_count
        info.reward_notice = message
        return info
        
    """
    获取access_token

    :param token: 阿里云盘token
    :return tuple[0]: 是否成功请求token
    :return tuple[1]: 用户名
    :return tuple[2]: access_token
    :return tuple[3]: message
    """
    def _get_access_token(self, token: str) -> tuple[bool, str, str, str]:
        data = requests.post(
            url='https://auth.aliyundrive.com/v2/account/token', 
            json={ 'grant_type': 'refresh_token', 'refresh_token': token }
        ).json()

        if ('code' in data and data['code'] in [
            'RefreshTokenExpired', 
            'InvalidParameter.RefreshToken'
        ]):
            return False, '', '', data['message']
        
        
        nick_name, user_name = data['nick_name'], data['user_name']
        name = nick_name if nick_name else user_name
        access_token = data['access_token']
        return True, name, access_token, '成功获取access_token'
    
    """
    执行签到操作

    :param token: 调用_get_access_token方法返回的access_token
    :return tuple[0]: 是否成功
    :return tuple[1]: 签到次数
    :return tuple[2]: message
    """
    def _check_in(self, access_token: str) -> tuple[bool, int, str]:
        data = requests.post(
            url='https://member.aliyundrive.com/v1/activity/sign_in_list',
            json={ 'isReward': False },
            params={ '_rx-s': 'mobile' },
            headers={ 'Authorization': f'Bearer {access_token}' }
        ).json()
  
        if 'success' not in data:
            return False, -1, data['message']
        
        success = data['success']
        signin_count = data['result']['signInCount']

        return success, signin_count, '签到成功'
    
    """
    获得奖励

    :param token: 调用_get_access_token方法返回的access_token
    :param sign_day: 领取第几天
    :return tuple[0]: 是否成功
    :return tuple[1]: message 奖励信息或者出错信息
    """
    def _get_reward(self, access_token: str, sign_day: int) -> tuple[bool, str]:
        data = requests.post(
            url='https://member.aliyundrive.com/v1/activity/sign_in_reward',
            json={ 'signInDay': sign_day },
            params={ '_rx-s': 'mobile' },
            headers={ 'Authorization': f'Bearer {access_token}' }
        ).json()

        if 'result' not in data:
            return False, data['message']
        
        success = data['success']
        notice = data['result']['notice']
        return success, notice
