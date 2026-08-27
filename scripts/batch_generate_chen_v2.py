# -*- coding: utf-8 -*-
"""
陈姓高质量取名脚本 V2
================
陈姓 + 不固定末字 + 8月29日-9月2日 + 每时辰10个高质量名字
策略：每个时辰独立生成，确保每个时辰都有10个名字
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_tools'))
sys.stdout.reconfigure(encoding='utf-8')

from name_generator import generate_names
from report_generator import generate_html_report

# 配置
SURNAME = '陈'
GENDER = 'male'
TOP_N_PER_SHICHEN = 10  # 每时辰10个名字

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

# 创建输出目录
output_dir = 'batch_reports'
os.makedirs(output_dir, exist_ok=True)

print('=' * 70)
print(f'  陈姓高质量取名 V2')
print(f'  日期范围：2026年8月29日 - 9月2日')
print(f'  每时辰：{TOP_N_PER_SHICHEN}个高质量名字')
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
        # 生成名字（多生成一些以便筛选）
        result = generate_names(
            surname=SURNAME,
            gender=GENDER,
            birth_year=year, birth_month=month, birth_day=day,
            birth_hour=hour,
            name_length=2,
            top_n=20,  # 多生成一些
            style=None
        )

        candidates = result.get('candidates', [])

        # 取前10个（已经按总分排序）
        top_candidates = candidates[:TOP_N_PER_SHICHEN]
        total_names += len(top_candidates)

        # 保存结果
        all_results.append({
            'date': date_str,
            'shichen': shichen_name,
            'hour': hour,
            'bazi': result.get('bazi'),
            'xiyongshen': result.get('xiyongshen'),
            'jiyongshen': result.get('jiyongshen'),
            'zodiac': result.get('zodiac'),
            'candidates': [{
                'name': c['full_name'],
                'score': c['total_score'],
                'grade': c['grade'],
                'scores': c['scores']
            } for c in top_candidates]
        })

        print(f'  {shichen_name}({hour:02d}时): {len(top_candidates)}个名字')

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
            'scores': c['scores']
        })

all_names_flat.sort(key=lambda x: x['score'], reverse=True)
top_10 = all_names_flat[:10]

# 创建汇总HTML
html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈姓高质量取名报告</title>
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
        .name-list { display: flex; flex-direction: column; gap: 8px; }
        .name-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: white; border-radius: 8px; border-left: 3px solid #667eea; }
        .name-text { font-size: 1.1em; font-weight: bold; }
        .name-score { color: #667eea; font-weight: bold; }
        .name-grade { font-size: 0.85em; color: #888; margin-left: 5px; }
        .name-details { font-size: 0.8em; color: #999; margin-top: 3px; }
        .footer { text-align: center; padding: 30px; color: #999; }
        .top-names { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; padding: 25px; margin-bottom: 30px; color: white; }
        .top-names h2 { margin-bottom: 20px; }
        .top-names-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }
        .top-name-card { background: rgba(255,255,255,0.2); border-radius: 10px; padding: 15px; text-align: center; }
        .top-name-card .rank { font-size: 1.5em; font-weight: bold; }
        .top-name-card .name { font-size: 1.3em; margin: 5px 0; }
        .top-name-card .score { opacity: 0.9; }
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
            <p>2026年8月29日 - 9月2日 | 每时辰10个高质量名字</p>
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
                    <div class="value">''' + str(score_counts.get('C', 0) + score_counts.get('D', 0) + score_counts.get('F', 0)) + '''</div>
                    <div class="label">C及以下 (<70)</div>
                </div>
            </div>
        </div>
'''

# 添加TOP 10展示
html_content += '''
        <div class="top-names">
            <h2>🏆 TOP 10 最佳名字</h2>
            <div class="top-names-grid">
'''

for i, n in enumerate(top_10, 1):
    html_content += f'''
                <div class="top-name-card">
                    <div class="rank">#{i}</div>
                    <div class="name">{n["name"]}</div>
                    <div class="score">{n["score"]}分 {n["grade"]}</div>
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
                    html_content += f'''                        <div class="name-item">
                            <div>
                                <div class="name-text">{c["name"]}</div>
                                <div class="name-details">{details}</div>
                            </div>
                            <div>
                                <span class="name-score">{c["score"]}</span>
                                <span class="name-grade">{c["grade"]}</span>
                            </div>
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
            <p>中华取名大师 - 陈姓高质量取名报告</p>
            <p>基于八字五行 · 三才五格 · 经典文学 · 声调平仄</p>
            <p>V2.0 算法：三层漏斗筛选 · 乘法扣分制 · 动态权重 · 4组推荐</p>
        </div>
    </div>
</body>
</html>
'''

# 保存HTML报告
report_path = os.path.join(output_dir, 'chen_high_quality_report_v2.html')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'  HTML报告已生成: {report_path}')

# 保存JSON数据
json_path = os.path.join(output_dir, 'chen_high_quality_data_v2.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f'  JSON数据已生成: {json_path}')

# 输出TOP 10
print()
print('=' * 70)
print('  🏆 TOP 10 最佳名字')
print('=' * 70)
print()
for i, n in enumerate(top_10, 1):
    print(f'  {i:2d}. {n["name"]:6s}  {n["score"]:5.1f}分 ({n["grade"]}) | {n["date"]} {n["shichen"]}')

print()
print('=' * 70)
print(f'  完成！共生成 {total_names} 个高质量名字')
print('=' * 70)
