# encoding='utf-8'
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from urllib import parse
import csv
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import base64
import time
import cv2
from PIL import Image
import os

# 创建一个ChromeOptions对象，用于配置Chrome浏览器的启动参数
options = ChromeOptions()

# 添加一个实验性的选项，排除某些启动开关，这里排除了'enable-automation'开关
# 排除这个开关可以使浏览器在启动时不显示自动化控制的标识，有助于绕过某些网站的反爬虫机制
options.add_experimental_option('excludeSwitches', ['enable-automation'])

# 使用配置好的options来初始化Chrome浏览器驱动
driver = webdriver.Chrome(options=options)

# 执行Chrome DevTools Protocol (CDP) 命令，这个命令会在每个新打开的文档上执行一段JavaScript代码
# 这段JavaScript代码的目的是重新定义window.navigator.webdriver对象的getter方法
# 将其getter方法设置为返回undefined，这意味着当网站尝试检查navigator.webdriver属性时
# 它将无法得到任何值（undefined），从而隐藏了自动化控制的痕迹
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                       {
                           'source': 'Object.defineProperty(navigator, "webdriver",{get:() => undefined})'
                       })

wait = WebDriverWait(driver, 10)
def resize_and_save_image(image_path, output_directory, output_filename, target_width,
                          target_height):
    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

        # 打开图像
    image = Image.open(image_path)

    # 如果图像是RGBA模式，转换为RGB模式
    if image.mode == 'RGBA':
        image = image.convert('RGB')

        # 调整图像尺寸
    new_img = image.resize((target_width, target_height))

    # 构建完整的输出文件路径
    output_path = os.path.join(output_directory, output_filename)

    # 保存为JPEG格式
    new_img.save(output_path)


def dow_base(base64_encoded_image, name):
    # 确保目录存在，如果不存在则创建它
    import os
    directory = './photo/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 解码Base64数据
    imagedata = base64.b64decode(base64_encoded_image)
    # 将解码后的数据写入文件
    with open(f'{directory}{name}', "wb") as file:
        file.write(imagedata)

    print(f'图片已保存为：{directory}{name}')


