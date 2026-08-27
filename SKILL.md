---
name: chinese-naming-master
description: >-
  Chinese naming (取名) skill based on BaZi (八字), WuXing (五行), SanCai-WuGe (三才五格),
  ShengXiao (生肖), and classical literature. This skill generates optimized Chinese names
  with full cultural analysis: BaZi calculation, favorable element (喜用神) determination,
  five-grid (五格) scoring, phonetic screening, zodiac compatibility, and literary references
  from 18 classical texts (诗经/楚辞/论语/周易/道德经 etc.). Should be used when users ask
  for help naming a child, generating Chinese names, analyzing name fortune (姓名学),
  or creating names based on birth date/time. Supports single/double character names,
  sibling names, and renaming (改名).
version: 3.3.0
author: chinese-naming-master
license: MIT
---

## ⚠️ 强制规则（必须遵守）

1. **最少候选名数量**：每次取名必须生成至少 **10个** 候选名（top_n >= 10）
2. **HTML报告输出**：每次取名必须生成精致的 **HTML报告**，包含：
   - 八字排盘完整分析
   - 每个名字的详细解读：整体评分、评分理由、字义含义、经典出处、人生寓意、周易关联
   - 评分维度可视化（雷达图/条形图）
   - 精致美观的视觉设计
3. **报告生成代码**：使用 `report_generator.py` 生成报告
   ```python
   from report_generator import generate_html_report
   output_path = generate_html_report(result)
   ```

# Chinese Naming Master (中华取名大师)

## Purpose

Generate optimized Chinese names using traditional naming arts (姓名学) combined with
classical literature references. The skill covers the complete workflow: from birth-date
BaZi analysis through character selection, five-grid scoring, and literary citation.

## When to Use

This skill should be used when:

- Users ask to name a newborn child (宝宝取名/起名)
- Users want to generate candidate Chinese names (候选名字)
- Users ask to analyze an existing name's fortune (姓名分析/五格数理)
- Users want to rename (改名)
- Users ask for names from classical literature (诗经取名/楚辞取名)
- Users want sibling/双胞胎 names (兄弟姐妹名/双胞胎名)
- Users ask about naming culture/methods (取名文化/技法)

## How to Use

### Quick Start: Generate Names

```python
import sys
sys.path.insert(0, '_tools')
from name_generator import generate_names

# Generate names for a baby born 2024-03-15 10:00, surname Li, male
result = generate_names(
    surname='李',
    gender='male',
    birth_year=2024, birth_month=3, birth_day=15, birth_hour=10,
    name_length=2,     # 2-character name
    top_n=10           # return top 10 candidates
)

# Output includes: BaZi, 喜用神, zodiac, ranked candidates with scores
for c in result['candidates']:
    print(f'{c["full_name"]}  {c["total_score"]} ({c["grade"]})')
```

### Core Modules

| Module | File | Function |
|--------|------|----------|
| BaZi Engine | `_tools/bazi_engine.py` | Solar date → 4 pillars + WuXing + 喜用神 |
| Scoring Engine | `_tools/scoring_engine.py` | V3.1 6-dimension weighted scoring + 乘法扣分 |
| Name Generator | `_tools/name_generator.py` | Full pipeline: input → output |
| Theme Narrator | `_tools/theme_narrator.py` | V3.2 seasonal grouping + per-name narrative |

### Data Resources

| Directory | Content |
|-----------|---------|
| `01-数据资料/` | Hanzi DB (18,821 chars, Kangxi strokes 98.8%), surnames (466), SanCai-WuGe, GanZhi-BaZi, literature (1138 items) |
| `02-规则与算法资料/` | BaZi/WuXing/ShengXiao/phonetic/form/scoring rules + 59 naming techniques |
| `03-文化资料/` | Classical index, idioms (50), poetry imagery (78), name culture, history cases |
| `04-输出与交互资料/` | Input/output schemas, interaction flow, test cases, walkthrough |
| `05-开源项目参考/` | 5 open-source projects + James88/qiming archive |
| `06-取名知识库/` | 37 reading notes (29 books + 5 topics + guides) |

### Key Workflows

#### Workflow 1: Full BaZi Naming

1. Collect user input (surname, gender, birth date/time) → see `04-输出与交互资料/01-用户信息收集模板.md`
2. Run BaZi engine → get 4 pillars, 喜用神, zodiac
3. Filter characters from `01-数据资料/汉字字库/hanzi_common.json` by:
   - WuXing match (喜用神) → see `01-数据资料/喜用神推荐映射表.json`
   - Gender match → see `hanzi_common.json` `gender_hint` field
   - ShengXiao radicals → see `02-规则与算法资料/03-生肖喜忌偏旁表.json`
   - Exclude rare/difficult/homophone-risk chars
