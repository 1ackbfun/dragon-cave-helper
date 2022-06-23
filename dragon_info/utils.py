import json


def similar(str1: str, str2: str) -> float:
    str1 = str1 + ' ' * (len(str2) - len(str1))
    str2 = str2 + ' ' * (len(str1) - len(str2))
    return sum(1 if i == j else 0
               for i, j in zip(str1, str2)) / float(len(str1))


class JSONFile():

    @staticmethod
    def write(json_path: str, json_content: any) -> None:
        with open(json_path, 'w', encoding='utf8') as f:
            f.write(
                json.dumps(json_content,
                           ensure_ascii=False,
                           sort_keys=False,
                           indent=2,
                           separators=(',', ': ')))
            f.close()
            print(f'[INFO] 写入到 JSON 文件 {json_path} 成功')
        return

    @staticmethod
    def read(json_path: str) -> any:
        result = None
        with open(json_path, 'r', encoding='utf8') as f:
            result = json.loads(f.read())
            f.close()
            print(f'[INFO] 读取 JSON 文件 {json_path} 成功')
        return result