def identify_gap():
    print('开始识别时间', time.asctime())
    # 读取背景图片和缺口图片
    bg_img = cv2.imread('./resized_photos/background_new.jpg')  # 背景图片
    tp_img = cv2.imread('./resized_photos/piece_new.jpg')  # 缺口图片
    # 确保图片加载成功
    if bg_img is None or tp_img is None:
        print("Error: 图片未正确加载。请检查文件路径和文件完整性。")
        return None
        # 识别图片边缘
    bg_edge = cv2.Canny(bg_img, 100, 200)  # 修正拼写错误
    tp_edge = cv2.Canny(tp_img, 100, 200)  # 修正拼写错误
    # 缺口匹配
    # 如果 tp_edge 太大，您可能需要先对其进行缩放
    res = cv2.matchTemplate(bg_edge, tp_edge, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    # 绘制方框
    th, tw = tp_edge.shape[:2]
    top_left = max_loc  # 左上角点的坐标，使用英文命名
    bottom_right = (top_left[0] + tw, top_left[1] + th)  # 右下角点的坐标
    cv2.rectangle(bg_img, top_left, bottom_right, (0, 0, 255), 2)  # 绘制矩形

    # 保存图片到本地
    cv2.imwrite('./resized_photos/output_with_rectangle.jpg', bg_img)
    print('结束时间', time.asctime())

    # 返回缺口的X坐标
    return top_left[0]
# 确定京东搜索的链接

def get_url(n, word):
    print('爬取第' + str(n) + '页')
    # 确定搜索商品的内容
    keyword = {'keyword': word}
    # 页面n与参数page的关系 page = 2 * n - 1
    page = '&page=' + str(2 * n - 1)
    # 为了在URL中输入中文，需要将中文关键字转为UrlEncode编码
    url = 'https://search.jd.com/Search?' + parse.urlencode(keyword) + '&enc=utf-8' + page

    # 设置headers以模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36",
        "Cookie": 'shshshfpa=695bf289-b0ab-cde5-dfa1-7a74834da5cd-1700819123; shshshfpx=695bf289-b0ab-cde5-dfa1-7a74834da5cd-1700819123; __jdu=17008191235031403315919; pinId=qzLMmYZWxuiEYdwRXNCWpQ; pin=wdqNbVMgrtCSCy; unick=qNbVMgrtCSCy; _tp=8KpUYIdC7WDDQWJeDlOwJQ%3D%3D; _pst=wdqNbVMgrtCSCy; areaId=7; PCSYCityID=CN_410000_410100_0; rkv=1.0; ipLoc-djd=7-412-416-47178; unpl=JF8EAKJnAGQiaE1TBksHE0USSg0AWFhaTBEKaGcGUQ5RSVUEHAdOFhkZbVdfXg1XFgdzZgdFXF5AUAMQARwiEEhtVF9cCE8VBWxhA2RtaEhUNRoyGxQRSlRUVl0LSRMCbWcAVV9aS1ANGworEyBMXV1ubThLFABuYAdkXGhLXAEfChwUFk1VZBUzCQYXBW5mDFRVWEhWARoAGxcRSV9UWlUIQycCX2Q; __jdv=76161171|kong|t_1001537277_|tuiguang|762a49f30ae74c6786124b830064d58c|1714695271396; ceshi3.com=000; wxa_level=1; retina=0; cid=9; jxsid=17146987874017612659; appCode=ms0ca95114; webp=1; mba_muid=17008191235031403315919; visitkey=8231062084993559639; wlfstk_smdl=utjq4l3pwgwo9vuq1tw2khix838av0ap; TrackID=12WV98ZmZTqZnfnz1P4HpQRyBo1uiH7K27l1_bjD9HvTM91qAciw1g5fn_X2CRs-D42CkczrUjnWOtYOa7SOe7zz2F-HlsLF-YWsj--ezMhs; thor=1F19F09BFA78DBAA36068FAAA078250B4C612859A3F14D6CA28BFA1A35C35E4B3BD66F11B73B8FEA5CBFE5D85EB54F9A00C3B72C4B971463A359773C8B44EF5DE66C60F1C430D4629251CAAA8123BF65DFB78CDFA5DD765DECFDD39D23F5DD4421CE0D386DEC52396034169EE20B707DB90987469687183D1393E610432BCAC21924F675E583BCB902A1DB3162F618D8; flash=2_pO1JKLc9S75GR37bzEgPoP3Tc8sCjl2OZypPGsd4hHSxTjRYIXHYS8HC3qTtRrQrb3_G5Pwwtk6Shv_Y2dH54RhneutNR7kGzKQ4NnN0y-_S-DwDeoPkTx47wX_alLgwqoagQFV_r5e018GaN8JI16nllQ89AgxxP7uGPNsNYvh*; x-rp-evtoken=N-nAb5Oj6OS1u8hkvixIgJFCUp-ln4mLMRr_Uux9hd9muaWvwcNzAnNDD8i7YE3XeF1-BCAcLZdSDLZAnI-FBrJ9usebVI_DyuFSNW7NZf6lEh6mumhkddcTrGJkRwGkPaE37nMDpjB-_x_FlJJMFWB69FJDX3F1Iz2q34rqDj5ZoN3tiWlveBF5lcADMFXb2PP3Z1emhc9J7EigjdPY0TTh6gCcpWhG4SuImW1xEHA%3D; qrsc=3; sbx_hot_h=null; cd_eid=jdd03JL6BWZYDK3S6ZA4T64WNA6EHR26TTNRQ7YWZBF45L22T2DY4A7BHZLISIZMLJGLZ5UQXCBFGRMSJRQP5T25PIBGG3EAAAAMPHTHL7OQAAAAACNCDCL5GYYDFZEX; PPRD_P=UUID.17008191235031403315919; jxsid_s_u=https%3A//so.m.jd.com/ware/search.action; sc_width=1536; mt_xid=V2_52007VwMUU1xRUlIfShtYBGUDF1NfWlJeF0kRbAEwCxFVX1xaRh9BGVgZYgMXVkELW1xMVU5aATNRFQZYUFEIGnkaXQZiHxNWQVlQSx9KElgBbAYXYl9oUmofShFVDWEEFFtbWWJaHEob; __wga=1714712186577.1714712137918.1714712137918.1714712137918.3.1; jxsid_s_t=1714712186818; __jd_ref_cls=MLoginRegister_Login; xapieid=jdd03JL6BWZYDK3S6ZA4T64WNA6EHR26TTNRQ7YWZBF45L22T2DY4A7BHZLISIZMLJGLZ5UQXCBFGRMSJRQP5T25PIBGG3EAAAAMPHTHL7OQAAAAACNCDCL5GYYDFZEX; 3AB9D23F7A4B3C9B=JL6BWZYDK3S6ZA4T64WNA6EHR26TTNRQ7YWZBF45L22T2DY4A7BHZLISIZMLJGLZ5UQXCBFGRMSJRQP5T25PIBGG3E; __jdc=181111935; chat.jd.com=20170206; RT="z=1&dm=jd.com&si=voz7oc04nb&ss=lvq9n9g6&sl=0&tt=0"; 3AB9D23F7A4B3CSS=jdd03JL6BWZYDK3S6ZA4T64WNA6EHR26TTNRQ7YWZBF45L22T2DY4A7BHZLISIZMLJGLZ5UQXCBFGRMSJRQP5T25PIBGG3EAAAAMPHUFBSIIAAAAADTENSLP5TLLBHUX; __jda=181111935.17008191235031403315919.1700819123.1714712116.1714716026.16; shshshfpb=BApXc920CPupArVyZQuwjUW1oEwM4ixQXBkLAlgxv9xJ1MsU5coO2'

    }
    print('京东搜索页面链接:' + url)
    return url

