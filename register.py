import requests
from lxml import etree

if __name__ == '__main__':
    rsp = requests.get("https://10minutemail.net/").text
    rsp = etree.HTML(rsp)
    print(rsp.xpath('//*[@id="fe_text"]/@value')[0])