# 安装指南

## 系统要求

- Python 3.8+
- 无需额外依赖（核心引擎仅使用 Python 标准库）

## 安装方式

### 方式一：Git Clone（推荐）

```bash
git clone https://github.com/yourname/chinese-naming-master.git
cd chinese-naming-master
```

### 方式二：下载 ZIP

从 GitHub Releases 页面下载 ZIP 压缩包，解压到本地目录。

### 方式三：作为 WorkBuddy Skill 安装

```bash
# 将整个目录复制到 WorkBuddy skills 目录
cp -r chinese-naming-master ~/.workbuddy/skills/chinese-naming-master
```

安装后 WorkBuddy 会自动识别 SKILL.md，当用户提到取名/起名/姓名学时会自动加载。

## 验证安装

```bash
cd chinese-naming-master
python _tools/bazi_engine.py
```

如果输出如下内容，说明安装成功：

```
=== 八字排盘引擎测试 ===

测试1: 2024-03-15 10:00
八字：甲辰年 丁卯月 戊寅日 丁巳时
日主：戊(土) | 强弱：中和(-1)
喜用神：水 | 忌用神： | 调候：木旺，喜火暖局或水润局
...
```

## 目录说明

| 目录 | 用途 |
|------|------|
| `_tools/` | 核心引擎代码（八字排盘/评分/取名生成） |
| `01-数据资料/` | 结构化数据文件（JSON） |
| `02-规则与算法资料/` | 取名规则文档 + 配置文件 |
| `03-文化资料/` | 文化背景资料 |
| `04-输出与交互资料/` | 输入输出模板 + 测试用例 |
| `05-开源项目参考/` | 参考项目归档 |
| `06-取名知识库/` | 37 篇精读笔记 |
| `docs/` | 详细文档 |
| `examples/` | 示例代码 |

## 常见问题

### Q: 需要安装 pip 包吗？
A: 不需要。核心引擎仅使用 Python 标准库（json, os, re, math, datetime, collections）。

### Q: 数据文件很大吗？
A: 全库约 50MB（含 James88/qiming 归档）。如不需要原始归档，可删除 `05-开源项目参考/james88-qiming/` 目录（约 43MB）。

### Q: 支持哪些 Python 版本？
A: Python 3.8+（使用了 walrus operator 和 f-string 特性，3.8 以下不兼容）。

### Q: 八字排盘精确吗？
A: 节气日期使用近似值（每月固定日期），精确排盘需接入天文计算库。对于取名用途，近似精度已足够。如需精确排盘，可接入 `ephem` 或 `sxtwl` 库。