# 在翻页后等待商品列表出现，表示页面加载完成
def wait_for_page_load():
    try:
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, 'J_goodsList')))
    except Exception as e:
        print("An error occurred while waiting for page load:", e)

# 在翻页之后调用等待函数
def parse_page(url, ostream):
    print('爬取信息并保存中...')
    driver.get(url)
    login()
    # 把滑轮慢慢下拉至底部，触发ajax
    for y in range(100):
        js = 'window.scrollBy(0,100)'
        driver.execute_script(js)
        time.sleep(0.1)
    # 翻页操作后等待页面加载完成
    wait_for_page_load()
    try:
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList .gl-item')))
    except TimeoutException:
        print("等待商品列表加载超时")
        return
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # 找到所有商品标签
    goods = soup.find_all('li', class_="gl-item")
    # 遍历每个商品，得到每个商品的信息
    # 遍历每个商品，得到每个商品的信息
    for good in goods:
        try:
            num = good['data-sku']
            # 京东有些手机没发布也显示了
            money = good.find('div', class_="p-price").strong.i.string
            if money == '待发布':
                continue
            # 就是京东有些商品竟然没有店铺名，导检索store时找不到对应的节点导致报错
            store = good.find('div', class_="p-shop").span
            commit = good.find('div', class_="p-commit").strong.a.string
            name = good.find('div', class_="p-name p-name-type-2").a.em
            detail_addr = good.find('div', class_="p-img").find('a')['href']
        except Exception:
            continue
        if store is not None:
            new_store = store.a.string
        else:
            new_store = '没有找到店铺 - -！'
        new_name = ''
        for item in name.strings:
            new_name = new_name + item
        product = (num, new_name, money, new_store, commit, detail_addr)
        save_to_csv(product, ostream)
        print(product)


