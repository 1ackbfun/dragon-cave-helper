# Dragon Cave Helper

## Preview Data

```
https://raw.githubusercontent.com/1ackbfun/dragon-cave-helper/main/data/dragon_db.json
```

```
https://cdn.jsdelivr.net/gh/1ackbfun/dragon-cave-helper@main/data/dragon_db.json
```

[JSON Hero](https://jsonhero.io/) \([Example](https://jsonhero.io/j/ixrJ50Rm0xbT)\)

## Example

```JSON
{
  "breed": [
    "英文种群名称",
    "中文种群名称"
  ],
  "egg": [
    "英文龙蛋描述",
    "中文龙蛋描述"
  ],
  "rarity": "稀有度",
  "habitat": [
    "栖息地1",
    "栖息地2"
  ],
  "bsa": "种族特性技能",
  "elemental": [
    "主要元素亲和力",
    "次要元素亲和力"
  ],
  "morphology": "型态",
  "release_at": "发布日期",
  "sprites": {
    "egg": [
      "官方的龙蛋图片文件名 (用于判断 /abandoned 的龙蛋信息以及渲染 /locations 的龙蛋图像)"
    ],
    "adult": [
      "官方/CDN的成体龙图片文件名 (用于预览龙蛋的成体外观)"
    ]
  }
}
```

## Todo

- [ ] 完善剩下缺失的数据项目
  1. 最重要的稀有度
  2. 官方的龙蛋图片文件名
  3. BSA
  4. 型态
  5. 元素亲和力
  6. 发布日期
- [ ] 研究中文 Wiki 存在、英文 Wiki 反而缺失的龙类是怎么回事，目前已发现的有
  1. `{'breed': 'Red-finned Tidal', 'breed_chs': '红鳍潮汐龙', 'egg': 'This egg is wet from the waves and has bright red stripes.', 'egg_chs': '这颗蛋被浪打湿并有明亮的红色条纹。'}`
  2. `{'breed': 'Seragamma Wyvern', 'breed_chs': '黄昏火山翼龙', 'egg': 'This plain-looking egg has faint speckles.', 'egg_chs': '这颗平凡的蛋上有淡淡的斑点。'}`
