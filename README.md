# 中华取名大师 (Chinese Naming Master)

> 基于 **八字五行 + 三才五格 + 生肖喜忌 + 经典文学** 的 AI 取名系统
>
> 覆盖 **18,821 字库**（康熙笔画 98.8%）+ **1,138 条经典取名素材**（18 部经典）+ **59 种取名技法** + 完整排盘/评分/生成引擎

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data: 144 files](https://img.shields.io/badge/data-144%20files-green.svg)](#)

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **八字排盘** | 公历生日 → 干支四柱（年/月/日/时柱）→ 五行统计 → 日主强弱 → 喜用神 → 调候建议 |
| **取名生成** | 全流程：输入 → 排盘 → 喜用神 → 字库筛选 → 候选名生成 → 五格计算 → 评分排序 → 输出 |
| **多维评分** | 7 维度加权评分（五行补益/五格数理/音韵流畅/寓意深度/三才配置/字形美观/生肖契合） |
| **经典引用** | 每个推荐名字附带经典出处（诗经/楚辞/周易/道德经等 18 部） |
| **生肖喜忌** | 12 生肖喜用/忌用偏旁部首筛选 |
| **音韵筛选** | 声调搭配 + 谐音黑名单（不雅/歧义/姓氏组合）+ 声母韵母检查 |
| **兄弟姐妹名** | 6 种关联命名策略（共用一字/反义对仗/递进序列/同源拆词/五行互补/声调呼应） |
| **改名支持** | 改名七法（谐音换字/部首改动/添删字/易序/综合） |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourname/chinese-naming-master.git
cd chinese-naming-master

# 无需安装额外依赖（仅依赖 Python 标准库）
# 如需运行示例脚本：
pip install -r requirements.txt  # 可选，仅 examples/ 需要
```

### 30 秒取名

```python
import sys
sys.path.insert(0, '_tools')

from name_generator import generate_names

# 给 2024年3月15日10点出生的李姓男宝宝取名
result = generate_names(
    surname='李',
    gender='male',
    birth_year=2024, birth_month=3, birth_day=15, birth_hour=10,
    name_length=2,
    top_n=5
)

print(f'八字：{result["bazi"]["year_ganzhi"]}年 {result["bazi"]["month_ganzhi"]}月 '
      f'{result["bazi"]["day_ganzhi"]}日 {result["bazi"]["hour_ganzhi"]}时')
print(f'喜用神：{result["xiyongshen"]} | 生肖：{result["zodiac"]}')
print('\n推荐名字：')
for c in result['candidates']:
    print(f'  {c["full_name"]}  {c["total_score"]}分 ({c["grade"]})')
```

**输出：**
```
八字：甲辰年 丁卯月 戊寅日 丁巳时
喜用神：水 | 生肖：龙

推荐名字：
  李海源  84.2分 (A优秀)
  李海溪  84.2分 (A优秀)
  李海江  81.2分 (A优秀)
  李海泽  79.6分 (B良好)
  李海清  78.8分 (B良好)
```

### 单独使用八字排盘

```python
import sys
sys.path.insert(0, '_tools')

from bazi_engine import get_bazi

# 1990年5月20日14点
bazi = get_bazi(1990, 5, 20, 14)
print(bazi)
# 八字：庚午年 辛巳月 乙酉日 癸未时
# 日主：乙(木) | 强弱：身弱(-2)
# 喜用神：水 | 忌用神：金 | 调候：火旺，喜水润局
# 五行统计：{'金': 3.5, '木': 1.3, '水': 1.0, '火': 2.5, '土': 1.8}
```

## 📁 项目结构

```
chinese-naming-master/
├── SKILL.md                        ← Skill 定义文件（WorkBuddy 标准）
├── README.md                       ← 本文件
├── LICENSE                         ← MIT 许可证
├── requirements.txt                ← Python 依赖（可选）
├── .gitignore
│
├── _tools/                         ← 核心引擎代码（3 个模块 + 7 个工具脚本）
│   ├── bazi_engine.py              ← 八字排盘引擎（公历→干支四柱+五行+喜用神）
│   ├── scoring_engine.py           ← 评分引擎（7 维度加权评分）
│   ├── name_generator.py           ← 取名生成引擎（全流程）
│   ├── add_tone_fields.py          ← 声调字段处理
│   ├── build_xiyongshen_map.py     ← 喜用神→字推荐映射生成
│   └── ...                         ← 其他数据加工脚本
│
├── 01-数据资料/                     ← 核心数据（JSON）
│   ├── 汉字字库/                    ← 18,821 字（康熙笔画 98.8%）+ 308 常用字
│   ├── 姓氏库/                      ← 413 单姓 + 53 复姓（全含康熙笔画+五行）
│   ├── 三才五格配置表/               ← 125 三才 + 81 数理 + 计算规则
│   ├── 天干地支与八字/               ← 天干/地支/生肖/纳音/节气
│   ├── 经典文学素材库/               ← 18 部经典 1,138 条取名素材
│   ├── 字辈谱库/                    ← 孔子世家+朱熹/朱元璋五行序辈
│   ├── 喜用神推荐映射表.json          ← 五行→推荐字/避用字
│   └── 五行部首推荐映射表.json         ← 五行→部首/字推荐
│
├── 02-规则与算法资料/                ← 取名规则（文档+配置）
│   ├── 01-八字排盘规则.md
│   ├── 02-五行分析规则.md
│   ├── 03-生肖喜忌规则.md + 偏旁表.json
│   ├── 04-音韵筛选规则.md + 谐音黑名单.json + 声母韵母表.json
│   ├── 05-字形筛选规则.md
│   ├── 06-评分规则.md + 权重配置.json
│   ├── 07-取名技法总览.md + 技法库.json
│   ├── 08-避讳与禁忌规则.md + 方法库.json
│   ├── 09-改名方法规则.md
│   ├── 10-姓氏声调模式表.json
│   ├── 11-兄弟姐妹名规则.json
│   ├── 12-声调搭配模式库.json
│   └── 算法总览与数据流.md
│
├── 03-文化资料/                     ← 名字解读文化底蕴
│   ├── 经典文献索引.md / 成语典故.md / 诗词意象.md / 姓名文化知识.md
│   └── 成语典故库.json / 诗词意象库.json / 历史命名案例库.json / 少数民族命名习俗库.json / 名字相协式库.json
│
├── 04-输出与交互资料/                ← 交互模板与 Schema
│   ├── 用户信息收集模板.md + schema.json
│   ├── 输出报告模板.md + schema.json
│   ├── 取名全流程示例.md
│   ├── 测试用例集.json
│   └── 交互流程设计.md
│
├── 05-开源项目参考/                  ← 5 个参考项目 + James88/qiming 归档
│
├── 06-取名知识库/                   ← 37 篇精读笔记（29 本书 + 5 专题 + 唐诗/宋词）
│   ├── 00-总目录与使用指南.md
│   ├── 01-先秦经典/（16 本）
│   ├── 02-辞书工具书/（5 本）
│   ├── 03-现代参考书/（10 本）
│   └── 04-专题资料/（5 个专题）
│
├── docs/                           ← 详细文档
│   ├── DATA_LIBRARY.md             ← 数据库完整目录与使用指引
│   ├── INSTALL.md                  ← 安装指南
│   ├── USAGE.md                    ← 使用教程
│   └── API.md                      ← API 文档
│
└── examples/                       ← 示例代码
    ├── quick_start.py              ← 快速开始示例
    ├── bazi_demo.py                ← 八字排盘示例
    └── naming_demo.py              ← 完整取名示例
```

## 📊 数据规模

| 维度 | 数量 |
|------|------|
| 汉字字库 | 18,821 字（康熙笔画覆盖率 98.8%） |
| 常用取名字 | 308 字（全字段含五行/部首/释义/性别/声调/风格标签） |
| 姓氏库 | 413 单姓 + 53 复姓 |
| 三才配置 | 125 组（完整吉凶断语） |
| 五格数理 | 1-81 数（完整吉凶） |
| 经典取名素材 | 1,138 条（18 部经典/文集） |
| 取名技法 | 59 种（20 创造学 + 32 法 + 7 改名） |
| 谐音黑名单 | 385 条（不雅/歧义/姓氏组合/缩写） |
| 知识库精读笔记 | 37 篇 |
| **总文件** | **144 个**（57 JSON + 64 MD + 23 PY） |

## 🔧 核心引擎

### 1. 八字排盘引擎 (`_tools/bazi_engine.py`)

```python
from bazi_engine import get_bazi

bazi = get_bazi(year=2024, month=3, day=15, hour=10)
# 返回：四柱干支、五行统计、日主强弱、喜用神、忌用神、调候建议、生肖、纳音
```

**算法：**
- 年柱：以立春为界（立春前用上一年）
- 月柱：以 12 节令为界，年干定月干（甲己之年丙作首...）
- 日柱：基日 1900-01-01 = 甲戌日，公式推算
- 时柱：日干定时干（甲己还加甲...）
- 五行统计：天干本气 + 地支藏干（本气/中气/余气加权）
- 日主强弱：得令 + 得地 + 得势 三维度评分
- 喜用神：身强则克泄耗，身弱则生扶

### 2. 评分引擎 (`_tools/scoring_engine.py`)

```python
from scoring_engine import score_name, load_data

data = load_data()
result = score_name('明轩', '李', data,
    xiyongshen='木', zodiac='龙',
    wuge_numbers=[8,15,13,5,21],
    sancai_wuxing=['金','土','木'],
    weight_preset='default')
# 返回：7 维度评分 + 加权总分 + 等级(S/A/B/C/D/F)
```

**7 个评分维度（默认权重）：**

| 维度 | 权重 | 说明 |
|------|------|------|
| 五行补益匹配度 | 25% | 喜用神五行 vs 名字五行 |
| 五格数理吉凶 | 15% | 1-81 数吉凶表 |
| 音韵流畅度 | 15% | 声调搭配+谐音+声母韵母 |
| 寓意深度 | 15% | 经典出处+字义美好度 |
| 三才配置吉凶 | 10% | 天格/人格/地格五行组合 |
| 字形美观度 | 10% | 笔画搭配+结构协调 |
| 生肖契合度 | 10% | 生肖喜忌偏旁匹配 |

### 3. 取名生成引擎 (`_tools/name_generator.py`)

```python
from name_generator import generate_names

result = generate_names(
    surname='李', gender='male',
    birth_year=2024, birth_month=3, birth_day=15, birth_hour=10,
    name_length=2, top_n=10
)
# 全流程：排盘 → 喜用神 → 筛选 → 生成 → 评分 → 排序 → 输出
```

## 📚 数据口径

| 项目 | 口径 |
|------|------|
| 笔画数 | 以**繁体字形 + 康熙字典笔画**为准 |
| 五行属性 | 以**字义五行为主**、字形（偏旁）五行为辅 |
| 三才吉凶 | 以 `sancai_full.json`（原文断语版 125 组）为准 |
| 八字排盘 | 月柱以**节令**为界，非农历初一 |
| 康熙笔画 | 308 常用字人工核对 + 18,311 字查繁体形式（breezyreeds/kangxi-strokecount） |
| 文学素材 | 出处须真实可查，篇名写全（如《诗经·郑风·野有蔓草》） |

## 📖 文档

- [安装指南](docs/INSTALL.md)
- [使用教程](docs/USAGE.md)
- [API 文档](docs/API.md)
- [数据库完整目录](docs/DATA_LIBRARY.md)

## 🤝 致谢

| 数据源 | 贡献 |
|--------|------|
| [James88/qiming](https://github.com/James88/qiming) | 字库三源合并（gsc_pinyin/xinhua/word.json）+ 三才/性别语料 |
| [breezyreeds/kangxi-strokecount](https://github.com/breezyreeds/kangxi-strokecount) | 63,696 字康熙笔画数据（MIT） |
| 《左传》《诗经》《楚辞》等 18 部经典 | 取名素材出处 |
| 李正明《给孩子起个好名字》 | 20 创造学技法 |
| 巨天中《吉名如意》 | 32 法 + 改名七法 |
| 吉常宏《古人名字解诂》 | 名字相协 22 式 |

## 📄 许可证

[MIT License](LICENSE) - 可自由使用、修改、分发。

数据文件中的古典文献内容属于公共领域；开源数据源（James88/qiming、breezyreeds/kangxi-strokecount）遵循各自原始许可证。

## ⚠️ 免责声明

本系统基于传统姓名学理论和文化典籍，取名结果仅供参考。姓名对人生的影响属于传统文化信仰范畴，不构成任何科学保证。建议结合家庭意愿、社会习俗和个人审美综合决策。
