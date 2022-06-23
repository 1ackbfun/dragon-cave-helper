import os
from bs4 import BeautifulSoup
import zhconv
from .utils import *
from .web_spider import Spider


def parse_dragon_data() -> list:
    result = []
    for root, _, files in os.walk(r'cache\\dragon_en'):
        count = -1
        for file_name in files:
            count += 1
            file_path = os.path.join(root, file_name)
            print(f'[INFO] 开始解析 <{count}> {file_path}')
            html = ''
            if os.access(file_path, os.R_OK):
                with open(file_path, 'r', encoding='utf8') as f:
                    html = f.read()
                    f.close()
            if html == '':
                print(f'[WARN] 文件 {file_path} 读取失败')
            else:
                soup = BeautifulSoup(html, 'lxml')
                dragon_info_card = soup.select_one('.portable-infobox')
                try:
                    encyclopedia_id_node = dragon_info_card.select_one(
                        'td[data-source="encyclopedia_id"]')
                    encyclopedia_id = '' if encyclopedia_id_node is None else encyclopedia_id_node.find(
                        'a').attrs['href'].replace(
                            'https://dragcave.net/dragonopedia', '')
                    dragon = {
                        'breed':
                        dragon_info_card.find('h2').text,
                        'egg_desc':
                        dragon_info_card.select_one(
                            'td[data-source="egg_description"]').text,
                        'release_at':
                        dragon_info_card.select_one(
                            'div[data-source="release"]').find('div').text,
                        'elemental': [
                            element.text
                            for element in dragon_info_card.select_one(
                                'div[data-source="elements"]').find_all('a')
                        ],
                        'morphology':
                        dragon_info_card.select_one(
                            'div[data-source="morphology"]').find('div').text,
                        'bsa': [
                            bsa.text for bsa in dragon_info_card.select_one(
                                'div[data-source="bsa"]').find_all('a')
                        ],
                        'price':
                        dragon_info_card.select_one(
                            'div[data-source="price"]').find('div').text,
                        'habitats':
                        dragon_info_card.select_one(
                            'div[data-source="habitats"]').find('div').text,
                        'encyclopedia_id':
                        encyclopedia_id,
                    }
                    result.append(dragon)
                except Exception as e:
                    print(f'[ERROR] {e}')
                    print(dragon_info_card.prettify())
    return result


def parse_dragon_data_plus() -> list:
    result = []
    for root, _, files in os.walk(r'cache\\dragon_zh'):
        count = -1
        for file_name in files:
            count += 1
            file_path = os.path.join(root, file_name)
            print(f'[INFO] 开始解析 <{count}> {file_path}')
            html = ''
            if os.access(file_path, os.R_OK):
                with open(file_path, 'r', encoding='utf8') as f:
                    html = f.read()
                    f.close()
            if html == '':
                print(f'[WARN] 文件 {file_path} 读取失败')
            else:
                soup = BeautifulSoup(html, 'lxml')
                dragon_info_card = soup.select_one('.infobox > tbody')
                try:
                    dragon = {
                        'breed':
                        file_name.replace('.html', '').replace('_', ' '),
                        'breed_chs':
                        zhconv.convert(
                            dragon_info_card.select_one(
                                '.tablebackground').text.strip(), 'zh-hans'),
                        'rarity':
                        zhconv.convert(
                            dragon_info_card.select('tr > td')[5].text.strip(),
                            'zh-hans'),
                    }
                    result.append(dragon)
                except Exception as e:
                    print(f'[ERROR] {e}')
                    print(file_path, dragon_info_card.prettify())
    return result


def init() -> None:
    # 爬取英文 Wiki 数据: 龙蛋图像 / 英文百科词条路径 / 英文名 / 英文蛋描述 / 栖息地 / BSA / 元素亲和力 / 形态 / 发布日期 / 参考售价
    latest_list = Spider.update_dragon_list()
    print(f'[INFO] 英文 Wiki 收录龙类数量 {len(latest_list)}')
    JSONFile.write(r'data/dragon_list.en.json', latest_list)
    Spider.cache_dragon_egg_sprites(latest_list)
    Spider.cache_dragon_data_html(latest_list)
    # 爬取中文 Wiki 数据: 中文百科词条路径 / 中文名 / 中文蛋描述 / 参考稀有度
    zh_list = Spider.update_dragon_list_zh()
    print(f'[INFO] 中文 Wiki 收录龙类数量 {len(zh_list)}')
    JSONFile.write(r'data/dragon_list.zh.json', zh_list)
    Spider.cache_dragon_data_html_2(zh_list)
    return


def parse() -> None:
    JSONFile.write(r'data/dragon_details.json', parse_dragon_data())
    JSONFile.write(r'data/dragon_details_plus.json', parse_dragon_data_plus())
    return


def integrate() -> None:
    return


def main() -> None:
    init()  # 缓存中英 Wiki 龙蛋页面的条目
    parse()  # 根据缓存的 HTML 文件解析数据并整合为 JSON 导出
    integrate()


if __name__ == '__main__':
    main()
