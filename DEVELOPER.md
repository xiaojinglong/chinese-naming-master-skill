# 开发者指南 (Developer Guide)

本文档面向需要修改或扩展中华取名大师的开发者。

---

## 目录结构说明

### 核心引擎（用户直接使用）

| 文件 | 说明 | 依赖 |
|------|------|------|
| `_tools/bazi_engine.py` | 八字排盘引擎 | 标准库 |
| `_tools/scoring_engine.py` | 评分引擎 | 标准库 |
| `_tools/name_generator.py` | 取名生成引擎 | 标准库 |
| `_tools/report_generator.py` | HTML报告生成器 | 标准库 |

### 数据加工脚本（开发者工具）

以下脚本用于从外部数据源生成项目所需的数据文件。**普通用户不需要运行这些脚本**，因为生成好的数据文件已包含在仓库中。

| 脚本 | 用途 | 外部数据依赖 |
|------|------|--------------|
| `gender_stats.py` | 从姓名语料库统计性别倾向 | `_downloads/qiming-main/data/Chinese_Names_Corpus_Gender（120W）.txt` |
| `build_full_hanzi.py` | 构建全量字库 | `_downloads/qiming-main/data/` |
| `merge_kangxi_strokes.py` | 合并康熙笔画数据 | `_downloads/kangxi/strokes.json` |
| `parse_sancai_full.py` | 解析三才配置表 | `_downloads/qiming-main/data/sancai.txt` |

### 辅助工具脚本

| 脚本 | 用途 | 外部依赖 |
|------|------|----------|
| `enrich_wuxing.py` | 扩充字库五行属性 | `05-开源项目参考/james88-qiming/data/`（已在仓库中） |
| `enrich_hanzi.py` | 扩充字库字段 | 无 |
| `gen_hanzi.py` | 生成常用字库 | 无（数据硬编码在脚本中） |
| `gen_ganzhi.py` | 生成干支数据 | 无 |
| `gen_sancai_wuge.py` | 生成三才五格数据 | 无 |
| `gen_wenxue.py` | 生成文学素材 | 无 |
| `gen_shengxiao_xiyi.py` | 生成生肖喜忌 | 无 |

---

## 外部数据源获取

如果您需要运行数据加工脚本，需要获取以下外部数据：

### 1. qiming-main 数据集

来源：[james88/qiming](https://github.com/james88/qiming) 开源项目

```bash
# 下载并解压到 _downloads/qiming-main/
mkdir -p _downloads/qiming-main
# 将数据文件放入 _downloads/qiming-main/data/
```

所需文件：
- `Chinese_Names_Corpus_Gender（120W）.txt` - 120万姓名性别语料
- `sancai.txt` - 三才配置原始数据
- 其他字库数据文件

### 2. 康熙笔画数据

```bash
mkdir -p _downloads/kangxi
# 将 strokes.json 放入 _downloads/kangxi/
```

---

## 数据文件格式说明

### hanzi_common.json（308个常用取名汉字）

```json
{
  "meta": { "name": "取名常用字库", "version": "1.0" },
  "chars": [
    {
      "char": "明",
      "traditional": "明",
      "pinyin": "míng",
      "strokes_simplified": 8,
      "strokes_kangxi": 8,
      "wuxing": "火",
      "radical": "日",
      "meaning": "光明、明亮",
      "kangxi_meaning": "照也",
      "lucky": "吉",
      "rare_flag": false,
      "difficult_flag": false,
      "homophone_risk": [],
      "gender_hint": "male",
      "tone": 2,
      "pinyin_tone": "míng",
      "style_tags": ["现代"]
    }
  ]
}
```

### wuge_1to81.json（五格数理表）

```json
{
  "meta": { "name": "五格1-81数理吉凶表" },
  "numbers": [
    { "number": 1, "grade": "大吉", "name": "太极之数", "meaning": "万物开泰..." }
  ]
}
```

### sancai_full.json（三才配置表）

```json
{
  "meta": { "name": "三才配置完整表" },
  "sancai": [
    { "combination": "木木木", "tian": "木", "ren": "木", "di": "木", "grade": "大吉", "explanation": "..." }
  ]
}
```

---

## 扩展指南

### 添加新的汉字

1. 编辑 `01-数据资料/汉字字库/hanzi_common.json`
2. 确保包含所有18个必填字段
3. 运行测试验证：`python _tools/name_generator.py`

### 添加新的文学素材

1. 在 `01-数据资料/经典文学素材库/` 目录下创建新的JSON文件
2. 遵循 `wenxue_schema.json` 中定义的格式
3. 评分引擎会自动加载新文件

### 添加新的评分维度

1. 在 `02-规则与算法资料/06-评分权重配置.json` 中添加新维度
2. 在 `_tools/scoring_engine.py` 中实现评分函数
3. 在 `score_name()` 函数中调用新评分函数

---

## 测试

```bash
# 运行核心引擎测试
python _tools/bazi_engine.py
python _tools/scoring_engine.py
python _tools/name_generator.py

# 运行示例脚本
python examples/quick_start.py
python examples/naming_with_report.py

# 压力测试（12000个名字）
python -c "
from _tools.name_generator import generate_names
for hour in range(0, 24, 2):
    for surname in ['李', '王', '张']:
        r = generate_names(surname, gender='male', birth_year=2026,
                          birth_month=8, birth_day=27, birth_hour=hour, top_n=10)
        assert len(r['candidates']) >= 10
print('All tests passed!')
"
```

---

## 注意事项

1. **节气近似值**：八字引擎使用2月4日作为立春的近似日期。如需精确计算，可使用 `jieqi.json` 中的数据
2. **字库选择**：默认使用 `hanzi_common.json`（308字），如需更大覆盖可切换到 `hanzi_full.json`（18821字）
3. **编码问题**：所有JSON文件使用UTF-8编码，Windows环境下注意终端编码设置
