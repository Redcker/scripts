import logging
import datetime
import json

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    import requests
    import pytz
except Exception as e:
    logging.error(f'依赖导入错误：{e}')
    exit(1)


def send_to_wechat(title):
    """
    微信推送
    """
    data = {
        'title': f'财富岛红包状态：{title}',
        'content': '请按照状态提示进行对应操作',
        'token': token,
    }
    url = 'http://www.pushplus.plus/send'
    requests.post(url, data=data)


def get_next_time():
    """
    获取下一个整点的时间戳
    """
    now_time = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    str_time = (now_time + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")
    timestamp = int(datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S").timestamp())
    return timestamp


class JxCFD(object):
    def __init__(self, cookie):
        """
        初始化财富岛类
        """
        self.cookie = cookie
        self.session = requests.session()
        self.session.headers = {
            "Host": "m.jingxi.com",
            "Accept": "*/*",
            "Connection": "keep-alive",
            'referer': 'https://st.jingxi.com/fortune_island/index2.html?ptag=7155.9.47&sceneval=2&sid=6f488e2778fa2db09a39f105577da07w',
            'user-agent': f'jdpingou;android;5.21.4;appBuild/20596;session/332;pap/JA2019_3111789;ef/1;',
            'cookie': self.cookie,
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }

    def get_cfd_url(self):
        """
        获取最新100红包url
        """
        url = 'https://m.jingxi.com/jxbfd/user/ExchangeState?strZone=jxbfd&dwType=2&sceneval=2&g_login_type=1'
        ret = self.session.get(url).json()
        try:
            pool = ret['hongbaopool']
        except KeyError:
            logging.error('获取最新url失败，可能是cookie已过期')
            send_to_wechat('cookie已失效')
            return
        else:
            dwLvl = ret['hongbao'][0]['dwLvl']
            new_url = f'https://m.jingxi.com/jxbfd/user/ExchangePrize?strZone=jxbfd&dwType=3&dwLvl={dwLvl}&ddwPaperMoney=100000&strPoolName={pool}&sceneval=2&g_login_type=1'
        return new_url

    def exchange_red_package(self):
        """
        兑换红包
        """
        cfd_url = self.get_cfd_url()
        if not cfd_url:
            return
        time_delta = next_timestamp - advance_time
        while datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).timestamp() < time_delta:  # 未到时间，无限循环
            pass
        try:
            start_time = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
            logging.info(f'开始请求，当前时间为：{start_time.strftime("%Y-%m-%d %H:%M:%S:%f")}')
            ret = self.session.get(cfd_url).json()
            spend_time = datetime.datetime.now(
                tz=pytz.timezone('Asia/Shanghai')).timestamp() - start_time.timestamp()  # 请求花费时间
        except requests.exceptions.JSONDecodeError:
            logging.error('cookie认证失败，请不要担心，这个是偶发情况。此次请求停止，等待下次请求')
            return
        if ret['iRet'] == 0:
            title = '抢到了'
        else:
            title = ret['sErrMsg']
        logging.info(f"抢购结果：{title}")
        ret_code = ret['iRet']
        if ret_code in [2013, 2016]:  # 抢早或者抢迟不推送至微信
            CONFIG['advance_time'] = spend_time
            with open('cfd_config.json', 'w', encoding='utf-8') as fp:  # 更新配置
                json.dump(CONFIG, fp, indent=2)
        else:
            send_to_wechat(title=title)


if __name__ == '__main__':
    logger = logging.getLogger()  # 日志配置
    fh = logging.FileHandler('cfd.log', encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    logging.getLogger('apscheduler').setLevel(logging.ERROR)  # 不输出apscheduler的非错误日志
    with open('cfd_config.json', 'r', encoding='utf-8') as f:
        try:
            CONFIG = json.load(f)  # 读取配置
        except json.decoder.JSONDecodeError:
            logging.error('配置读取错误，请检查配置文件格式是否正确')
            exit(1)
    token = CONFIG['pushplus_token']  # 读取pushplus token
    cookie = CONFIG['cookie']  # 读取token
    advance_time = CONFIG['advance_time']  # 提前时间
    next_timestamp = get_next_time()
    jx_cfd = JxCFD(cookie)
    scheduler = BlockingScheduler()
    try:
        scheduler.add_job(func=jx_cfd.exchange_red_package, trigger='cron', second=59, minute=59, id='jx_cfd',
                          timezone='Asia/Shanghai')
    except Exception as e:
        logging.error(f'启动定时任务失败，具体错误为：{e}')
    else:
        logging.info('定时脚本启动成功')
        scheduler.start()
