## 财富岛抢购脚本使用方法

***首先需要一台具有Python3.7+环境的服务器 / 个人计算机 / 其他设备***

### 拉取脚本

```shell
git clone https://github.com/Redcker/scripts.git
```

### 进入jd文件夹

```shell
cd scripts/jd
```

### 安装依赖

```shell
pip install -r requirements.txt
```

### 填写配置

若配置了pushplus_token，在抢购状态异常或者抢购成功会推送提醒

目前仅支持单账号，原因是同一IP同时发多个请求会被阻断，可在多个服务器部署或者使用代理实现多账号并发

***advance_time是请求提前多久发送，会自动优化，尽量不要手动修改***

cookie的格式为pt_key=''

填完配置后，检查是否符合json格式

### 运行脚本

若为Linux系统，可后台挂起

```shell
nohup python3 jx_cfd_hb.py >/dev/null 2>&1 &
```

若为windows，直接运行脚本，然后小化窗口即可

### 查看日志

日志文件在脚本同目录下的cfd.log中

### 停止脚本

先查看进程号

```shell
ps -aux | grep 'python3 jx_cfd_hb.py'
```

第一行，第二列有一串数字，就是进程号 

用进程号替换掉下方的PID即可停止脚本

```shell
kill -9 PID
```





