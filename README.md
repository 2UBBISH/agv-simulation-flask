# README

## 1. install requirements

```shell script
pip install -r requirements.txt

# 安装python-socketio时请注意，当python==3.6时，须安装5.0.4版本
# 具体见https://blog.csdn.net/zbaby77/article/details/117411026

```

## 2. make sure python version

```shell script
python=3.6
```

## 3. how to start?

* python agv_simulation_flask.py or deploy it to uwsgi webserver

* ##### python版本运行方法

  先运行Debug文件夹里的server.py,再运行agv_simulation_flask.py

  再visit http://localhost:5000就可以开始运行了

* ##### c++版本运行方法

  先运行c++ project文件夹里的c++agv.exe，再运行Debug文件夹里的server1.py,再运行agv_simulation_flask.py即可

#### 4、更新说明

- ##### c++
- 
（1）现在会根据发送过来的算法选择（选项为1，2，3）来使用不同的算法了

（2）新增了算法

algorithm1：cbs

algorithm2：ecbs

algorithm3：ecbs

