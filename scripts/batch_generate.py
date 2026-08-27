# -*- coding: utf-8 -*-
"""
批量生成名字脚本
陈姓 + 固定末字"骐" + 8月29日-9月2日 + 每时辰30个名字
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
FIXED_LAST_CHAR = '骐'
TOP_N = 30

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
print(f'  批量取名：{SURNAME}姓 + 固定末字"{FIXED_LAST_CHAR}"')
print(f'  日期范围：2026年8月29日 - 9月2日')
print(f'  每时辰：{TOP_N}个名字')
print(f'  总计：{len(DATES)}天 × {len(SHICHEN)}时辰 × {TOP_N}名 = {len(DATES)*len(SHICHEN)*TOP_N}个名字')
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
        result = generate_names(
            surname=SURNAME,
            gender=GENDER,
            birth_year=year, birth_month=month, birth_day=day,
            birth_hour=hour,
            name_length=2,
            top_n=TOP_N,
            fixed_last_char=FIXED_LAST_CHAR
        )

        candidates = result.get('candidates', [])
        total_names += len(candidates)

        # 保存结果
        all_results.append({
            'date': date_str,
            'shichen': shichen_name,
            'hour': hour,
            'bazi': result.get('bazi'),
            'xiyongshen': result.get('xiyongshen'),
            'zodiac': result.get('zodiac'),
            'candidates': [{
                'name': c['full_name'],
                'score': c['total_score'],
                'grade': c['grade'],
                'scores': c['scores']
            } for c in candidates]
        })

        print(f'  {shichen_name}({hour:02d}时): {len(candidates)}个名字')

    print()

# 生成汇总HTML报告
print('=' * 70)
print('  生成HTML报告...')
print('=' * 70)
print()

# 创建汇总HTML
html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈骐 - 批量取名报告</title>
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
        .name-list { display: flex; flex-wrap: wrap; gap: 8px; }
        .name-tag { display: inline-block; padding: 5px 12px; background: linear-gradient(135deg, #667eea20, #764ba220); border-radius: 20px; font-size: 0.9em; }
        .name-tag .score { color: #667eea; font-weight: bold; margin-left: 5px; }
        .footer { text-align: center; padding: 30px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>陈骐 - 批量取名报告</h1>
            <p>2026年8月29日 - 9月2日 | 每时辰30个名字</p>
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
                <div class="number">陈骐</div>
                <div class="label">姓名格式</div>
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
                    html_content += f'                        <span class="name-tag">{c["name"]}<span class="score">{c["score"]}</span></span>\n'

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
            <p>中华取名大师 - 批量取名报告</p>
            <p>基于八字五行 · 三才五格 · 经典文学</p>
        </div>
    </div>
</body>
</html>
'''

# 保存HTML报告
report_path = os.path.join(output_dir, 'chenqi_batch_report.html')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'  HTML报告已生成: {report_path}')

# 保存JSON数据
json_path = os.path.join(output_dir, 'chenqi_batch_data.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f'  JSON数据已生成: {json_path}')

print()
print('=' * 70)
print(f'  完成！共生成 {total_names} 个名字')
print('=' * 70)
