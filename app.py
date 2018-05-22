#!/usr/bin/env python
# coding=utf-8

"""

@author: sml2h3

@license: (C) Copyright 2017-2018

@contact: sml2h3@gmail.com

@software: easyprice

@file: main.py

@time: 2018/4/24 上午11:58
"""
import os
from celery import Celery
# 实例化一个Celery
app = Celery("shopper")
# 读取配置文件并批量配置
app.config_from_object("conf.celery")


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == '__main__':
    app.start()