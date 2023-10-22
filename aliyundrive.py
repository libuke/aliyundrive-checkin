import pytz
import requests
import datetime
from aliyundrive_info import AliyundriveInfo
from tenacity import retry, stop_after_attempt, wait_random, RetryError

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
            reward_notice='',
            task_notice=''
        )

        def handle_error(error_message: str) -> AliyundriveInfo:
            info.message = error_message
            return info

        try:
            flag, user_name, access_token, message = self._get_access_token(token)
            if not flag:
                return handle_error(f'get_access_token error: {message}')

            flag, signin_count, message = self._check_in(access_token)
            if not flag:
                return handle_error(f'check_in error: {message}')

            flag, message = self._get_reward(access_token, signin_count)
            if not flag:
                return handle_error(f'get_reward error: {message}')

            flag, message, reward_notice, task_notice = self._get_task(access_token)
            if not flag:
                return handle_error(f'get_task error: {message}')

            info.success = True
            info.user_name = user_name
            info.signin_count = signin_count
            info.reward_notice = reward_notice
            info.task_notice = task_notice

            return info

        except RetryError as e:
            return handle_error(f'Unexpected error occurred: {str(e)}')

    """
    获取access_token

    :param token: 阿里云盘token
    :return tuple[0]: 是否成功请求token
    :return tuple[1]: 用户名
    :return tuple[2]: access_token
    :return tuple[3]: message
    """

    @retry(stop=stop_after_attempt(10), wait=wait_random(min=5, max=30))
    def _get_access_token(self, token: str) -> tuple[bool, str, str, str]:
        url = 'https://auth.aliyundrive.com/v2/account/token'
        payload = {'grant_type': 'refresh_token', 'refresh_token': token}

        response = requests.post(url, json=payload, timeout=5)
        data = response.json()

        if 'code' in data and data['code'] in ['RefreshTokenExpired', 'InvalidParameter.RefreshToken']:
            return False, '', '', data['message']

        nick_name, user_name = data['nick_name'], data['user_name']
        name = nick_name if nick_name else user_name
        access_token = data['access_token']
        return True, name, access_token, ''

    """
    执行签到操作

    :param token: 调用_get_access_token方法返回的access_token
    :return tuple[0]: 是否成功
    :return tuple[1]: 签到次数
    :return tuple[2]: message
    """

    @retry(stop=stop_after_attempt(10), wait=wait_random(min=5, max=30))
    def _check_in(self, access_token: str) -> tuple[bool, int, str]:
        url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
        payload = {'isReward': False}
        params = {'_rx-s': 'mobile'}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.post(url, json=payload, params=params, headers=headers, timeout=5)
        data = response.json()

        if 'success' not in data:
            return False, -1, data['message']

        success = data['success']
        signin_count = data['result']['signInCount']

        return success, signin_count, ''

    """
    获得奖励

    :param token: 调用_get_access_token方法返回的access_token
    :param sign_day: 领取第几天
    :return tuple[0]: 是否成功
    :return tuple[1]: message
    """

    @retry(stop=stop_after_attempt(10), wait=wait_random(min=5, max=30))
    def _get_reward(self, access_token: str, sign_day: int) -> tuple[bool, str]:
        url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
        payload = {'signInDay': sign_day}
        params = {'_rx-s': 'mobile'}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.post(url, json=payload, params=params, headers=headers, timeout=5)
        data = response.json()

        if 'result' not in data:
            return False, data['message']

        success = data['success']
        return success, ''

    """
    今日奖励/任务

    :param token: 调用_get_access_token方法返回的access_token
    :return tuple[0]: 是否成功
    :return tuple[1]: message
    :return tuple[2]: 奖励信息
    :return tuple[3]: 任务信息
    """

    @retry(stop=stop_after_attempt(10), wait=wait_random(min=10, max=30))
    def _get_task(self, access_token: str) -> tuple[bool, str]:
        url = 'https://member.aliyundrive.com/v2/activity/sign_in_list'
        payload = {}
        params = {'_rx-s': 'mobile'}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.post(url, json=payload, params=params, headers=headers, timeout=5)
        data = response.json()

        if 'result' not in data:
            return False, data['message']

        success = data['success']
        signInInfos = data['result']['signInInfos']

        shanghai_timezone = pytz.timezone('Asia/Shanghai')
        current_datetime = datetime.datetime.now(shanghai_timezone)
        day = current_datetime.day

        rewards = filter(lambda info: int(info.get('day', 0)) == day, signInInfos)
        
        award_notice = ''
        task_notice = ''

        for reward in next(rewards)['rewards']:
            name = reward['name']
            remind = reward['remind']
            type = reward['type']

            if type == "dailySignIn":
                award_notice = name
            if type == "dailyTask":
                task_notice = f'{remind}（{name}）'
        return success, '', award_notice, task_notice
