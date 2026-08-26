# API 文档

## 模块概览

| 模块 | 文件 | 核心函数 |
|------|------|---------|
| 八字排盘 | `_tools/bazi_engine.py` | `get_bazi()`, `get_recommended_radicals()` |
| 评分引擎 | `_tools/scoring_engine.py` | `score_name()`, `load_data()` |
| 取名生成 | `_tools/name_generator.py` | `generate_names()`, `calc_wuge()`, `filter_chars()` |

---

## bazi_engine 模块

### `get_bazi(year, month, day, hour=12, minute=0) -> BaziResult`

八字排盘主函数。从公历生日计算八字四柱、五行统计、日主强弱、喜用神。

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| year | int | - | 公历年（如 2024） |
| month | int | - | 公历月（1-12） |
| day | int | - | 公历日（1-31） |
| hour | int | 12 | 公历时（0-23） |
| minute | int | 0 | 公历分（暂未使用，预留） |

**返回：** `BaziResult` 对象

**BaziResult 属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| year_ganzhi | str | 年柱干支（如 "甲辰"） |
| month_ganzhi | str | 月柱干支 |
| day_ganzhi | str | 日柱干支 |
| hour_ganzhi | str | 时柱干支 |
| day_master | str | 日主（日干，如 "戊"） |
| day_master_wuxing | str | 日主五行（如 "土"） |
| strength | str | 强弱判定（"身强"/"身弱"/"中和"） |
| strength_score | int | 强弱分数 |
| xiyongshen | str | 喜用神五行（如 "水"） |
| jiyongshen | str | 忌用神五行 |
| tiaohou | str | 调候建议 |
| zodiac | str | 生肖（如 "龙"） |
| nayin | str | 年柱纳音（如 "覆灯火"） |
| wuxing_count | dict | 五行统计 {金:x, 木:x, 水:x, 火:x, 土:x} |
| pillars | dict | 四柱详情 {year/month/day/hour: 干支} |

**示例：**

```python
bazi = get_bazi(2024, 3, 15, 10)
print(bazi.year_ganzhi)  # "甲辰"
print(bazi.xiyongshen)   # "水"
print(bazi.zodiac)       # "龙"
```

### `get_recommended_radicals(xiyongshen) -> list`

根据喜用神返回推荐的偏旁部首。

**参数：** `xiyongshen` (str) - 喜用神五行（金/木/水/火/土）

**返回：** 部首列表（如 `['水', '氵', '雨', '子', '亥', '鱼', '黑']`）

### `get_forbidden_radicals(jiyongshen) -> list`

根据忌用神返回应避用的偏旁部首。

---

## scoring_engine 模块

### `load_data() -> dict`

加载评分所需的所有数据文件（权重配置、五格表、三才表、字库、生肖偏旁表）。

**返回：** 数据字典

### `score_name(name, surname, data, xiyongshen=None, jiyongshen=None, zodiac=None, wuge_numbers=None, sancai_wuxing=None, weight_preset='default') -> dict`

对候选名字进行多维度加权评分。

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| name | str | - | 名字（不含姓氏，如 "明轩"） |
| surname | str | - | 姓氏（如 "李"） |
| data | dict | - | `load_data()` 返回的数据 |
| xiyongshen | str | None | 喜用神五行 |
| jiyongshen | str | None | 忌用神五行 |
| zodiac | str | None | 生肖 |
| wuge_numbers | list | None | 五格数字 [天格, 人格, 地格, 外格, 总格] |
| sancai_wuxing | list | None | 三才五行 [天格五行, 人格五行, 地格五行] |
| weight_preset | str | 'default' | 权重预设 |

**返回：** 评分结果字典

```python
{
    'name': '明轩',
    'surname': '李',
    'full_name': '李明轩',
    'scores': {
        'wuxing_match': 50,       # 五行补益匹配度 (0-100)
        'wuge_shuli': 85,         # 五格数理吉凶 (0-100)
        'yinyun_fluency': 60,     # 音韵流畅度 (0-100)
        'yiyi_depth': 80,         # 寓意深度 (0-100)
        'sancai_config': 70,      # 三才配置吉凶 (0-100)
        'zixing_beauty': 60,      # 字形美观度 (0-100)
        'shengxiao_compat': 65,   # 生肖契合度 (0-100)
    },
    'weights': {...},             # 使用的权重配置
    'total_score': 65.8,          # 加权总分
    'grade': 'C（合格）',          # 等级 (S/A/B/C/D/F)
}
```

