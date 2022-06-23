import os
import re
import time
import copy
import requests
from bs4 import BeautifulSoup
import lxml


class Spider():
    'Dragon Cave Wiki 爬虫'

    WIKI = {
        'root': 'https://dragcave.fandom.com',
        'dragon_list.en': {
            'url': 'https://dragcave.fandom.com/wiki/Egg/Identification_guide',
            'path': r'cache\\dragon_list.en.html'
        },
        'dragon_list.zh': {
            'url':
            'https://dragcave.fandom.com/zh/wiki/%E9%BE%8D%E8%9B%8B%E7%A8%AE%E9%A1%9E?variant=zh-hans',
            'path': r'cache\\dragon_list.zh.html'
        },
    }

    def __init__(self) -> None:
        pass

    @staticmethod
    def download_image(img_url: str,
                       img_path: str,
                       force_refresh: bool = False) -> bool:
        if force_refresh or not os.access(img_path, os.R_OK):
            time.sleep(1)
            try:
                response = requests.get(
                    img_url,
                    headers={
                        'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
                    })
                if response.status_code != 200:
                    print(f'[ERROR] 访问图片地址 {img_url} 失败')
                    return False
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                    print(f"[INFO] 下载图片 {img_path} 成功")
            except Exception as e:
                print(f'[ERROR] 从 {img_url} 下载图片 {img_path} 失败\n{e}')
                return False
        else:
            print('[INFO] 本地已存在该图片 跳过下载')
        return True

    @staticmethod
    def get_html(url: str,
                 cache_path: str,
                 allow_use_cache: bool = True) -> str:
        html = ''
        if allow_use_cache and os.access(cache_path, os.R_OK):
            with open(cache_path, 'r', encoding='utf8') as f:
                html = f.read()
                f.close()
        else:
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f'[ERROR] 访问网页地址 {url} 失败')
                    return ''
                html = response.text
                with open(cache_path, 'w', encoding='utf8') as f:
                    f.write(html)
                    f.close()
                    print(f'[INFO] 缓存网页到 {cache_path} 成功')
            except Exception as e:
                print(f'[ERROR] 缓存网页 {url} 失败\n{e}')
        return html

    @classmethod
    def update_dragon_list(cls) -> list:
        html = cls.get_html(cls.WIKI['dragon_list.en']['url'],
                            cls.WIKI['dragon_list.en']['path'], False)
        soup = BeautifulSoup(html, 'lxml')  # html.parser / lxml
        result = []
        index = 0
        for table in soup.select('.article-table > tbody'):
            if table.find('th').text.strip() != 'Egg':
                continue
            for raw_data in table.find_all('tr'):
                data = raw_data.find_all('td')
                if len(data) < 3:
                    continue
                try:
                    rarity = 'Unknown'
                    if index == 4:
                        rarity = 'Other'
                    elif index == 5:
                        rarity = 'Holiday'
                    dragon = {
                        'breed':
                        re.sub(r'\[.*\]$', '', data[0].find('a')['title'])
                        if 'title' in data[0].find('a').attrs else re.sub(
                            r'\[.*\]$', '', data[2].text.strip()),
                        'egg_desc':
                        re.sub(
                            r'\[.+\]$', '',
                            data[1].text.strip().replace('\'',
                                                         '’').replace('﻿',
                                                                      '')),
                        'wiki_path':
                        data[0].find('a')['href'],
                        'rarity':
                        rarity,
                        'egg_sprite': {
                            'filename':
                            data[0].find('img')['data-image-key'],
                            'url':
                            data[0].find('img')['data-src']
                            if 'data-src' in data[0].find('img').attrs else
                            data[0].find('img')['src']
                        }
                    }
                    if dragon['breed'] == 'Sunset':
                        dragon['breed'] = 'Sunset Dragon'
                        dragon[
                            'wiki_path'] = '/wiki/' + dragon['breed'].replace(
                                ' ', '_')
                        result.append(copy.deepcopy(dragon))
                        dragon['breed'] = 'Sunrise Dragon'
                        dragon[
                            'wiki_path'] = '/wiki/' + dragon['breed'].replace(
                                ' ', '_')
                    result.append(dragon)
                except Exception as e:
                    print(f'[ERROR] parse failed {e}')
                    print(raw_data.prettify())
            index += 1
        return result

    @classmethod
    def cache_dragon_egg_sprites(cls, dragon_list: list) -> None:
        count = 0
        for dragon in dragon_list:
            img_path = f"sprite\\{dragon['egg_sprite']['filename']}"
            if not os.access(img_path, os.R_OK):
                print(f"[{count}] 尝试缓存 {img_path}")
                Spider.download_image(dragon['egg_sprite']['url'], img_path)
            count += 1
        return

    @classmethod
    def cache_dragon_data_html(cls, dragon_list: list) -> None:
        count = 0
        for dragon in dragon_list:
            url = None
            page_path = f"cache\\dragon_en\\{dragon['wiki_path'].split('/')[-1]}.html"
            if dragon['wiki_path'].startswith('/'):
                url = f"{cls.WIKI['root']}{dragon['wiki_path']}"
            elif dragon['breed'] == 'Sunset':
                url = 'https://dragcave.fandom.com/wiki/Sunset_Dragon'
                page_path = 'cache\\dragon_en\\Sunset_Dragon.html'
                # url = 'https://dragcave.fandom.com/wiki/Sunrise_Dragon'
                # page_path = 'cache\\dragon_en\\Sunrise_Dragon.html'
            else:
                print(f"[{count}] 网址错误 {dragon['wiki_path']} 取消爬取")
                print(dragon)
                continue
            if not os.access(page_path, os.R_OK):
                time.sleep(1)
                print(f"[{count}] 尝试缓存 {url}")
                Spider.get_html(url, page_path)
            count += 1
        return

    @classmethod
    def cache_dragon_data_html_2(cls, dragon_list: list) -> None:
        count = -1
        for dragon in dragon_list:
            count += 1
            if dragon['wiki_path'] == '':
                continue
            url = None
            page_path = f"cache\\dragon_zh\\{dragon['breed'].replace(' ', '_')}.html"
            if dragon['wiki_path'].startswith(
                    '/') and dragon['wiki_path'] != '/zh/wiki/Bauta_Dragon':
                url = f"{cls.WIKI['root']}{dragon['wiki_path']}"
            else:
                print(f"[{count}] 网址错误 {dragon['wiki_path']} 取消爬取")
                print(dragon)
                continue
            if not os.access(page_path, os.R_OK):
                time.sleep(1)
                print(f"[{count}] 尝试缓存 {url}")
                Spider.get_html(url, page_path)
        return

    @classmethod
    def update_dragon_list_zh(cls) -> list:
        html = cls.get_html(cls.WIKI['dragon_list.zh']['url'],
                            cls.WIKI['dragon_list.zh']['path'], False)
        soup = BeautifulSoup(html, 'lxml')
        result = []
        table_index = -1
        for table in soup.select('.article-table > tbody'):
            table_index += 1
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
                        re.sub(
                            r'\[.*\]$', '',
                            data[2 if table_index == 5 else -2].text.strip()),
                        'egg_desc':
                        f'{egg_desc[:separator_index-1]}.',
                        'egg_desc_chs':
                        re.sub(r'\[.*\]$', '',
                               egg_desc[separator_index:].strip()),
                        'wiki_path':
                        data[-2].find('a')['href']
                        if data[-2].find('a') is not None else '',
                    })
                except Exception as e:
                    print(f'[ERROR] {e}')
                    print(raw_data.prettify())
        return result

    @classmethod
    def parse_dragon_data() -> None:
        return