4. Generate candidate names (1 or 2 characters)
5. Calculate WuGe (五格) → see `01-数据资料/三才五格配置表/wuge_calc_rules.json`
6. Score with scoring engine (7 dimensions, weighted) → see `02-规则与算法资料/06-评分权重配置.json`
7. Rank and output top N → see `04-输出与交互资料/02-输出报告模板.md`

#### Workflow 2: Literature-Based Naming

1. Determine source classic based on gender/style:
   - Female → 诗经 (`shijing.json`, 178 items)
   - Male → 楚辞 (`chuci.json`, 89 items) or 周易 (`zhouyi.json`, 127 items)
   - Philosophical → 道德经 (`daodejing.json`, 172 items) or 论语 (`lunyu.json`, 81 items)
2. Search `01-数据资料/经典文学素材库/*.json` for matching words
3. Cross-reference with `hanzi_common.json` for WuXing/strokes/phonetics
4. Apply standard scoring pipeline

#### Workflow 3: Name Analysis (existing name)

1. Decompose name into characters
2. Look up each char in `hanzi_common.json` or `hanzi_full.json`
3. Calculate WuGe (五格) using `wuge_calc_rules.json`
4. Check SanCai configuration using `sancai_full.json`
5. Check phonetics (tones, homophones) using `04-声母韵母表.json` + `04-谐音黑名单词库.json`
6. Check ShengXiao compatibility using `03-生肖喜忌偏旁表.json`
7. Find literary references in `经典文学素材库/*.json`
8. Output analysis report per `02-输出报告模板.md`

### Weight Presets (V3.1)

The scoring engine uses a **6-dimension weighted** scoring system. Default weights (other dims ×0.82 + wuxing 0.18, dynamic: 平声姓→音韵 priority, 仄声姓→寓意 priority):

| Dimension | Default Weight | Notes |
|-----------|----------------|-------|
| 五格数理 (wuge_shuli) | 14.76% | 三才 + 核心格凶硬上限 |
| 音韵流畅 (yinyun) | 20.5% (平声姓 22.96%) | 声调平仄+谐音+声母韵母+粘连度 |
| 寓意深度 (yiyi) | 18.04% (仄声姓 20.5%) | 经典出处+字义美好度 |
| 字形美观 (zixing) | 8.2% | 笔画搭配+结构协调 |
| 现代语感 (modern_sense) | 20.5% | 成词性+时代感+用字审美 |
| **五行补益 (wuxing_buyi)** | **18%** | **V3.1 复活：喜用神 +25/字，忌神 -15** |

Multiplicative penalties (V3.1 full table): 谐音黑名单 ×0.1 / 核心三格凶数 ×0.5 / 外格凶数 ×0.85 / 核心半凶 ×0.9 / 俗气名 ×0.3 / 老气组合 ×0.5.

> 注：`06-评分权重配置.json` 内仍保留旧 7 维预设表（`default`/`八字优先`/`文雅古风`/`现代好听`）作为可读参考，但 `score_name` 自 V3.1 起以代码内六维权重为准，preset 参数目前不改变实际权重。

### Tone Screening Rules

- Adjacent characters should have different tones (see `02-规则与算法资料/12-声调搭配模式库.json`)
- Last character prefers tone 1 or 2 (收音响亮)
- Avoid all-flat (1/2) or all-ze (3/4) patterns
- Check homophones against `04-谐音黑名单词库.json` (103 不雅 + 204 歧义)

### Forbidden Characters

- Family elder names (避讳) → see `02-规则与算法资料/08-避讳与禁忌规则.md`
- Homophone blacklist → see `04-谐音黑名单词库.json`
- Rare/difficult chars → see `hanzi_common.json` `rare_flag`/`difficult_flag` fields
- Zodiac-disliked radicals → see `03-生肖喜忌偏旁表.json`

### Naming Techniques (59 total)

For creative naming beyond algorithmic generation, reference:
- 20 creativity techniques → `02-规则与算法资料/07-取名技法库.json`
- 32 traditional/modern methods → `02-规则与算法资料/08-取名方法库.json`
- 7 renaming methods → `02-规则与算法资料/09-改名方法规则.md`

### Sibling Name Generation

For multi-child families, see `02-规则与算法资料/11-兄弟姐妹名规则.json`:
- Shared character (共用一字)
- Antonym pairing (反义对仗)
- Sequential progression (递进序列)
- Word splitting (同源拆词)
- WuXing complement (五行互补)
