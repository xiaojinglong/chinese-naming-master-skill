# -*- coding: utf-8 -*-
"""
陈姓高质量取名脚本 V3 - 经典文学优先版
====================================
核心策略：优先使用经典文学中的双字词，确保每个名字都有文化底蕴
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_tools'))
sys.stdout.reconfigure(encoding='utf-8')

from name_generator import generate_names, load_hanzi_db, load_literature_map
from scoring_engine import load_data, score_name
from bazi_engine import get_bazi

# 配置
SURNAME = '陈'
GENDER = 'male'
TOP_N_PER_SHICHEN = 10

# 日期范围：8月29日 - 9月2日
DATES = [
    (2026, 8, 29),
    (2026, 8, 30),
    (2026, 8, 31),
    (2026, 9, 1),
    (2026, 9, 2),
]

# 12时辰
SHICHEN = [
    ('子时', 0), ('丑时', 2), ('寅时', 4), ('卯时', 6),
    ('辰时', 8), ('巳时', 10), ('午时', 12), ('未时', 14),
    ('申时', 16), ('酉时', 18), ('戌时', 20), ('亥时', 22),
]

def get_classic_names_from_literature():
    """从经典文学中提取适合取名的双字词"""
    from scoring_engine import _load_literature_data
    literature = _load_literature_data()  # 使用完整的文学数据
    hanzi_map = load_hanzi_db('expanded')

    classic_names = []

    for word, info in literature.items():
        if len(word) == 2:
            # 检查两个字是否都在字库中
            ch1, ch2 = word[0], word[1]
            if ch1 in hanzi_map and ch2 in hanzi_map:
                # 检查字的属性
                info1 = hanzi_map[ch1]
                info2 = hanzi_map[ch2]

                # 排除不适合的字
                if info1.get('rare_flag') or info2.get('rare_flag'):
                    continue
                if info1.get('difficult_flag') or info2.get('difficult_flag'):
                    continue

                # 检查五行是否适合（喜用神为木，所以优先选木、水属性的字）
                wx1 = info1.get('wuxing', '')
                wx2 = info2.get('wuxing', '')

                # 计算适合度
                score = 0
                book = info.get('book', '') if isinstance(info, dict) else ''
                source = info.get('source', '') if isinstance(info, dict) else ''
                meaning = info.get('meaning', '') if isinstance(info, dict) else ''

                # 经典来源加分
                if 'shijing' in book:
                    score += 4  # 诗经最高
                elif 'chuci' in book:
                    score += 3  # 楚辞次之
                elif 'lunyu' in book or 'mengzi' in book:
                    score += 2  # 论语、孟子
                elif 'zhouyi' in book or 'daodejing' in book:
                    score += 2  # 周易、道德经

                # 五行加分（喜用神为木）
                if wx1 == '木':
                    score += 2
                if wx2 == '木':
                    score += 2
                if wx1 == '水':
                    score += 1
                if wx2 == '水':
                    score += 1

                # 含义加分
                positive_words = ['美好', '高洁', '光明', '宏大', '远大', '贤德', '才智', '吉祥', '安康', '和谐']
                for pw in positive_words:
                    if pw in meaning:
                        score += 1

                if score >= 3:  # 至少3分才入选
                    classic_names.append({
                        'name': word,
                        'ch1': ch1,
                        'ch2': ch2,
                        'source': source,
                        'meaning': meaning,
                        'book': book,
                        'score': score,
                        'wuxing': [wx1, wx2]
                    })

    # 按分数排序
    classic_names.sort(key=lambda x: x['score'], reverse=True)
    return classic_names

def generate_names_with_classic(surname, gender, year, month, day, hour, top_n=10):
    """使用经典文学词汇生成名字"""
    # 获取八字信息
    bazi = get_bazi(year, month, day, hour)
    xiyongshen = bazi.xiyongshen
    jiyongshen = bazi.jiyongshen
    zodiac = bazi.zodiac

    # 获取经典名字候选
    classic_names = get_classic_names_from_literature()

    # 加载数据
    hanzi_map = load_hanzi_db('expanded')
    scoring_data = load_data('expanded')

    # 为每个经典名字计算评分
    scored_names = []
    for item in classic_names:
        name = item['name']
        ch1, ch2 = item['ch1'], item['ch2']

        # 计算五格
        from name_generator import calc_wuge, load_surnames
        surname_map = load_surnames()
        wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)

        # 计算评分
        result = score_name(
            name, surname, scoring_data,
            xiyongshen=xiyongshen, jiyongshen=jiyongshen,
            zodiac=zodiac,
            wuge_numbers=wuge_info['wuge_numbers'],
            sancai_wuxing=wuge_info['sancai_wuxing'],
            literature_map=load_literature_map(),
            surname_chars=list(surname)
        )

        # 添加经典出处信息
        result['classic_source'] = item['source']
        result['classic_meaning'] = item['meaning']
        result['classic_book'] = item['book']

        scored_names.append(result)

    # 按总分排序
    scored_names.sort(key=lambda x: x['total_score'], reverse=True)

    # 返回前top_n个
    return scored_names[:top_n], {
        'year_ganzhi': bazi.year_ganzhi,
        'month_ganzhi': bazi.month_ganzhi,
        'day_ganzhi': bazi.day_ganzhi,
        'hour_ganzhi': bazi.hour_ganzhi,
        'wuxing_count': bazi.wuxing_count,
        'day_master': bazi.day_master,
        'day_master_wuxing': bazi.day_master_wuxing,
        'xiyongshen': xiyongshen,
        'jiyongshen': jiyongshen,
        'zodiac': zodiac,
        'strength': bazi.strength,
        'tiaohou': bazi.tiaohou,
        'nayin': bazi.nayin
    }

# 创建输出目录
output_dir = 'batch_reports'
os.makedirs(output_dir, exist_ok=True)

print('=' * 70)
print(f'  陈姓高质量取名 V3 - 经典文学优先版')
print(f'  日期范围：2026年8月29日 - 9月2日')
print(f'  每时辰：{TOP_N_PER_SHICHEN}个高质量名字（优先经典文学出处）')
print(f'  总计：{len(DATES)}天 × {len(SHICHEN)}时辰 × {TOP_N_PER_SHICHEN}名 = {len(DATES)*len(SHICHEN)*TOP_N_PER_SHICHEN}个名字')
print('=' * 70)
print()

# 存储所有结果
all_results = []
total_names = 0

for year, month, day in DATES:
    date_str = f'{year}-{month:02d}-{day:02d}'
    print(f'【{date_str}】')

    for shichen_name, hour in SHICHEN:
        # 生成名字
        names, bazi_info = generate_names_with_classic(
            SURNAME, GENDER, year, month, day, hour, top_n=TOP_N_PER_SHICHEN
        )

        total_names += len(names)

        # 保存结果
        all_results.append({
            'date': date_str,
            'shichen': shichen_name,
            'hour': hour,
            'bazi': bazi_info,
            'xiyongshen': bazi_info['xiyongshen'],
            'zodiac': bazi_info['zodiac'],
            'candidates': [{
                'name': c['full_name'],
                'score': c['total_score'],
                'grade': c['grade'],
                'scores': c['scores'],
                'classic_source': c.get('classic_source', ''),
                'classic_meaning': c.get('classic_meaning', ''),
                'classic_book': c.get('classic_book', '')
            } for c in names]
        })

        print(f'  {shichen_name}({hour:02d}时): {len(names)}个名字')

    print()

# 生成汇总HTML报告
print('=' * 70)
print('  生成HTML报告...')
print('=' * 70)
print()

# 收集所有名字并排序，找出TOP 10
all_names_flat = []
for r in all_results:
    for c in r['candidates']:
        all_names_flat.append({
            'name': c['name'],
            'score': c['score'],
            'grade': c['grade'],
            'date': r['date'],
            'shichen': r['shichen'],
            'scores': c['scores'],
            'classic_source': c.get('classic_source', ''),
            'classic_meaning': c.get('classic_meaning', ''),
            'classic_book': c.get('classic_book', '')
        })

all_names_flat.sort(key=lambda x: x['score'], reverse=True)
top_10 = all_names_flat[:10]

# 创建汇总HTML
html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈姓高质量取名报告 - 经典文学版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 20px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: white; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #667eea; }
        .summary-card .label { color: #666; margin-top: 5px; }
        .date-section { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .date-title { font-size: 1.5em; color: #333; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }
        .shichen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        .shichen-card { background: #f8f9fa; border-radius: 12px; padding: 15px; }
        .shichen-title { font-weight: bold; color: #667eea; margin-bottom: 10px; font-size: 1.1em; }
        .bazi-info { font-size: 0.85em; color: #666; margin-bottom: 10px; }
        .name-list { display: flex; flex-direction: column; gap: 10px; }
        .name-item { padding: 12px; background: white; border-radius: 8px; border-left: 4px solid #667eea; }
        .name-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
        .name-text { font-size: 1.2em; font-weight: bold; }
        .name-score { color: #667eea; font-weight: bold; font-size: 1.1em; }
        .name-details { font-size: 0.85em; color: #888; margin-bottom: 5px; }
        .name-classic { font-size: 0.9em; color: #666; background: #f0f4ff; padding: 8px; border-radius: 5px; margin-top: 5px; }
        .name-classic .source { color: #667eea; font-weight: bold; }
        .footer { text-align: center; padding: 30px; color: #999; }
        .top-names { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; padding: 25px; margin-bottom: 30px; color: white; }
        .top-names h2 { margin-bottom: 20px; }
        .top-names-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .top-name-card { background: rgba(255,255,255,0.2); border-radius: 10px; padding: 15px; }
        .top-name-card .rank { font-size: 1.2em; font-weight: bold; margin-bottom: 5px; }
        .top-name-card .name { font-size: 1.3em; font-weight: bold; margin-bottom: 5px; }
        .top-name-card .score { opacity: 0.9; margin-bottom: 5px; }
        .top-name-card .source { font-size: 0.9em; opacity: 0.8; }
        .stats { background: white; border-radius: 15px; padding: 25px; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .stats h2 { color: #333; margin-bottom: 15px; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .stat-item { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px; }
        .stat-item .value { font-size: 1.5em; font-weight: bold; color: #667eea; }
        .stat-item .label { color: #666; font-size: 0.9em; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>陈姓高质量取名报告</h1>
            <p>经典文学优先版 | 2026年8月29日 - 9月2日 | 每时辰10个高质量名字</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="number">5</div>
                <div class="label">天数</div>
            </div>
            <div class="summary-card">
                <div class="number">60</div>
                <div class="label">时辰数</div>
            </div>
            <div class="summary-card">
                <div class="number">''' + str(total_names) + '''</div>
                <div class="label">总名字数</div>
            </div>
            <div class="summary-card">
                <div class="number">陈</div>
                <div class="label">姓氏</div>
            </div>
        </div>
'''

# 添加统计信息
score_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
for n in all_names_flat:
    grade = n['grade'][0]
    score_counts[grade] = score_counts.get(grade, 0) + 1

# 统计有经典出处的名字
classic_count = sum(1 for n in all_names_flat if n.get('classic_source'))

html_content += '''
        <div class="stats">
            <h2>📊 分数分布统计</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="value">''' + str(score_counts.get('S', 0)) + '''</div>
                    <div class="label">S极佳 (90+)</div>
                </div>
                <div class="stat-item">
                    <div class="value">''' + str(score_counts.get('A', 0)) + '''</div>
                    <div class="label">A优秀 (80-90)</div>
                </div>
                <div class="stat-item">
                    <div class="value">''' + str(score_counts.get('B', 0)) + '''</div>
                    <div class="label">B良好 (70-80)</div>
                </div>
                <div class="stat-item">
                    <div class="value">''' + str(classic_count) + '''</div>
                    <div class="label">有经典出处</div>
                </div>
            </div>
        </div>
'''

# 添加TOP 10展示
html_content += '''
        <div class="top-names">
            <h2>🏆 TOP 10 最佳名字（经典文学出处）</h2>
            <div class="top-names-list">
'''

for i, n in enumerate(top_10, 1):
    source_info = f'《{n.get("classic_book", "")}》' if n.get('classic_book') else ''
    html_content += f'''
                <div class="top-name-card">
                    <div class="rank">#{i}</div>
                    <div class="name">{n["name"]}</div>
                    <div class="score">{n["score"]}分 {n["grade"]}</div>
                    <div class="source">{source_info} {n.get("classic_source", "")[:30]}</div>
                </div>
'''

html_content += '''
            </div>
        </div>
'''

# 添加每天的数据
for year, month, day in DATES:
    date_str = f'{year}-{month:02d}-{day:02d}'
    html_content += f'''
        <div class="date-section">
            <div class="date-title">📅 {date_str}</div>
            <div class="shichen-grid">
'''

    for shichen_name, hour in SHICHEN:
        # 找到对应的结果
        for r in all_results:
            if r['date'] == date_str and r['hour'] == hour:
                bazi = r['bazi']
                bazi_str = f"{bazi['year_ganzhi']} {bazi['month_ganzhi']} {bazi['day_ganzhi']} {bazi['hour_ganzhi']}"
                xiyongshen = r['xiyongshen']
                zodiac = r['zodiac']

                html_content += f'''
                <div class="shichen-card">
                    <div class="shichen-title">{shichen_name}({hour:02d}时)</div>
                    <div class="bazi-info">八字：{bazi_str} | 喜{xiyongshen} | {zodiac}</div>
                    <div class="name-list">
'''

                for c in r['candidates']:
                    scores = c['scores']
                    details = f"五格{scores['wuge_shuli']} 音韵{scores['yinyun']} 寓意{scores['yiyi']} 字形{scores['zixing']}"
                    classic_info = ''
                    if c.get('classic_source'):
                        classic_info = f'''
                        <div class="name-classic">
                            <span class="source">《{c.get('classic_book', '')}》</span> {c.get('classic_source', '')[:40]}
                        </div>'''

                    html_content += f'''                        <div class="name-item">
                            <div class="name-header">
                                <div class="name-text">{c["name"]}</div>
                                <div class="name-score">{c["score"]}分 {c["grade"]}</div>
                            </div>
                            <div class="name-details">{details}</div>
                            {classic_info}
                        </div>
'''

                html_content += '''
                    </div>
                </div>
'''
                break

    html_content += '''
            </div>
        </div>
'''

html_content += '''
        <div class="footer">
            <p>中华取名大师 - 陈姓高质量取名报告（经典文学版）</p>
            <p>基于八字五行 · 三才五格 · 经典文学 · 声调平仄</p>
            <p>V3.0 算法：经典文学优先 · 三层漏斗筛选 · 乘法扣分制 · 动态权重</p>
        </div>
    </div>
</body>
</html>
'''

# 保存HTML报告
report_path = os.path.join(output_dir, 'chen_classic_report_v3.html')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'  HTML报告已生成: {report_path}')

# 保存JSON数据
json_path = os.path.join(output_dir, 'chen_classic_data_v3.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f'  JSON数据已生成: {json_path}')

# 输出TOP 10
print()
print('=' * 70)
print('  🏆 TOP 10 最佳名字（经典文学出处）')
print('=' * 70)
print()
for i, n in enumerate(top_10, 1):
    book = n.get('classic_book', '')
    source = n.get('classic_source', '')[:30]
    print(f'  {i:2d}. {n["name"]:6s}  {n["score"]:5.1f}分 ({n["grade"]})')
    print(f'      出处：《{book}》 {source}')
    print()

print('=' * 70)
print(f'  完成！共生成 {total_names} 个高质量名字')
print('=' * 70)
