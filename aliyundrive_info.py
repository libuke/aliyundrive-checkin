class AliyundriveInfo:
    def __init__(
            self, 
            success: bool, 
            user_name: str, 
            signin_count: int, 
            message: str, 
            reward_notice: str):
        self.success = success
        self.user_name = user_name
        self.signin_count = signin_count
        self.message = message
        self.reward_notice = reward_notice

    def __str__(self) -> str:
        message_all = ''
        if self.success:
            message_all = f'{self.user_name}：完成第{self.signin_count}次签到，{self.reward_notice}\n'
        else:
            message_all = f'签到失败，错误信息：{self.message}\n'

        return message_all