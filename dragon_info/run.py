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
                    bsa_node = dragon_info_card.select_one(
                        'div[data-source="bsa"]').find('a')
                    bsa = '' if bsa_node is None else bsa_node.text
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
                        'bsa':
                        bsa,
                        'price':
                        dragon_info_card.select_one(
                            'div[data-source="price"]').find('div').text,
                        'habitats':
                        dragon_info_card.select_one(
                            'div[data-source="habitats"]').find('div').text,
                        'encyclopedia_id':
                        encyclopedia_id.strip('/'),
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
    JSONFile.write(r'data\\dragon_list.en.json', latest_list)
    Spider.cache_dragon_egg_sprites(latest_list)
    Spider.cache_dragon_data_html(latest_list)
    # 爬取中文 Wiki 数据: 中文百科词条路径 / 中文名 / 中文蛋描述 / 参考稀有度
    zh_list = Spider.update_dragon_list_zh()
    print(f'[INFO] 中文 Wiki 收录龙类数量 {len(zh_list)}')
    JSONFile.write(r'data\\dragon_list.zh.json', zh_list)
    Spider.cache_dragon_data_html_2(zh_list)
    return


def parse() -> None:
    JSONFile.write(r'data\\dragon_details.json', parse_dragon_data())
    JSONFile.write(r'data\\dragon_details_plus.json', parse_dragon_data_plus())
    return


def integrate() -> None:
    database = []
    for dragon in JSONFile.read(r'data\\dragon_list.en.json'):
        database.append({
            'breed': [dragon['breed'], ''],
            'egg': [dragon['egg_desc'], ''],
            'rarity': dragon['rarity'],
            'habitats': [],
            'bsa': '',
            'elemental': [],
            'morphology': '',
            'release_at': '',
            'wiki': [dragon['wiki_path'], ''],
            'sprites': {
                'egg': [
                    '', dragon['egg_sprite']['filename'],
                    dragon['egg_sprite']['url']
                ],
            }
        })
    for new_info in JSONFile.read(r'data\\dragon_list.zh.json'):
        dragon_found = False
        for dragon in database:
            have_desc = dragon['egg'][0].lower().replace('\'', '’')
            new_desc = new_info['egg_desc'].lower().replace('\'', '’')
            if dragon['breed'][0] == new_info['breed'] or similar(
                    have_desc, new_desc) > 0.9:
                dragon_found = True
                dragon['egg'][1] = new_info['egg_desc_chs']
                dragon['wiki'][1] = new_info['wiki_path']
                break
        if dragon_found == '':
            print(f"[WARN] 没有找到 {new_info}")
    for new_info in JSONFile.read(r'data\\dragon_details.json'):
        dragon_found = False
        for index, dragon in enumerate(database):
            have_desc = dragon['egg'][0].lower().replace('\'', '’')
            new_desc = new_info['egg_desc'].lower().replace('\'', '’')
            if dragon['breed'][0] == new_info['breed'] or similar(
                    have_desc, new_desc) > 0.9:
                dragon_found = True
                if dragon['egg'][0] != new_info['egg_desc']:
                    # print(
                    #     f"[WARN] <{index}> {new_info['breed']} 蛋的描述不一致 [{dragon['breed'][0]}] [{new_info['breed']}]"
                    # )
                    # print('相似度为:',
                    #       similar(dragon['egg'][0], new_info['egg_desc']))
                    # print(f"龙蛋清单: {dragon['egg'][0]}")
                    # print(f"条目单页: {new_info['egg_desc']}\n")
                    dragon['egg'][0] = new_info['egg_desc']
                dragon['breed'][0] = new_info['breed']
                dragon['release_at'] = new_info['release_at']
                dragon['elemental'] = new_info['elemental']
                dragon['morphology'] = new_info['morphology']
                dragon['bsa'] = new_info['bsa']
                dragon['price'] = new_info['price']
                if new_info['habitats'] != '':
                    for habitat in new_info['habitats'].split(','):
                        dragon['habitats'].append(habitat.strip())
                dragon['encyclopedia_id'] = 0 if new_info[
                    'encyclopedia_id'] == '' else int(
                        new_info['encyclopedia_id'])
                break
        if dragon_found == '':
            print(f"[WARN] 没有找到 {new_info}")
    rarity_dict = {
        '非常普通': 'Normal',
        '常见': 'Normal',
        '不常见': 'NotNormal',
        '稀有': 'Rare',
        '非常稀有': 'SuperRare',
    }
    for new_info in JSONFile.read(r'data\\dragon_details_plus.json'):
        dragon_found = False
        for dragon in database:
            if dragon['breed'][0] == new_info['breed']:
                dragon_found = True
                dragon['breed'][1] = new_info['breed_chs']
                if new_info['rarity'] == '':
                    new_info['rarity'] = 'Unknown'
                elif '节' in new_info['rarity']:
                    new_info['rarity'] = 'Holiday'
                else:
                    new_info['rarity'] = rarity_dict[new_info['rarity']]
                if dragon['rarity'] == 'Unknown':
                    dragon['rarity'] = new_info['rarity']
                break
        if dragon_found == '':
            print(f"[WARN] 没有找到 {new_info}")
    JSONFile.write(r'data\\dragon_db.json', database)
    return


def main() -> None:
    init()  # 缓存中英 Wiki 龙蛋页面的条目
    parse()  # 根据缓存的 HTML 文件解析数据并整合为 JSON 导出
    integrate()


if __name__ == '__main__':
    main()
