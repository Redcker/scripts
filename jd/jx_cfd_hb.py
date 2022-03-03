import json
import datetime
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

logger = logging.getLogger()
fh = logging.FileHandler('cfd.log', encoding='utf-8')
formatter = logging.Formatter("%(asctime)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.INFO)
with open('cfd_config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.loads(f.read())
token = CONFIG['pushplus_token']
cookie = CONFIG['cookie']
advance_time = CONFIG['advance_time']
offset_time = 0.01


def send_to_wechat(title):
    data = {
        'title': f'财富岛红包状态：{title}',
        'content': '请按照状态提示进行对应操作',
        'token': token,
    }
    url = 'http://www.pushplus.plus/send'
    requests.post(url, data=data)


def get_next_time():
    now_time = datetime.datetime.now()
    str_time = (now_time + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")
    timestamp = int(datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S").timestamp())
    return timestamp


class JxCFD(object):
    def __init__(self, cookie):
        self.cookie = cookie
        self.session = requests.session()
        self.session.headers = {
            'referer': 'https://st.jingxi.com/',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'cookie': self.cookie
        }

    def get_cfd_url(self):
        url = 'https://m.jingxi.com/jxbfd/user/ExchangeState?strZone=jxbfd&dwType=2&sceneval=2&g_login_type=1'
        ret = self.session.get(url).json()
        dwLvl = ret['hongbao'][0]['dwLvl']
        pool = ret['hongbaopool']
        new_url = f'https://m.jingxi.com/jxbfd/user/ExchangePrize?strZone=jxbfd&dwType=3&dwLvl={dwLvl}&ddwPaperMoney=100000&strPoolName={pool}&sceneval=2&g_login_type=1'
        return new_url

    def exchange_red_package(self):
        cfd_url = self.get_cfd_url()
        while datetime.datetime.now().timestamp() < (next_timestamp + advance_time):  # 未到时间，无限循环
            pass
        ret = self.session.get(cfd_url).json()
        if ret['iRet'] == 0:
            title = '抢到了'
        else:
            title = ret['sErrMsg']
        logging.info(f"抢购结果：{title}")
        ret_code = ret['iRet']
        if ret_code in [2013, 2016]:  # 抢早或者抢迟不推送至微信
            if ret_code == 2013:  # 迟了
                new_advance_time = advance_time + offset_time
            else:  # 早了
                new_advance_time = advance_time - offset_time
            CONFIG['advance_time'] = new_advance_time
            with open('cfd_config.json', 'w', encoding='utf-8') as fp:  # 更新配置
                json.dump(CONFIG, fp, indent=2)
        else:
            send_to_wechat(title=title)


if __name__ == '__main__':
    next_timestamp = get_next_time()
    jx_cfd = JxCFD(cookie)
    scheduler = BlockingScheduler()
    scheduler.add_job(func=jx_cfd.exchange_red_package, trigger='cron', minute=59, id='jx_cfd',
                      timezone='Asia/Shanghai')
    scheduler.start()
