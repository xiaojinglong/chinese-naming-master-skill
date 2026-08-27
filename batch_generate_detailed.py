# -*- coding: utf-8 -*-
"""
批量生成名字脚本（详细报告版）
陈姓 + 固定末字"骐" + 8月29日-9月2日 + 每时辰30个名字
每个时辰生成独立的详细报告
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_tools'))
sys.stdout.reconfigure(encoding='utf-8')

from name_generator import generate_names, load_hanzi_db, calc_wuge, load_surnames
from scoring_engine import load_data
from report_generator import generate_html_report, escape_html, load_literature_refs

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

# 加载数据
hanzi_map = load_hanzi_db('common')
surname_map = load_surnames()
scoring_data = load_data()
literature_refs = load_literature_refs()

# 创建输出目录
output_dir = 'batch_reports'
os.makedirs(output_dir, exist_ok=True)

# 骐字信息
qi_info = hanzi_map.get(FIXED_LAST_CHAR, {})
qi_wuxing = qi_info.get('wuxing', '木')
qi_strokes = qi_info.get('strokes_kangxi', 18)
qi_meaning = qi_info.get('meaning', '骐骥，千里马')

print('=' * 70)
print(f'  批量取名（详细报告版）：{SURNAME}姓 + 固定末字"{FIXED_LAST_CHAR}"')
print(f'  日期范围：2026年8月29日 - 9月2日')
print(f'  每时辰：{TOP_N}个名字（含详细解读）')
print('=' * 70)
print()

def generate_detailed_html(date_str, shichen_name, hour, result):
    """为每个时辰生成详细的HTML报告"""
    bazi = result.get('bazi', {})
    xiyongshen = result.get('xiyongshen', '')
    jiyongshen = result.get('jiyongshen', '')
    zodiac = result.get('zodiac', '')
    candidates = result.get('candidates', [])

    # 生成名字卡片HTML
    cards_html = ""
    for i, c in enumerate(candidates, 1):
        name = c.get('name', '')
        full_name = c.get('full_name', '')
        total_score = c.get('total_score', 0)
        grade = c.get('grade', '')
        scores = c.get('scores', {})

        # 获取首字信息
        first_char = name[0] if name else ''
        first_info = hanzi_map.get(first_char, {})
        first_wuxing = first_info.get('wuxing', '')
        first_strokes = first_info.get('strokes_kangxi', 0)
        first_meaning = first_info.get('meaning', '')
        first_lucky = first_info.get('lucky', '')

        # 检查文学出处
        first_lit = literature_refs.get(first_char, {})
        lit_source = ''
        if first_lit:
            if isinstance(first_lit, dict):
                lit_source = first_lit.get('source', '')
            else:
                lit_source = str(first_lit)

        # 评分理由
        score_reasons = []
        if scores.get('wuxing_match', 0) >= 80:
            score_reasons.append(f'五行补益得力（{scores["wuxing_match"]}分）')
        if scores.get('wuge_shuli', 0) >= 80:
            score_reasons.append(f'五格数理吉祥（{scores["wuge_shuli"]}分）')
        if scores.get('yinyun_fluency', 0) >= 70:
            score_reasons.append(f'音韵流畅优美（{scores["yinyun_fluency"]}分）')
        if scores.get('yiyi_depth', 0) >= 80:
            score_reasons.append(f'寓意深刻隽永（{scores["yiyi_depth"]}分）')
        if scores.get('sancai_config', 0) >= 80:
            score_reasons.append(f'三才配置吉祥（{scores["sancai_config"]}分）')
        if scores.get('zixing_beauty', 0) >= 70:
            score_reasons.append(f'字形美观大方（{scores["zixing_beauty"]}分）')
        if scores.get('shengxiao_compat', 0) >= 70:
            score_reasons.append(f'生肖契合度高（{scores["shengxiao_compat"]}分）')

        reasons_html = ''
        if score_reasons:
            reasons_html = '<div class="reasons">' + ''.join(f'<span class="reason">✓ {r}</span>' for r in score_reasons) + '</div>'

        # 人生寓意
        life_meaning = f'{first_meaning}与骐骥（千里马）结合，寓意{first_meaning}如千里马般杰出，前途无量'

        # 周易关联
        zhouyi_ref = ''
        if first_char in ['乾', '坤', '谦', '益', '泰', '恒', '明']:
            zhouyi_map = {
                '乾': '天行健，君子以自强不息',
                '坤': '地势坤，君子以厚德载物',
                '谦': '谦谦君子，卑以自牧',
                '益': '风雷益，君子以见善则迁',
                '泰': '天地交泰，后以财成天地之道',
                '恒': '不恒其德，或承之羞',
                '明': '明入地中，明夷',
            }
            zhouyi_ref = f'<div class="zhouyi">☯ 周易：{zhouyi_map.get(first_char, "")}</div>'

        # 等级颜色
        grade_color = '#4CAF50' if 'S' in grade or 'A' in grade else '#FF9800' if 'B' in grade else '#9E9E9E'

        cards_html += f'''
        <div class="name-card">
            <div class="card-header">
                <div class="rank">#{i}</div>
                <div class="name">{escape_html(full_name)}</div>
                <div class="score-circle" style="border-color:{grade_color}">
                    <div class="score-num">{total_score}</div>
                    <div class="score-grade">{grade}</div>
                </div>
            </div>
            <div class="card-body">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">首字</div>
                        <div class="info-value">{escape_html(first_char)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">五行</div>
                        <div class="info-value wuxing-{first_wuxing}">{first_wuxing}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">笔画</div>
                        <div class="info-value">{first_strokes}画</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">吉凶</div>
                        <div class="info-value">{first_lucky}</div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">📝 字义解释</div>
                    <div class="section-content">{escape_html(first_meaning)}</div>
                </div>

                <div class="section">
                    <div class="section-title">🎯 寓意</div>
                    <div class="section-content">"{escape_html(first_char)}"与"骐"（千里马）组合，寓意{escape_html(first_meaning)}，如千里马般杰出，前途无量</div>
                </div>

                {f'<div class="section"><div class="section-title">📚 经典出处</div><div class="section-content">{escape_html(lit_source)}</div></div>' if lit_source else ''}

                {f'<div class="section"><div class="section-title">🌟 人生寓意</div><div class="section-content">{escape_html(life_meaning)}</div></div>' if life_meaning else ''}

                {zhouyi_ref}

                <div class="section">
                    <div class="section-title">📊 评分详情</div>
                    <div class="scores-grid">
                        <div class="score-item">
                            <span class="score-label">五行补益</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("wuxing_match", 0)}%"></div></div>
                            <span class="score-val">{scores.get("wuxing_match", 0)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">五格数理</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("wuge_shuli", 0)}%"></div></div>
                            <span class="score-val">{scores.get("wuge_shuli", 0)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">音韵流畅</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("yinyun_fluency", 0)}%"></div></div>
                            <span class="score-val">{scores.get("yinyun_fluency", 0)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">寓意深度</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("yiyi_depth", 0)}%"></div></div>
                            <span class="score-val">{scores.get("yiyi_depth", 0)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">三才配置</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("sancai_config", 0)}%"></div></div>
                            <span class="score-val">{scores.get("sancai_config", 0)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">字形美观</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("zixing_beauty", 0)}%"></div></div>
                            <span class="score-val">{scores.get("zixing_beauty", 0)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">生肖契合</span>
                            <div class="score-bar"><div class="score-fill" style="width:{scores.get("shengxiao_compat", 0)}%"></div></div>
                            <span class="score-val">{scores.get("shengxiao_compat", 0)}</span>
                        </div>
                    </div>
                </div>

                {reasons_html}
            </div>
        </div>
        '''

    # 构建完整HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈骐 - {date_str} {shichen_name} 详细报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: rgba(255,255,255,0.95); border-radius: 20px; padding: 30px; margin-bottom: 25px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 2em; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }}
        .header .info {{ color: #666; font-size: 0.95em; }}
        .header .info span {{ margin: 0 10px; }}
        .bazi-section {{ background: rgba(255,255,255,0.95); border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); }}
        .bazi-title {{ font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 15px; }}
        .bazi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px; }}
        .bazi-item {{ text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea20, #764ba220); border-radius: 12px; }}
        .bazi-label {{ font-size: 0.85em; color: #666; margin-bottom: 5px; }}
        .bazi-value {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .bazi-details {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .detail-item {{ padding: 10px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; }}
        .detail-label {{ color: #666; }}
        .detail-value {{ font-weight: 600; color: #333; }}
        .name-card {{ background: rgba(255,255,255,0.95); border-radius: 15px; margin-bottom: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); overflow: hidden; }}
        .card-header {{ display: flex; align-items: center; padding: 20px; background: linear-gradient(135deg, #f5f7fa, #c3cfe2); border-bottom: 2px solid #eee; }}
        .rank {{ width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; }}
        .name {{ flex: 1; font-size: 1.8em; font-weight: bold; color: #333; letter-spacing: 3px; }}
        .score-circle {{ width: 70px; height: 70px; border: 3px solid; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .score-num {{ font-size: 1.3em; font-weight: bold; color: #333; }}
        .score-grade {{ font-size: 0.65em; color: #666; }}
        .card-body {{ padding: 20px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }}
        .info-item {{ text-align: center; padding: 12px; background: #f8f9fa; border-radius: 10px; }}
        .info-label {{ font-size: 0.8em; color: #666; margin-bottom: 5px; }}
        .info-value {{ font-weight: 600; color: #333; }}
        .wuxing-金 {{ color: #FFD700; }}
        .wuxing-木 {{ color: #228B22; }}
        .wuxing-水 {{ color: #4169E1; }}
        .wuxing-火 {{ color: #FF4500; }}
        .wuxing-土 {{ color: #8B4513; }}
        .section {{ margin-bottom: 15px; }}
        .section-title {{ font-weight: bold; color: #333; margin-bottom: 8px; padding-bottom: 5px; border-bottom: 2px solid #667eea30; }}
        .section-content {{ color: #555; line-height: 1.6; }}
        .scores-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }}
        .score-item {{ display: flex; align-items: center; }}
        .score-label {{ width: 70px; font-size: 0.8em; color: #666; }}
        .score-bar {{ flex: 1; height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden; margin: 0 8px; }}
        .score-fill {{ height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 5px; }}
        .score-val {{ width: 30px; text-align: right; font-weight: 600; font-size: 0.85em; color: #333; }}
        .reasons {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
        .reason {{ padding: 6px 12px; background: #e8f5e9; border-radius: 20px; font-size: 0.85em; color: #2e7d32; }}
        .zhouyi {{ padding: 12px; background: #e8eaf6; border-radius: 10px; margin-top: 10px; color: #283593; }}
        .footer {{ text-align: center; padding: 30px; color: rgba(255,255,255,0.8); font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>陈骐 - 取名详细报告</h1>
            <div class="info">
                <span>📅 {date_str}</span>
                <span>⏰ {shichen_name}({hour:02d}时)</span>
                <span>👤 男</span>
            </div>
        </div>

        <div class="bazi-section">
            <div class="bazi-title">🔮 八字排盘</div>
            <div class="bazi-grid">
                <div class="bazi-item">
                    <div class="bazi-label">年柱</div>
                    <div class="bazi-value">{bazi.get("year_ganzhi", "")}</div>
                </div>
                <div class="bazi-item">
                    <div class="bazi-label">月柱</div>
                    <div class="bazi-value">{bazi.get("month_ganzhi", "")}</div>
                </div>
                <div class="bazi-item">
                    <div class="bazi-label">日柱</div>
                    <div class="bazi-value">{bazi.get("day_ganzhi", "")}</div>
                </div>
                <div class="bazi-item">
                    <div class="bazi-label">时柱</div>
                    <div class="bazi-value">{bazi.get("hour_ganzhi", "")}</div>
                </div>
            </div>
            <div class="bazi-details">
                <div class="detail-item">
                    <span class="detail-label">日主：</span>
                    <span class="detail-value">{bazi.get("day_master", "")}（{bazi.get("day_master_wuxing", "")}）</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">强弱：</span>
                    <span class="detail-value">{bazi.get("strength", "")}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">喜用神：</span>
                    <span class="detail-value" style="color:#667eea;font-weight:bold">{xiyongshen}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">忌用神：</span>
                    <span class="detail-value">{jiyongshen}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">生肖：</span>
                    <span class="detail-value">{zodiac}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">纳音：</span>
                    <span class="detail-value">{bazi.get("nayin", "")}</span>
                </div>
            </div>
        </div>

        <div class="bazi-section">
            <div class="bazi-title">✨ 推荐名字（共{len(candidates)}个）</div>
            <p style="color:#666;margin-bottom:15px">首字 + 骐（{qi_wuxing}行，{qi_strokes}画，{qi_meaning}）</p>
        </div>

        {cards_html}

        <div class="footer">
            <p>中华取名大师 - 详细取名报告</p>
            <p>基于八字五行 · 三才五格 · 经典文学 · 周易智慧</p>
        </div>
    </div>
</body>
</html>'''

    return html


# 开始生成
print('开始生成详细报告...')
print()

total_names = 0
report_count = 0

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

        # 生成详细HTML
        html = generate_detailed_html(date_str, shichen_name, hour, result)

        # 保存文件
        filename = f'chenqi_{date_str}_{shichen_name}.html'
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        report_count += 1
        print(f'  {shichen_name}({hour:02d}时): {len(candidates)}个名字 -> {filename}')

    print()

# 生成索引页
print('生成索引页...')
index_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈骐 - 批量取名报告索引</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 40px; margin-bottom: 30px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .header h1 { font-size: 2.5em; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
        .header p { color: #666; font-size: 1.1em; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #667eea; }
        .summary-card .label { color: #666; margin-top: 5px; }
        .date-section { background: rgba(255,255,255,0.95); border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .date-title { font-size: 1.3em; font-weight: bold; color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }
        .links-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        .link-item { padding: 12px; background: linear-gradient(135deg, #667eea20, #764ba220); border-radius: 10px; text-align: center; transition: all 0.3s; }
        .link-item:hover { background: linear-gradient(135deg, #667eea40, #764ba240); transform: translateY(-2px); }
        .link-item a { text-decoration: none; color: #333; font-weight: 600; }
        .link-item .shichen { font-size: 0.85em; color: #667eea; }
        .footer { text-align: center; padding: 30px; color: rgba(255,255,255,0.8); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>陈骐 - 批量取名报告</h1>
            <p>2026年8月29日 - 9月2日 | 每时辰30个名字 | 详细解读</p>
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
                <div class="number">60</div>
                <div class="label">详细报告</div>
            </div>
        </div>
'''

for year, month, day in DATES:
    date_str = f'{year}-{month:02d}-{day:02d}'
    index_html += f'''
        <div class="date-section">
            <div class="date-title">📅 {date_str}</div>
            <div class="links-grid">
'''
    for shichen_name, hour in SHICHEN:
        filename = f'chenqi_{date_str}_{shichen_name}.html'
        index_html += f'''
                <div class="link-item">
                    <a href="{filename}">
                        <div class="shichen">{shichen_name}</div>
                        <div>{hour:02d}时</div>
                    </a>
                </div>
'''
    index_html += '''
            </div>
        </div>
'''

index_html += '''
        <div class="footer">
            <p>中华取名大师 - 批量取名报告</p>
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

print()
print('=' * 70)
print(f'  完成！')
print(f'  总名字数：{total_names}')
print(f'  报告数：{report_count}个详细报告 + 1个索引页')
print(f'  输出目录：{output_dir}/')
print(f'  入口文件：{output_dir}/index.html')
print('=' * 70)
