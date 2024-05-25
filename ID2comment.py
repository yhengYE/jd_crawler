# 导入必要的库
import requests
import json
import time
import pandas as pd
import name2id

# 函数：发起请求到京东并获取特定页面的数据
def start(page, produce_id):
    # 构建京东商品评论页面的URL
    url = ('https://club.jd.com/comment/productPageComments.action?'
           f'&productId={produce_id}'  # 商品ID
           f'&score=0'  # 0表示所有评论，1表示好评，2表示中评，3表示差评，5表示追加评论
           '&sortType=5'  # 排序类型（通常使用5）
           f'&page={page}'  # 要获取的页面数
           '&pageSize=10'  # 每页评论数
           '&isShadowSku=0'
           '&fold=1')

    # 设置headers以模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36"
    }

    time.sleep(2)
    # 发送GET请求获取数据
    response = requests.get(url=url, headers=headers)
    # 将返回的JSON数据解析为字典
    data = json.loads(response.text)
    print(data)  # 打印获取的数据，确保正确获取到评论数据
    return data


# 解析函数：从返回的数据中提取所需信息
def parse(data):
    items = data['comments']
    for i in items:
        yield i['content']


# TXT函数：将数据写入TXT文件
def txt(items, file_path='wooting.txt'):
    # 打开文件，如果文件不存在则创建
    with open(file_path, 'a', encoding='utf-8') as file:
        # 遍历每个条目，将其格式化为字符串并写入文件
        for item in items:
            file.write(item + '\n')  # 直接写入评论内容并添加换行符

def read_first_column(line):
    # 以逗号为分隔符，只返回第一个逗号前的内容
    return line.split(',')[0]

# 主函数：控制整个爬取过程
def crawler(filename):
    # 读取 Excel 文件，假设 ID 列在第一列
    df = pd.read_csv(filename, encoding='utf-8-sig', header=None, converters={0: read_first_column})

    # 提取 ID 列
    produce_ids = df.iloc[:, 0].tolist()
    batch_size = 20  # 每批处理的 ID 数量
    num_batches = len(produce_ids) // batch_size + 1

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = min((batch_index + 1) * batch_size, len(produce_ids))
        batch_produce_ids = produce_ids[start_index:end_index]

        for produce_id in batch_produce_ids:
            total_pages = 10  # 设置要爬取的总页数

            for current_page in range(total_pages):
                time.sleep(0.05)
                data = start(current_page + 1, produce_id)  # 交换参数顺序
                parsed_data = parse(data)
                txt(parsed_data)

                print('商品ID为', produce_id, '的第', current_page + 1, '页抓取完毕')



# 如果作为独立脚本运行，则执行主函数
if __name__ == '__main__':
    word='塑水宗'
    filename=name2id.n2id(word)
    crawler(filename)