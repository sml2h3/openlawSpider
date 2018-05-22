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
from Register import Register
from Lib.Logger import Logger
import time
logger = Logger("test.py")


reg = Register.register()
while True:
    email, cookies = reg.get_email_address()
    logger.info("获得随机邮箱：" + email)
    reg.register_in_openlaw(email)
    rsp = reg.get_mail_list(cookies)
    logger.info("等待接收激活邮件")
    flag = True
    count = 0
    if reg.check_email(rsp):
        flag = False
        count += 1
    while flag:
        if count > 10:
            break
        rsp = reg.get_mail_list(cookies)
        # if reg.check_email(rsp):
        #     flag = False
        # else:
        #     logger.info("等待接收激活邮件")
        #     count += 1
        logger.info("等待接收激活邮件")
        count += 1
        time.sleep(5)
    rsp = reg.get_active_link(rsp, cookies)
    is_active = reg.check_account_active(rsp)
    if is_active:
        logger.info("激活成功，您的账号信息为:\r\n用户名:" + email + "\r\n密码为:openlawClawer520")
        reg.save_to_Database(email)