### `get_grade(score) -> str`

将分数转为等级。

| 分数范围 | 等级 |
|---------|------|
| 90+ | S（极佳） |
| 80-89 | A（优秀） |
| 70-79 | B（良好） |
| 60-69 | C（合格） |
| 50-59 | D（一般） |
| <50 | F（不推荐） |

---

## name_generator 模块

### `generate_names(surname, gender=None, birth_year=None, birth_month=None, birth_day=None, birth_hour=12, name_length=2, style=None, top_n=10, weight_preset='default') -> dict`

取名全流程主函数。

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| surname | str | - | 姓氏 |
| gender | str | None | 性别（'male'/'female'/'neutral'） |
| birth_year | int | None | 出生年 |
| birth_month | int | None | 出生月 |
| birth_day | int | None | 出生日 |
| birth_hour | int | 12 | 出生时 |
| name_length | int | 2 | 名字长度（1 或 2） |
| style | str | None | 风格偏好（'大气'/'文雅'/'古风'/'现代'） |
| top_n | int | 10 | 返回前 N 个 |
| weight_preset | str | 'default' | 评分权重预设 |

**返回：**

```python
{
    'input': {...},          # 输入参数
    'bazi': {...},           # 八字排盘结果
    'xiyongshen': '水',      # 喜用神
    'jiyongshen': '',        # 忌用神
    'zodiac': '龙',          # 生肖
    'candidates': [          # 候选名列表（按分数排序）
        {
            'name': '海源',
            'full_name': '李海源',
            'scores': {...},     # 7 维度评分
            'total_score': 84.2,
            'grade': 'A（优秀）',
        },
        ...
    ],
    'summary': {
        'total_candidates': 250,  # 生成总数
        'scored': 250,            # 评分总数
        'top_n': 10,              # 返回数量
    }
}
```

### `calc_wuge(surname, name, hanzi_map, surname_map) -> dict`

计算五格数字和三才五行。

**返回：**

```python
{
    'wuge_numbers': [8, 15, 13, 5, 21],      # [天格, 人格, 地格, 外格, 总格]
    'sancai_wuxing': ['金', '土', '木'],     # 三才五行
    'strokes': {'surname': 7, 'name': [11, 14]},  # 笔画
}
```

### `filter_chars(hanzi_map, gender=None, xiyongshen=None, jiyongshen=None, zodiac=None, ...) -> list`

从字库筛选候选字。

**硬过滤（排除）：** 生僻字、难写字、忌用神五行、性别不匹配

**软过滤（优先）：** 喜用神五行、生肖喜用偏旁

**返回：** 符合条件的字库条目列表

---

## 数据文件 API

### 汉字字库 (`hanzi_common.json`)

```python
{
    "char": "铭",
    "traditional": "銘",
    "pinyin": "míng",
    "tone": 2,                    # 声调 (1-4, 0=轻声)
    "pinyin_tone": "ming2",       # 数字声调格式
    "strokes_simplified": 11,
    "strokes_kangxi": 14,         # 康熙笔画
    "wuxing": "金",              # 五行
    "radical": "钅",             # 部首
    "meaning": "铭刻、铭记",
    "kangxi_meaning": "《说文》'记也'",
    "lucky": "吉",
    "rare_flag": false,
    "difficult_flag": false,
    "homophone_risk": "",
    "gender_hint": "male",        # male/female/neutral
    "style_tags": ["古风"]        # 风格标签
}
```

### 文学素材 (`shijing.json` 等)

```python
{
    "source": "诗经",
    "items": [
        {
            "word": "清扬",
            "origin": "《诗经·郑风·野有蔓草》",
            "quote": "有美一人，清扬婉兮",
            "meaning": "眉目清秀、神采飞扬",
            "usage": "女名多用",
            "pinyin": "qīng yáng",
            "style_tags": ["文雅"]
        }
    ]
}
```

### 评分权重 (`06-评分权重配置.json`)

```python
{
    "default": {
        "wuxing_match": 25,
        "wuge_shuli": 15,
        "yinyun_fluency": 15,
        "yiyi_depth": 15,
        "sancai_config": 10,
        "zixing_beauty": 10,
        "shengxiao_compat": 10
    },
    "presets": {
        "八字优先": {...},
        "文雅古风": {...},
        "现代好听": {...},
        "传统稳健": {...}
    },
    "hard_filters": [...],
    "soft_filters": [...]
}
```
