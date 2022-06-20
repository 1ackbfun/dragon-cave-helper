import os
import re
import json
import requests
#import lxml
from bs4 import BeautifulSoup


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
                            breed = [
                                re.sub(r'\[.*\]$', '', data[2].text.strip()),
                                data[0].find('img')['alt'].split(' egg')[0],
                            ]
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
                            result[breed[0]] = {
                                'breed':
                                breed,
                                'egg': [
                                    re.sub(r'\[.*\]$', '',
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
                    for raw_data in table.find_all('tr'):
                        data = raw_data.find_all('td')
                        if len(data) < 3:
                            continue
                        try:
                            egg_desc = data[1].text
                            separator_index = egg_desc.rfind('.')
                            result.append({
                                'breed':
                                data[0].find('img')['alt'].split(' egg')[0],
                                'breed_chs':
                                re.sub(r'\[.*\]$', '', data[2].text.strip()),
                                'egg':
                                f'{egg_desc[:separator_index]}.',
                                'egg_chs':
                                re.sub(r'\[.*\]$', '',
                                       egg_desc[separator_index + 1:].strip())
                            })
                        except Exception as e:
                            print(f'[ERROR] {e}')
                            print(raw_data.prettify())
            print(f'[INFO] 处理完成 成功解析 {len(result)} 组数据')
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
        for dragon in result:
            dragon_name = dragon['breed']
            if dragon_name in database:
                database[dragon_name]['breed'][1] = dragon['breed_chs']
                if database[dragon_name]['egg'][0] == dragon['egg']:
                    database[dragon_name]['egg'][1] = dragon['egg_chs']
                else:
                    print(
                        f"[WARN] 两次采集到的龙蛋描述出现差异: {dragon_name} ({dragon['breed_chs']})\n英文 Wiki: {database[dragon_name]['egg'][0]}\n中文 Wiki: {dragon['egg']}\n"
                    )
            else:
                print(f"[WARN] 在现存数据中没有找到 {dragon_name} ({dragon['egg']})\n")
        print(database['Witchlight Dragon'])
        with open(r'data\\database.json', 'w', encoding='utf8') as f:
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
