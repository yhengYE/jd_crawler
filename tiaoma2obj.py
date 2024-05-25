# coding=utf-8
import ddddocr
import requests
import json
import os
import time
import sys
import xlrd
import threading
import re
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup
import logging
import logging.handlers
'''
日志模块
'''
LOG_FILENAME = 'msg_seckill.log'
logger = logging.getLogger()

def set_logger():
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(process)d-%(threadName)s - '
                                  '%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

set_logger()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

path = os.path.abspath(os.path.dirname(sys.argv[0]))

# json化
def parse_json(s):
    begin = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[begin:end])

# 创建目录
def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        os.makedirs(path)
        logger.info(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        logger.info(path + ' 目录已存在')
        return False

# 爬取 "tiaoma.cnaidc.com" 来查找商品信息
def requestT1(shop_id):
    url = 'http://tiaoma.cnaidc.com'
    s = requests.session()

    # 获取验证码
    img_data = s.get(url + '/index/verify.html?time=', headers=headers).content
    with open('verification_code.png', 'wb') as v:
        v.write(img_data)

    # 解验证码
    ocr = ddddocr.DdddOcr()
    with open('verification_code.png', 'rb') as f:
        img_bytes = f.read()
    code = ocr.classification(img_bytes)
    logger.info('当前验证码为 ' + code)
    # 请求接口参数
    data = {"code": shop_id, "verify": code}
    resp = s.post(url + '/index/search.html', headers=headers, data=data)
    resp_json = parse_json(resp.text)
    logger.info(resp_json)

    # 判断是否查询成功
    if resp_json['msg'] == '查询成功' and resp_json['json'].get('code_img'):
        code_name = resp_json['json']['code_name']


        # 保存商品图片
        img_url = ''
        if resp_json['json']['code_img'].find('http') == -1:
            img_url = url + resp_json['json']['code_img']

        else:
            img_url = resp_json['json']['code_img']

        try:
            shop_img_data = s.get(img_url, headers=headers, timeout=10, ).content
            # 新建目录
            mkdir(path + '\\' + shop_id)
            localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())

            # 保存图片
            with open(path + '\\' + shop_id + '\\' + str(localtime) + '.png', 'wb') as v:
                v.write(shop_img_data)
            logger.info(path + '\\' + shop_id + '\\' + str(localtime) + '.png')
            return code_name
        except requests.exceptions.ConnectionError:
            logger.info('访问图片URL出现错误！')


    if resp_json['msg'] == '验证码错误':
        requestT1(shop_id)

'''
# 通过配合商品名通过百度找图片
def getBaiDu(shop_id, search_title):
    baidu_url = "http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1460997499750_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word={}".format(
        search_title)
    result = requests.get(baidu_url, headers=headers)
    dowmloadPic(result.text, shop_id)

def dowmloadPic(html, shop_id):
    # 爬取多少张
    num_download = 5
    # 新建目录
    mkdir(path + '\\' + shop_id)
    for addr in re.findall('"objURL":"(.*?)"', html, re.S):
        if num_download < 0:
            break
        logger.info('现在正在爬取URL中的地址：' + str(addr))
        try:
            pic = requests.get(addr, timeout=10, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.info('您当前的URL出现错误！')
            continue
        localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        fn = open(path + '\\' + shop_id + '\\' + str(localtime) + '.png', 'wb')
        fn.write(pic.content)
        fn.close()

        # drop_wartermark(path + '\\' + shop_id + '\\' + str(localtime) +'.png', path + '\\' + shop_id + '\\' + str(localtime) +'-0.png')

        num_download = num_download - 1
        logger.info(path + '\\' + shop_id + '\\' + str(localtime) + '.png')
'''

# 检测图像中的码（解码）
def Read_Decode_Pic(image):
    shop_id = ""  # 创建一个字符串变量用于存储识别出的数字

    # 遍历解码
    for code in decode(image):
        data = code.data.decode('utf-8')  # 解码数据

        # 多边形获取（矩形的框）
        color = (0, 0, 255)
        pts_poly = np.array(code.polygon, np.int32)  # 获取多边形坐标
        cv2.polylines(image, [pts_poly], True, color, 5)  # 画多边形框

        # 显示数据（获取矩形框的左上角作为Text的坐标(左边坐标)，显示数据）
        pts_rect = code.rect
        cv2.putText(image, data, (pts_rect[0], pts_rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # 将识别出的数字追加到字符串变量中
        shop_id += data

    cv2.imshow('image', image)  # 等画出所有矩形后显示
    return shop_id  # 返回字符串变量

# 检测视频中的码（解码）
def Read_Decode_Cam():
    cap = cv2.VideoCapture(0)  # 打开视频
    cap.set(3, 1000)  # 帧的宽度
    cap.set(4, 800)  # 帧的高度

    while True:
        success, image = cap.read()  # 获取每一帧图片
        cv2.imshow('image', image)
        image = Read_Decode_Pic(image)  # 对每一帧图片检测
        cv2.waitKey(1)  # 延时1ms

def run(shop_id):
    # 通过 "tiaoma.cnaidc.com" 查找
    # requestT1('6935580000116')
    code_name = requestT1(shop_id)
    print('商品条码为：',shop_id)
    print('商品名称为：',code_name)

    # 通过百度查找
    # getBaiDu('6903148094501', '矿泉水')
    # getBaiDu(shop_id, shop_name)

if __name__ == '__main__':
    img = cv2.imread('demo2.jpg')
    shop_id=Read_Decode_Pic(img)  # 检测图像中的码（解码）
    #Read_Decode_Cam()  # 检测视频中的码（解码）
    cv2.waitKey(0)
    run(shop_id)

