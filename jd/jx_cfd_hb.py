"""
cron: 50 59 * * * *
new Env('财富岛兑换红包 - By Redcker');
"""
import datetime
from jd.ql_api import get_envs, post_envs, delete_envs

try:
    import requests
    import pytz
except Exception as e:
    print(f'依赖导入错误：{e}')
    exit(1)


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
            'user-agent': 'jdpingou;android;5.21.4;appBuild/20596;session/332;pap/JA2019_3111789;ef/1;',
            'cookie': self.cookie['value'],
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
        except (KeyError, IndexError):
            print('获取最新url失败，可能是cookie过期或黑号')
            print('获取最新url失败，可能是cookie过期或黑号')
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
        while datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).timestamp() < (
                next_timestamp - float(advance_time['value'])):  # 未到时间，无限循环
            pass
        try:
            start_time = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).timestamp()
            ret = self.session.get(cfd_url).json()
            spend_time = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).timestamp() - start_time  # 请求花费时间
        except requests.exceptions.JSONDecodeError:
            print('cookie认证失败，请不要担心，这个是偶发情况。此次请求停止，等待下次请求')
            return
        if ret['iRet'] == 0:
            title = '抢到了'
        else:
            title = ret['sErrMsg']
        print(f"抢购结果：{title}")
        ret_code = ret['iRet']
        delete_envs([advance_time['id']])
        post_envs('CFD_ADVANCE_TIME', str(spend_time), '财富岛提前多久执行，请勿手动修改')
        if ret_code in [2013, 2016]:  # 抢早或者抢迟不推送至微信
            delete_envs([advance_time['id']])
            post_envs('CFD_ADVANCE_TIME', str(spend_time), '财富岛提前多久执行，请勿手动修改')


if __name__ == '__main__':
    advance_time = get_envs('CFD_ADVANCE_TIME')
    if len(advance_time) > 0:
        advance_time = advance_time[0]
    else:
        advance_time = 0.20
        ret = post_envs('CFD_ADVANCE_TIME', str(advance_time), '财富岛提前多久执行，请勿手动修改')
        advance_time = ret
    cookie = get_envs('CFD_HB_COOKIE')
    if len(cookie) > 0:
        cookie = cookie[0]
    else:
        print('请先添加环境变量CFD_HB_COOKIE,内容为待抢账号的cookie')
        exit(0)
    next_timestamp = get_next_time()
    jx_cfd = JxCFD(cookie)
    jx_cfd.exchange_red_package()