def login():
    # 填写登录信息
    time.sleep(0.5)
    driver.find_element(By.ID, 'loginname').clear()
    driver.find_element(By.ID, 'loginname').send_keys('账号')
    time.sleep(0.5)
    driver.find_element(By.ID, 'nloginpwd').clear()
    driver.find_element(By.ID, 'nloginpwd').send_keys('密码')
    driver.implicitly_wait(3)
    driver.find_element(By.ID, 'loginsubmit').click()
    time.sleep(0.5)

    # 下载图片
    # 图片文件名（确保它们是唯一的，并且带上扩展名）
    bg_filename = 'background.jpg'
    tp_filename = 'piece.jpg'

    # 尝试次数
    attempts = 10

    for i in range(attempts):
        try:
            # 尝试获取昵称元素的文本
            name = driver.find_element(By.CLASS_NAME, 'nickname').text
            print(f'{name}-用户登录成功')
            # 如果找到了昵称，则关闭浏览器并退出循环

        except NoSuchElementException:
            print('未找到昵称元素，尝试第', i + 1, '次')

            # 获取图片src
            bg_img = driver.find_element(By.XPATH,
                                         '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div['
                                         '1]/img').get_attribute('src')
            tp_img = driver.find_element(By.XPATH,
                                         '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[1]/div[2]/div['
                                         '2]/img').get_attribute('src')
            # 清洗base64
            bg_img = re.split(',', bg_img)[1]
            tp_img = re.split(',', tp_img)[1]

            # 调用函数保存图片
            dow_base(bg_img, bg_filename)
            dow_base(tp_img, tp_filename)

            # 改变图片大小
            resize_and_save_image('./photo/background.jpg', './resized_photos', 'background_new.jpg',
                                  242, 94)
            resize_and_save_image('./photo/piece.jpg', './resized_photos', 'piece_new.jpg', 33, 33)

            # 分析滑块距离
            total_distance = identify_gap()
            print('缺口x距离：', total_distance)
            # 获取滑块元素
            hk = driver.find_element(By.XPATH,
                                     '//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[2]/div[3]')
            # 创建动作链并执行滑动操作
            action = ActionChains(driver)
            action.click_and_hold(hk).perform()
            time.sleep(0.5)  # 等待点击和保持生效

            # 接下来执行滑动逻辑...
            # 这里添加您自己的滑动逻辑代码
            # 每次滑动的距离
            step_size = (int(total_distance) / 14)+0.55
            print('每次滑动的距离：', step_size)
            # 滑动的间隔时间
            interval = 0.1
            for j in range(14):
                if j <= 6:
                    action.move_by_offset(xoffset=step_size - 1, yoffset=2).perform()
                    # action.pause(interval)
                elif 6 < j <= 12:
                    action.move_by_offset(xoffset=step_size + 1, yoffset=1).perform()
                    # action.pause(2)
                else:
                    action.move_by_offset(xoffset=step_size + 1.5, yoffset=1).perform()
                    action.release().perform()  # 释放鼠标
            # 等待一段时间再进行下一次尝试
            time.sleep(0.5)



def save_to_csv(result, ostream):
    ostream.writerow(result)

def n2id(word):

    # pages = int(input('请输入你想要抓取的页数(范围是1-100):'))
    pages = 1
    flag = False
    filename = f"{word}.csv"
    if not os.path.exists(filename):
        flag = True
    with open(filename, 'a', newline='', encoding='utf-8-sig') as output:
        writer = csv.writer(output)
        # 京东最大页面数为100

        if 1 <= pages <= 100:
            page = pages + 1
            for n in range(1, page):
                try:
                    url = get_url(n, word)  # 这里需要定义 get_url 函数
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue
                try:
                    parse_page(url, writer)  # 这里需要定义 parse_page 函数
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue
            print(word + '商品爬取完毕！')

    return filename

if __name__ == '__main__':
   word = '塑水宗'
   n2id()