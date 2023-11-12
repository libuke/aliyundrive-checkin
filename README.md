# aliyundrive-checkin
- aliyundrive-checkin是一个定时自动签到的python程序
- 2023/11/12: 增加对青龙面板的支持 [[@lelemka0](https://github.com/lelemka0)]
- 2023/11/09: 修复漏签时出现的问题 [[@cibimo](https://github.com/cibimo)]
- 2023/10/22: 调整网络请求失败重试次数、重试间隔时间，减小签到失败的概率
- 2023/08/10: 推送支持微信应用图文消息、消息代理，支持获取每日任务 [[@thsrite](https://github.com/thsrite)]
- 2023/08/02: 采用linux构建，外加飞书推送支持 [[@bequt](https://github.com/bequt)]
- 2023/06/12: 增加requests出错重试，使用chatgpt优化代码结构
- 2023/05/17: 增加自动领取签到奖励，显示本月签到次数

## 说明
- 脚本还无法自动完成任务，只能领取签到奖励

# 如何使用？ 
## Github Action
1. Fork项目到自己的仓库
2. 点击Settings -> 点击选项卡 Secrets and variables -> 点击Actions -> New repository secret


    | Name   | Secret                           |
    | ------ | ------------------------------- |
    | TOKEN *   | 阿里云盘Token 可以添加多个用英文逗号(,)分割 无需空格  |
    | SCKEY  | Server酱 推送密钥 |
    | PUSHPLUS_TOKEN  | pushplus 推送Token |
    | WECOM_TOKENS  | 企业微信 Token |
    | WECOM_WEBHOOK  | 企业微信 WEBHOOK |
    | BARK_DEVICEKEY  | IOS应用Bark 推送密钥 |
    | FEISHU_DEVICEKEY  | 飞书 推送密钥 |

以上TOKEN为阿里云盘签到必填项 推送项选择其中一个即可 也可多渠道推送

3. 点击Actions -> 选择aliyundrive-checkin -> 点击Run workflow 运行即可

## 青龙面板
1. 使用以下参数添加订阅

    | 项     | 值                              |
    | ------ | ------------------------------- |
    | 链接 | "--recursive https://github.com/libuke/aliyundrive-checkin.git" |
    | 分支 | main |
    | 白名单 | main_ql.py |
    | 依赖文件 | ".py$\|qlapi" |
  
   注: recursive不是青龙支持的方法，仅在2.16.5上测试

2. 添加环境变量
  
    从[mrabit/aliyundriveDailyCheck](https://github.com/mrabit/aliyundriveDailyCheck)迁移无需任何变量修改
    - refreshToken*: 阿里云盘Token
      - 可添加多个refreshToken
    - CLIENT_ID: 青龙应用ID
    - CLIENT_SECRET: 青龙应用SECRET
    - 权限至少包含`环境变量`

3. 设置喜欢的脚本运行时间，开始使用

## 其它设置
- 需要调整推送内容修改aliyundrive_info.py文件即可
- 自动签到时间修改.github/workflows/checkin.yml文件 cron项即可实现
  - 该cron指定的是格林尼治时间（UTC），如果需要换算成北京时间，要在该cron的基础上增加八小时得到北京时间。

## 如何获取阿里云盘TOKEN？
- [https://alist.nn.ci/zh/guide/drivers/aliyundrive.html](https://alist.nn.ci/zh/guide/drivers/aliyundrive.html)

# 如侵权请联系本人删除
