import requests
import time
import re
import pymysql
from lxml import etree
from Config.Config import *
from Predict.Predict import Predict
from Lib.Logger import Logger
logger = Logger('Register')


class register(object):

    def __init__(self):
        # 获取随机邮件地址
        self.get_mail_address_url = "https://10minutemail.net/"
        # 获取邮件列表地址
        self.get_mail_list_url = "https://10minutemail.net/mailbox.ajax.php?_=" + str(time.time())
        # openlaw cookies初始化地址
        self.init_url = "http://openlaw.cn/register.jsp"
        # openlaw 获取验证码图片地址
        self.kaptcha_url = "http://openlaw.cn/Kaptcha.jpg?v=" + str(time.time())
        # openlaw注册地址
        self.register_url = "http://openlaw.cn/service/rest/us.User/collection/register"
        # openlaw注册的POST数据包
        self.data = {
            "_csrf": "",
            "email": "",
            "userName": "",  # 和邮箱相同
            "nickName": "",  # 默认去除@后面的内容
            "password": "",
            "validateCode": "",
            "agree": "forever"
        }
        # openlaw注册的headers参数
        self.header = {
            "Referer": "http://openlaw.cn/register.jsp",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }
        self.db = ""
        if database == "mysql":
            self.db = pymysql.connect(database_host,database_username,database_password,database_db )

    # 获取随机邮箱
    def get_email_address(self):
        rsp = requests.get(self.get_mail_address_url)
        cookies = rsp.cookies
        rsp = etree.HTML(rsp.text)
        email_address = rsp.xpath('//*[@id="fe_text"]/@value')[0]
        return email_address, cookies

    # 获取邮件列表
    def get_mail_list(self, cookies):
        rsp = requests.get(self.get_mail_list_url, cookies=cookies)
        return rsp.text

    # 检查是否有openlaw的注册邮件发送过来
    def check_email(self, content):
        if "Openlaw系统邮件" in content:
            return True
        else:
            return False

    # 读出openlaw的激活邮件地址
    def get_active_link(self, content, cookies):
        pat = re.compile('<a href="(.*?)">您的账号已申请成功，请激活', re.S)
        link = pat.findall(content)[0]
        url = self.get_mail_address_url + link
        rsp = requests.get(url=url, cookies=cookies).text
        pat = re.compile('<p>请点击下面的链接激活您的帐号，完成注册<br /><a href="(.*?)">')
        link = pat.findall(rsp)[0]
        rsp = requests.get(link)
        return rsp.text

    # 检查openlaw账号是否成功激活
    def check_account_active(self, content):
        if '激活成功!' in content:
            return True
        else:
            return False

    # 在openlaw上申请注册
    def register_in_openlaw(self, email):
        s = requests.session()
        # 初始化cookies
        init_page = s.get(self.init_url)
        init_page = etree.HTML(init_page.text)
        csrf = init_page.xpath('//*[@id="form-signup"]/input/@value')[0]
        nick_name = email.split("@")[0]
        # 获取验证码图片
        kaptcha = s.get(self.kaptcha_url).content
        predict = Predict()
        validateCode = predict.run(kaptcha)
        register_param = self.data
        register_param['_csrf'] = csrf
        register_param['email'] = email
        register_param['userName'] = email
        register_param['nickName'] = nick_name
        register_param['password'] = 'openlawClawer520'
        register_param['validateCode'] = validateCode
        rsp = s.post(self.register_url, data=register_param, headers=self.header)
        return rsp

    def save_to_Database(self, email):
        self.cursor = self.db.cursor()
        sql = "insert into account(username, password)values('{}','{}')".format(email, "openlawClawer520")
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except:
            # 如果发生错误则回滚
            self.db.rollback()


if __name__ == '__main__':
    reg = register()
    email, cookies = reg.get_email_address()
    logger.info("获得随机邮箱：" + email)
    reg.register_in_openlaw(email)
    rsp = reg.get_mail_list(cookies)
    logger.info("等待接收激活邮件")
    flag = True
    if reg.check_email(rsp):
        flag = False
    while flag:
        rsp = reg.get_mail_list(cookies)
        if reg.check_email(rsp):
            flag = False
        else:
            logger.info("等待接收激活邮件")
        time.sleep(5)
    rsp = reg.get_active_link(rsp, cookies)
    is_active = reg.check_account_active(rsp)
    if is_active:
        logger.info("激活成功，您的账号信息为:\r\n用户名:" + email + "\r\n密码为:openlawClawer520")