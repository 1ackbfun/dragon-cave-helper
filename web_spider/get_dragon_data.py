import os
import re
import json
import requests
#import lxml
from bs4 import BeautifulSoup


def similar(str1: str, str2: str) -> float:
    str1 = str1 + ' ' * (len(str2) - len(str1))
    str2 = str2 + ' ' * (len(str1) - len(str2))
    return sum(1 if i == j else 0
               for i, j in zip(str1, str2)) / float(len(str1))


class Spider():
    'Dragon Cave Wiki 爬虫'

    def getDragonData() -> bool:

        def captureHTML(url: str,
                        cache_path: str,
                        allow_use_cache: bool = False) -> str:
            html = ''
            if allow_use_cache and os.access(cache_path, os.R_OK):
                with open(cache_path, 'r', encoding='utf8') as f:
                    html = f.read()
                    f.close()
            else:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f'[ERROR] 从 {url} 获取数据失败\n{e}')
                    return ''
                print(f'[INFO] 爬取网页 {url} 成功')
                html = response.text
                with open(cache_path, 'w', encoding='utf8') as f:
                    f.write(html)
                    f.close()
            return html

        def parseHTML(html: str, method: str) -> dict or list:
            soup = BeautifulSoup(html, 'html.parser')  # html.parser / lxml
            result = []
            if method == 'type.en':
                result = {}
                morphology = [
                    '未知型态', 'Two-headed Dragon', 'Pygmy Dragon', 'Drake',
                    'Non-dragon', '未知型态'
                ]
                index = 0
                for table in soup.select('.article-table > tbody'):
                    if table.find('th').text.strip() != 'Egg':
                        continue
                    for raw_data in table.find_all('tr'):
                        data = raw_data.find_all('td')
                        if len(data) < 3:
                            continue
                        try:
                            breed = re.sub(r'\[.*\]$', '',
                                           data[2].text.strip())
                            habitats = []
                            if len(data) > 3:
                                for habitat_str in data[3].find_all('a'):
                                    habitat = habitat_str.text.strip()
                                    if habitat == 'All habitats':
                                        habitats.extend([
                                            'Alpine', 'Coast', 'Desert',
                                            'Forest', 'Jungle', 'Volcano'
                                        ])
                                    else:
                                        habitats.append(habitat)
                            result[breed] = {
                                'breed': [breed, ''],
                                'egg': [
                                    re.sub(r'\[.+\]$', '',
                                           data[1].text.strip()), ''
                                ],
                                'rarity':
                                'Holiday' if index == 5 else '未知稀有度',
                                'habitat':
                                habitats,
                                'bsa':
                                '未知种族特性技能',
                                'elemental': ['主要元素亲和力', '次要元素亲和力'],
                                'morphology':
                                morphology[index],
                                'release_at':
                                '未知发布日期',
                                'sprites': {
                                    'egg': [''],
                                    'adult': ['']
                                }
                            }
                        except Exception as e:
                            print(f'[ERROR] {e}')
                            print(raw_data.prettify())
                    index += 1
            elif method == 'type.zh':
                for table in soup.select('.article-table > tbody'):
                    if table.find('th').text.strip() != '蛋':
                        continue
                    temp_egg_desc = ''
                    temp_count = 0
                    for raw_data in table.find_all('tr'):
                        data = raw_data.find_all('td')
                        if len(data) < 3:
                            continue
                        if 'rowspan' in data[1].attrs:
                            temp_egg_desc = data[1].text
                            temp_count = int(data[1]['rowspan']) - 1
                        try:
                            if temp_count > 0 and len(data) == 3:
                                egg_desc = temp_egg_desc
                                temp_count -= 1
                            else:
                                egg_desc = data[1].text
                            separator_index = re.search(
                                '[\\u4e00-\\u9fa5]',
                                egg_desc).span()[0]  #egg_desc.rfind('.')
                            result.append({
                                'breed':
                                data[0].find('img')['alt'].split(' egg')[0],
                                'breed_chs':
                                re.sub(r'\[.*\]$', '', data[2].text.strip()),
                                'egg':
                                f'{egg_desc[:separator_index-1]}.',
                                'egg_chs':
                                re.sub(r'\[.*\]$', '',
                                       egg_desc[separator_index:].strip())
                            })
                        except Exception as e:
                            print(f'[ERROR] {e}')
                            print(raw_data.prettify())
            print(f'[INFO] {method} 处理完成 成功解析 {len(result)} 组数据')
            return result

        wiki = {
            'type.en': {
                'url':
                'https://dragcave.fandom.com/wiki/Egg/Identification_guide',
                'path': r'cache\\type.en.html'
            },
            'type.zh': {
                'url':
                'https://dragcave.fandom.com/zh/wiki/%E9%BE%8D%E8%9B%8B%E7%A8%AE%E9%A1%9E?variant=zh-hans',
                'path': r'cache\\type.zh.html'
            },
        }
        target = 'type.en'
        database = parseHTML(
            captureHTML(wiki[target]['url'], wiki[target]['path'], True),
            target)
        target = 'type.zh'
        result = parseHTML(
            captureHTML(wiki[target]['url'], wiki[target]['path'], True),
            target)
        print('[INFO] 开始整合数据...\n')
        for dragon in result:
            dragon_name = dragon['breed']
            if dragon_name in database:
                database[dragon_name]['breed'][1] = dragon['breed_chs']
                if database[dragon_name]['egg'][0] == dragon['egg']:
                    database[dragon_name]['egg'][1] = dragon['egg_chs']
                elif similar(database[dragon_name]['egg'][0],
                             dragon['egg']) > 0.9:
                    # TODO 抉择: 使用中文 Wiki 还是英文 Wiki 的版本
                    database[dragon_name]['egg'][1] = dragon['egg_chs']
                else:
                    print(
                        f"英文 Wiki: {database[dragon_name]['egg'][0]}\n中文 Wiki: {dragon['egg']}\n[ERROR] 两次采集到的龙蛋描述出现巨大差异: {dragon_name} ({dragon['breed_chs']})\n"
                    )
            else:
                found = False
                for record_dragon in database:
                    if database[record_dragon]['egg'][0] == dragon['egg']:
                        # or dragon['breed'] in database[record_dragon]['breed'][0]
                        database[record_dragon]['egg'][1] = dragon['egg_chs']
                        found = True
                        break
                    elif similar(database[record_dragon]['egg'][0],
                                 dragon['egg']) > 0.9:
                        database[record_dragon]['egg'][1] = dragon['egg_chs']
                        found = True
                        print(
                            f"英文 Wiki: {database[record_dragon]['egg'][0]} ({database[record_dragon]['breed'][0]})"
                        )
                        print(f"中文 Wiki: {dragon['egg']} ({dragon['breed']})")
                        print('[WARN] 检索到相似描述的龙蛋 已尝试应用\n')
                        break
                if found:
                    #print('[DEBUG] 已通过龙蛋描述检索到对应的龙')
                    pass
                else:
                    print(dragon)
                    print(
                        f"[ERROR] 在现存数据中没有找到 {dragon_name} ({dragon['egg']})\n"
                    )
        print('[DEBUG]', database['Witchlight Dragon'])
        with open(r'data\\dragon_db.json', 'w', encoding='utf8') as f:
            f.write(
                json.dumps(database,
                           ensure_ascii=False,
                           sort_keys=False,
                           indent=2,
                           separators=(',', ': ')))
            f.close()
        return True


def main() -> None:
    Spider.getDragonData()


if __name__ == '__main__':
    main()
