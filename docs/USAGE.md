# 使用教程

## 一、取名（完整流程）

### 1.1 基本取名

```python
import sys
sys.path.insert(0, '_tools')

from name_generator import generate_names

result = generate_names(
    surname='李',                    # 姓氏
    gender='male',                   # 性别：male/female/neutral
    birth_year=2024,                 # 出生年（公历）
    birth_month=3,                   # 出生月
    birth_day=15,                    # 出生日
    birth_hour=10,                   # 出生时（0-23，默认12）
    name_length=2,                   # 名字长度：1（单字名）或 2（双字名）
    top_n=10,                        # 返回前N个候选
    weight_preset='default'          # 评分权重：default/八字优先/文雅古风/现代好听
)

# 查看结果
print(f'八字：{result["bazi"]["year_ganzhi"]}年 {result["bazi"]["month_ganzhi"]}月 '
      f'{result["bazi"]["day_ganzhi"]}日 {result["bazi"]["hour_ganzhi"]}时')
print(f'日主：{result["bazi"]["day_master"]}({result["bazi"]["day_master_wuxing"]})')
print(f'喜用神：{result["xiyongshen"]} | 忌用神：{result["jiyongshen"]}')
print(f'生肖：{result["zodiac"]} | 纳音：{result["bazi"]["nayin"]}')
print(f'\n推荐名字（共{len(result["candidates"])}个）：')

for i, c in enumerate(result['candidates'], 1):
    print(f'\n{i}. {c["full_name"]}  {c["total_score"]}分 ({c["grade"]})')
    for dim, score in c['scores'].items():
        print(f'   {dim}: {score}')
```

### 1.2 使用不同权重预设

```python
# 八字优先（五行权重 35%）
result = generate_names('李', 'male', 2024, 3, 15, 10,
                       name_length=2, weight_preset='八字优先')

# 文雅古风（寓意权重 30%）
result = generate_names('王', 'female', 2024, 6, 20, 8,
                       name_length=2, weight_preset='文雅古风')

# 现代好听（音韵权重 35%）
result = generate_names('张', 'male', 2024, 8, 15, 10,
                       name_length=2, weight_preset='现代好听')
```

### 1.3 单字名

```python
result = generate_names('刘', 'male', 2024, 3, 15, 10,
                       name_length=1, top_n=5)
# 单字名的五格计算：外格固定为2
```

### 1.4 复姓取名

```python
result = generate_names('欧阳', 'male', 2024, 3, 15, 10,
                       name_length=2, top_n=5)
# 复姓五格计算：天格=姓两字笔画和+1，人格=姓第二字笔画+名首字笔画
```

## 二、八字排盘（单独使用）

```python
import sys
sys.path.insert(0, '_tools')

from bazi_engine import get_bazi

# 基本排盘
bazi = get_bazi(2024, 3, 15, 10)
print(bazi)

# 获取喜用神推荐部首
from bazi_engine import get_recommended_radicals, get_forbidden_radicals
print(f'喜用神{bazi.xiyongshen}推荐部首:', get_recommended_radicals(bazi.xiyongshen))
print(f'忌用神{bazi.jiyongshen}避用部首:', get_forbidden_radicals(bazi.jiyongshen))
```

### 立春边界测试

```python
# 立春前（2月4日前）年柱用上一年
bazi_before = get_bazi(2024, 2, 3, 10)  # 年柱=癸卯（2023年）
bazi_after = get_bazi(2024, 2, 5, 10)   # 年柱=甲辰（2024年）
```

## 三、姓名分析（已有名字）

```python
import sys
sys.path.insert(0, '_tools')

from scoring_engine import score_name, load_data
from name_generator import calc_wuge, load_hanzi_db, load_surnames

data = load_data()
hanzi_map = load_hanzi_db()
surname_map = load_surnames()

# 分析"李明轩"
name = '明轩'
surname = '李'

# 1. 计算五格
wuge = calc_wuge(surname, name, hanzi_map, surname_map)
print(f'五格：天格{wuge["wuge_numbers"][0]} 人格{wuge["wuge_numbers"][1]} '
      f'地格{wuge["wuge_numbers"][2]} 外格{wuge["wuge_numbers"][3]} '
      f'总格{wuge["wuge_numbers"][4]}')
print(f'三才：{wuge["sancai_wuxing"]}')

# 2. 评分（需要喜用神和生肖）
result = score_name(name, surname, data,
                    xiyongshen='水',       # 从八字排盘获得
                    zodiac='龙',            # 从八字排盘获得
                    wuge_numbers=wuge['wuge_numbers'],
                    sancai_wuxing=wuge['sancai_wuxing'])

print(f'\n{surname}{name} 综合评分: {result["total_score"]} ({result["grade"]})')
for dim, score in result['scores'].items():
    print(f'  {dim}: {score}')
```

## 四、从经典文学选名

```python
import json

# 搜索诗经中的取名素材
with open('01-数据资料/经典文学素材库/shijing.json', encoding='utf-8') as f:
    shijing = json.load(f)

# 按关键词搜索
keyword = '清'
matches = [item for item in shijing['items'] if keyword in item['word']]
for m in matches:
    print(f'{m["word"]} ← {m["origin"]}')
    print(f'  原句：{m["quote"]}')
    print(f'  寓意：{m["meaning"]}')
    print(f'  适用：{m["usage"]}')
```

## 五、兄弟姐妹名

```python
# 参考 02-规则与算法资料/11-兄弟姐妹名规则.json
import json

with open('02-规则与算法资料/11-兄弟姐妹名规则.json', encoding='utf-8') as f:
    rules = json.load(f)

for strategy in rules['strategies']:
    print(f'{strategy["name"]}：{strategy["description"]}')
    for ex in strategy.get('examples', []):
        print(f'  例：{ex}')
```

## 六、改名

```python
# 参考 02-规则与算法资料/09-改名方法规则.md
# 改名七法：谐音换字/部首改动/添删字/易序/综合

# 例：原名"朱月坡"有谐音问题，用谐音换字法改为"朱岳坡"
# 在字库中搜索"岳"替代"月"
```

## 七、自定义权重

```python
import json

# 修改 02-规则与算法资料/06-评分权重配置.json
with open('02-规则与算法资料/06-评分权重配置.json', encoding='utf-8') as f:
    config = json.load(f)

# 添加自定义预设（注：V3.1 起 score_name 实际使用代码内六维权重，
# 此处仅作可读参考。要真正改变权重需修改 scoring_engine.score_name 内的 weights 字典）
config['presets']['我的风格'] = {
    'wuge_shuli': 20,
    'yinyun': 20,
    'yiyi': 20,
    'zixing': 10,
    'modern_sense': 20,
    'wuxing_buyi': 10
}

with open('02-规则与算法资料/06-评分权重配置.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=1)

# 使用自定义预设
result = generate_names('李', 'male', 2024, 3, 15, 10,
                       name_length=2, weight_preset='我的风格')
```

## 八、API 速查

| 函数 | 模块 | 用途 |
|------|------|------|
| `get_bazi(year, month, day, hour)` | bazi_engine | 八字排盘 |
| `get_recommended_radicals(xiyongshen)` | bazi_engine | 喜用神→推荐部首 |
| `score_name(name, surname, data, ...)` | scoring_engine | 单个名字评分 |
| `load_data()` | scoring_engine | 加载评分数据 |
| `generate_names(surname, gender, ...)` | name_generator | 完整取名流程 |
| `calc_wuge(surname, name, ...)` | name_generator | 五格计算 |
| `filter_chars(hanzi_map, ...)` | name_generator | 字库筛选 |
