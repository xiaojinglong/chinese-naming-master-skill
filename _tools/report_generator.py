# -*- coding: utf-8 -*-
"""
HTML报告生成器
==============
为取名结果生成精致的HTML报告，包含详细的名字解读。

报告内容：
- 八字排盘分析
- 每个候选名的详细解读（评分、含义、出处、寓意、周易相关、人生寓意）
- 评分维度雷达图
- 精致的视觉设计
"""
import html as html_module
import json
import os
import webbrowser
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))


def escape_html(text):
    """HTML转义，防止XSS"""
    if text is None:
        return ''
    return html_module.escape(str(text))


def load_literature_refs():
    """加载文学引用库"""
    refs = {}
    # 诗词意象
    shici_path = os.path.join(BASE, '..', '03-文化资料', '诗词意象库.json')
    if os.path.exists(shici_path):
        with open(shici_path, encoding='utf-8') as f:
            data = json.load(f)
        for item in data.get('items', []):
            imagery = item.get('imagery', '')
            if imagery:
                refs[imagery] = {
                    'source': item.get('poem_ref', ''),
                    'meaning': item.get('meaning', ''),
                    'theme': item.get('theme', '')
                }
    # 成语典故
    chengyu_path = os.path.join(BASE, '..', '03-文化资料', '成语典故库.json')
    if os.path.exists(chengyu_path):
        with open(chengyu_path, encoding='utf-8') as f:
            data = json.load(f)
        for item in data.get('items', []):
            for word in item.get('usable_words', []):
                refs[word] = {
                    'source': item.get('source', ''),
                    'meaning': item.get('meaning', ''),
                    'idiom': item.get('idiom', '')
                }
    return refs


def get_char_analysis(char, hanzi_map, literature_refs):
    """获取单字的详细分析"""
    info = hanzi_map.get(char, {})
    analysis = {
        'char': char,
        'wuxing': info.get('wuxing', '未知'),
        'strokes': info.get('strokes_kangxi', 0),
        'meaning': info.get('meaning', ''),
        'kangxi_meaning': info.get('kangxi_meaning', ''),
        'radical': info.get('radical', ''),
        'pinyin': info.get('pinyin_tone', ''),
        'lucky': info.get('lucky', ''),
        'literature': literature_refs.get(char, None),
        'style_tags': info.get('style_tags', []),
    }
    return analysis


def get_zhouyi_reference(name, chars_info):
    """获取周易相关引用"""
    # 常见的周易卦辞与名字的关联
    zhouyi_refs = {
        '恒': {'hexagram': '恒卦', 'quote': '不恒其德，或承之羞', 'meaning': '持之以恒，德行恒久'},
        '乾': {'hexagram': '乾卦', 'quote': '天行健，君子以自强不息', 'meaning': '刚健进取，自强不息'},
        '坤': {'hexagram': '坤卦', 'quote': '地势坤，君子以厚德载物', 'meaning': '厚德载物，包容万象'},
        '谦': {'hexagram': '谦卦', 'quote': '谦谦君子，卑以自牧', 'meaning': '谦虚谨慎，修养品德'},
        '益': {'hexagram': '益卦', 'quote': '风雷益，君子以见善则迁', 'meaning': '见善则迁，有过则改'},
        '泰': {'hexagram': '泰卦', 'quote': '天地交泰，后以财成天地之道', 'meaning': '通达亨泰，和谐顺遂'},
        '明': {'hexagram': '明夷卦', 'quote': '明入地中，明夷', 'meaning': '光明磊落，智慧通达'},
        '泽': {'hexagram': '兑卦', 'quote': '丽泽兑，君子以朋友讲习', 'meaning': '润泽万物，恩泽广布'},
        '雨': {'hexagram': '需卦', 'quote': '云上于天，需', 'meaning': '恩泽如雨，润物无声'},
        '海': {'hexagram': '坎卦', 'quote': '水洊至，习坎', 'meaning': '胸怀如海，包容万物'},
        '浩': {'hexagram': '乾卦', 'quote': '大哉乾元，万物资始', 'meaning': '浩然正气，刚正不阿'},
        '鹏': {'hexagram': '渐卦', 'quote': '鸿渐于陆，其羽可用为仪', 'meaning': '鹏程万里，志向高远'},
        '德': {'hexagram': '坤卦', 'quote': '地势坤，君子以厚德载物', 'meaning': '品德高尚，德行天下'},
    }
    result = []
    for char_info in chars_info:
        char = char_info['char']
        if char in zhouyi_refs:
            result.append(zhouyi_refs[char])
    return result


def get_life_meaning(name, chars_info, bazi_info):
    """生成人生寓意解读"""
    meanings = []
    for char_info in chars_info:
        char = char_info['char']
        meaning = char_info.get('meaning', '')
        if meaning:
            meanings.append(f"{char}（{meaning}）")

    # 根据五行和字义组合生成人生寓意
    wuxing_chars = [c for c in chars_info if c.get('wuxing')]
    if len(wuxing_chars) >= 2:
        wx1 = wuxing_chars[0].get('wuxing', '')
        wx2 = wuxing_chars[-1].get('wuxing', '')

        # 五行相生关系
        sheng_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        if sheng_map.get(wx1) == wx2:
            return f"{''.join(meanings)}，五行{wx1}生{wx2}，相生相助，人生顺遂通达"
        elif sheng_map.get(wx2) == wx1:
            return f"{''.join(meanings)}，五行{wx2}生{wx1}，根基稳固，厚积薄发"

    return f"{''.join(meanings)}，寓意美好，人生光明"


def generate_html_report(result, output_path=None):
    """
    生成HTML报告

    参数：
      result: generate_names() 的返回结果
      output_path: 输出文件路径，默认为当前目录下的 naming_report.html
    """
    # 动态导入避免循环引用
    import sys
    sys.path.insert(0, BASE)
    from name_generator import load_hanzi_db

    hanzi_map = load_hanzi_db()
    literature_refs = load_literature_refs()

    # 准备数据
    input_info = result.get('input', {})
    bazi_info = result.get('bazi', {})
    candidates = result.get('candidates', [])
    xiyongshen = result.get('xiyongshen', '')
    jiyongshen = result.get('jiyongshen', '')
    zodiac = result.get('zodiac', '')

    # 生成时间
    gen_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')

    # 构建候选名详细数据
    detailed_candidates = []
    for i, cand in enumerate(candidates, 1):
        name = cand.get('name', '')
        surname = cand.get('surname', '')
        full_name = cand.get('full_name', '')

        # 获取每个字的详细分析
        chars_info = []
        for ch in name:
            chars_info.append(get_char_analysis(ch, hanzi_map, literature_refs))

        # 周易引用
        zhouyi_refs = get_zhouyi_reference(name, chars_info)

        # 人生寓意
        life_meaning = get_life_meaning(name, chars_info, bazi_info)

        # 文学出处
        literature_sources = []
        for ci in chars_info:
            if ci.get('literature'):
                lit = ci['literature']
                literature_sources.append({
                    'char': ci['char'],
                    'source': lit.get('source', ''),
                    'meaning': lit.get('meaning', ''),
                    'idiom': lit.get('idiom', '')
                })

        # 评分理由
        scores = cand.get('scores', {})
        score_reasons = []
        if scores.get('wuxing_match', 0) >= 80:
            score_reasons.append(f"五行补益得力（{scores['wuxing_match']}分），与喜用神高度契合")
        if scores.get('wuge_shuli', 0) >= 80:
            score_reasons.append(f"五格数理吉祥（{scores['wuge_shuli']}分），数理配置良好")
        if scores.get('yinyun_fluency', 0) >= 70:
            score_reasons.append(f"音韵流畅优美（{scores['yinyun_fluency']}分），声调搭配和谐")
        if scores.get('yiyi_depth', 0) >= 80:
            score_reasons.append(f"寓意深刻隽永（{scores['yiyi_depth']}分），文化底蕴丰富")
        if scores.get('sancai_config', 0) >= 80:
            score_reasons.append(f"三才配置吉祥（{scores['sancai_config']}分），天地人和谐")
        if scores.get('zixing_beauty', 0) >= 70:
            score_reasons.append(f"字形美观大方（{scores['zixing_beauty']}分），结构协调匀称")
        if scores.get('shengxiao_compat', 0) >= 70:
            score_reasons.append(f"生肖契合度高（{scores['shengxiao_compat']}分），与{zodiac}年相宜")

        detailed_candidates.append({
            'rank': i,
            'full_name': full_name,
            'name': name,
            'surname': surname,
            'total_score': cand.get('total_score', 0),
            'grade': cand.get('grade', ''),
            'scores': scores,
            'chars_info': chars_info,
            'zhouyi_refs': zhouyi_refs,
            'life_meaning': life_meaning,
            'literature_sources': literature_sources,
            'score_reasons': score_reasons,
        })

    # 生成HTML
    html = _build_html_template(
        input_info=input_info,
        bazi_info=bazi_info,
        candidates=detailed_candidates,
        xiyongshen=xiyongshen,
        jiyongshen=jiyongshen,
        zodiac=zodiac,
        gen_time=gen_time
    )

    # 保存文件
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'naming_report.html')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def _build_html_template(input_info, bazi_info, candidates, xiyongshen, jiyongshen, zodiac, gen_time):
    """构建HTML模板"""

    # 评分维度雷达图数据
    score_labels = ['五行补益', '五格数理', '音韵流畅', '寓意深度', '三才配置', '字形美观', '生肖契合']
    score_keys = ['wuxing_match', 'wuge_shuli', 'yinyun_fluency', 'yiyi_depth', 'sancai_config', 'zixing_beauty', 'shengxiao_compat']

    # 生成候选名卡片HTML
    cards_html = ""
    for cand in candidates:
        # 评分维度条形图
        bars_html = ""
        for label, key in zip(score_labels, score_keys):
            score = cand['scores'].get(key, 0)
            color = _get_score_color(score)
            bars_html += f'''
            <div class="score-bar-item">
                <span class="score-label">{label}</span>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width:{score}%;background:{color}"></div>
                </div>
                <span class="score-value">{score}</span>
            </div>'''

        # 字义解读
        chars_html = ""
        for ci in cand['chars_info']:
            lit_html = ""
            if ci.get('literature'):
                lit = ci['literature']
                lit_html = f'<div class="char-literature">📚 {lit.get("source", "")}</div>'

            chars_html += f'''
            <div class="char-card">
                <div class="char-main">{ci['char']}</div>
                <div class="char-info">
                    <div>五行：<span class="wuxing-tag wuxing-{ci['wuxing']}">{ci['wuxing']}</span></div>
                    <div>笔画：{ci['strokes']}画</div>
                    <div>含义：{ci['meaning']}</div>
                    {f'<div>康熙释义：{ci["kangxi_meaning"]}</div>' if ci.get('kangxi_meaning') else ''}
                    {f'<div>吉凶：{ci["lucky"]}</div>' if ci.get('lucky') else ''}
                </div>
                {lit_html}
            </div>'''

        # 周易引用
        zhouyi_html = ""
        if cand['zhouyi_refs']:
            for ref in cand['zhouyi_refs']:
                zhouyi_html += f'''
                <div class="zhouyi-item">
                    <div class="zhouyi-hexagram">☯ {ref['hexagram']}</div>
                    <div class="zhouyi-quote">「{ref['quote']}」</div>
                    <div class="zhouyi-meaning">{ref['meaning']}</div>
                </div>'''

        # 文学出处
        literature_html = ""
        if cand['literature_sources']:
            for lit in cand['literature_sources']:
                idiom_text = f"（{lit['idiom']}）" if lit.get('idiom') else ""
                literature_html += f'''
                <div class="literature-item">
                    <span class="literature-char">「{lit['char']}」</span>
                    <span class="literature-source">{lit['source']}{idiom_text}</span>
                </div>'''

        # 评分理由
        reasons_html = ""
        if cand['score_reasons']:
            reasons_html = '<div class="reasons-list">'
            for reason in cand['score_reasons']:
                reasons_html += f'<div class="reason-item">✓ {reason}</div>'
            reasons_html += '</div>'

        # 等级颜色
        grade = cand['grade']
        grade_color = '#4CAF50' if 'S' in grade or 'A' in grade else '#FF9800' if 'B' in grade else '#9E9E9E'

        cards_html += f'''
        <div class="name-card" id="name-{cand['rank']}">
            <div class="card-header">
                <div class="rank-badge">#{cand['rank']}</div>
                <div class="name-title">{cand['full_name']}</div>
                <div class="score-circle" style="border-color:{grade_color}">
                    <div class="score-number">{cand['total_score']}</div>
                    <div class="score-grade">{grade}</div>
                </div>
            </div>

            <div class="card-body">
                <div class="section">
                    <h3 class="section-title">📝 字义解读</h3>
                    <div class="chars-container">{chars_html}</div>
                </div>

                <div class="section">
                    <h3 class="section-title">📊 评分详情</h3>
                    <div class="scores-container">{bars_html}</div>
                </div>

                {'<div class="section"><h3 class="section-title">⭐ 评分理由</h3>{reasons_html}</div>' if reasons_html else ''}

                <div class="section">
                    <h3 class="section-title">🌟 人生寓意</h3>
                    <div class="life-meaning">{cand['life_meaning']}</div>
                </div>

                {'<div class="section"><h3 class="section-title">☯ 周易关联</h3>' + zhouyi_html + '</div>' if zhouyi_html else ''}

                {'<div class="section"><h3 class="section-title">📚 经典出处</h3>' + literature_html + '</div>' if literature_html else ''}
            </div>
        </div>'''

    # 八字信息
    bazi_section = ""
    if bazi_info:
        wuxing_data = bazi_info.get('wuxing_count', {})
        wuxing_bars = ""
        for wx, count in [('金', wuxing_data.get('金', 0)), ('木', wuxing_data.get('木', 0)),
                          ('水', wuxing_data.get('水', 0)), ('火', wuxing_data.get('火', 0)),
                          ('土', wuxing_data.get('土', 0))]:
            pct = min(100, int(count * 20))
            wuxing_bars += f'''
            <div class="wuxing-bar-item">
                <span class="wuxing-name">{wx}</span>
                <div class="wuxing-bar-bg">
                    <div class="wuxing-bar-fill wuxing-{wx}" style="width:{pct}%"></div>
                </div>
                <span class="wuxing-count">{count}</span>
            </div>'''

        bazi_section = f'''
        <div class="section bazi-section">
            <h2 class="section-title">🔮 八字排盘分析</h2>
            <div class="bazi-grid">
                <div class="bazi-item">
                    <div class="bazi-label">年柱</div>
                    <div class="bazi-value">{bazi_info.get('year_ganzhi', '')}</div>
                </div>
                <div class="bazi-item">
                    <div class="bazi-label">月柱</div>
                    <div class="bazi-value">{bazi_info.get('month_ganzhi', '')}</div>
                </div>
                <div class="bazi-item">
                    <div class="bazi-label">日柱</div>
                    <div class="bazi-value">{bazi_info.get('day_ganzhi', '')}</div>
                </div>
                <div class="bazi-item">
                    <div class="bazi-label">时柱</div>
                    <div class="bazi-value">{bazi_info.get('hour_ganzhi', '')}</div>
                </div>
            </div>
            <div class="bazi-details">
                <div class="detail-item">
                    <span class="detail-label">日主：</span>
                    <span class="detail-value">{bazi_info.get('day_master', '')}（{bazi_info.get('day_master_wuxing', '')}）</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">强弱：</span>
                    <span class="detail-value">{bazi_info.get('strength', '')}（{bazi_info.get('strength_score', '')}分）</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">喜用神：</span>
                    <span class="detail-value highlight">{xiyongshen}</span>
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
                    <span class="detail-value">{bazi_info.get('nayin', '')}</span>
                </div>
            </div>
            <div class="wuxing-chart">
                <h3>五行分布</h3>
                {wuxing_bars}
            </div>
        </div>'''

    # 输入信息
    birth_str = input_info.get('birth', '未提供')
    gender_str = {'male': '男', 'female': '女'}.get(input_info.get('gender'), '未指定')
    style_str = input_info.get('style', '默认')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中华取名大师 - 命名报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* 页头 */
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .info-tags {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .info-tag {{
            padding: 8px 20px;
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            border-radius: 25px;
            font-size: 0.95em;
            color: #333;
        }}

        /* 八字区域 */
        .bazi-section {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        }}

        .bazi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}

        .bazi-item {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea20, #764ba220);
            border-radius: 15px;
            border: 2px solid #667eea40;
        }}

        .bazi-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
        }}

        .bazi-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}

        .bazi-details {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}

        .detail-item {{
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
        }}

        .detail-label {{
            color: #666;
            font-size: 0.9em;
        }}

        .detail-value {{
            color: #333;
            font-weight: 600;
        }}

        .detail-value.highlight {{
            color: #667eea;
            font-size: 1.2em;
        }}

        .wuxing-chart {{
            margin-top: 20px;
        }}

        .wuxing-chart h3 {{
            margin-bottom: 15px;
            color: #333;
        }}

        .wuxing-bar-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}

        .wuxing-name {{
            width: 40px;
            font-weight: bold;
            color: #333;
        }}

        .wuxing-bar-bg {{
            flex: 1;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 10px;
        }}

        .wuxing-bar-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}

        .wuxing-金 {{ background: linear-gradient(90deg, #C0C0C0, #FFD700); }}
        .wuxing-木 {{ background: linear-gradient(90deg, #90EE90, #228B22); }}
        .wuxing-水 {{ background: linear-gradient(90deg, #87CEEB, #4169E1); }}
        .wuxing-火 {{ background: linear-gradient(90deg, #FFA500, #FF4500); }}
        .wuxing-土 {{ background: linear-gradient(90deg, #DEB887, #8B4513); }}

        .wuxing-count {{
            width: 30px;
            text-align: right;
            color: #666;
        }}

        /* 名字卡片 */
        .name-card {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .name-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}

        .card-header {{
            display: flex;
            align-items: center;
            padding: 25px 30px;
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            border-bottom: 2px solid #eee;
        }}

        .rank-badge {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
            font-weight: bold;
            margin-right: 20px;
        }}

        .name-title {{
            flex: 1;
            font-size: 2em;
            font-weight: bold;
            color: #333;
            letter-spacing: 5px;
        }}

        .score-circle {{
            width: 80px;
            height: 80px;
            border: 4px solid;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}

        .score-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}

        .score-grade {{
            font-size: 0.7em;
            color: #666;
        }}

        .card-body {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 25px;
        }}

        .section-title {{
            font-size: 1.2em;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea30;
        }}

        /* 字义卡片 */
        .chars-container {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .char-card {{
            flex: 1;
            min-width: 150px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            border-radius: 15px;
            text-align: center;
        }}

        .char-main {{
            font-size: 3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}

        .char-info {{
            text-align: left;
            font-size: 0.9em;
            color: #555;
            line-height: 1.8;
        }}

        .char-literature {{
            margin-top: 10px;
            padding: 8px;
            background: #fff3e0;
            border-radius: 8px;
            font-size: 0.85em;
            color: #e65100;
        }}

        .wuxing-tag {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        /* 评分条 */
        .scores-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }}

        .score-bar-item {{
            display: flex;
            align-items: center;
        }}

        .score-label {{
            width: 70px;
            font-size: 0.85em;
            color: #666;
        }}

        .score-bar-bg {{
            flex: 1;
            height: 12px;
            background: #f0f0f0;
            border-radius: 6px;
            overflow: hidden;
            margin: 0 10px;
        }}

        .score-bar-fill {{
            height: 100%;
            border-radius: 6px;
            transition: width 0.3s ease;
        }}

        .score-value {{
            width: 35px;
            text-align: right;
            font-weight: 600;
            color: #333;
            font-size: 0.9em;
        }}

        /* 评分理由 */
        .reasons-list {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}

        .reason-item {{
            padding: 10px 15px;
            background: #e8f5e9;
            border-radius: 10px;
            color: #2e7d32;
            font-size: 0.9em;
        }}

        /* 人生寓意 */
        .life-meaning {{
            padding: 20px;
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
            border-radius: 15px;
            color: #e65100;
            font-size: 1.05em;
            line-height: 1.8;
        }}

        /* 周易关联 */
        .zhouyi-item {{
            padding: 15px;
            background: linear-gradient(135deg, #e8eaf6, #c5cae9);
            border-radius: 12px;
            margin-bottom: 10px;
        }}

        .zhouyi-hexagram {{
            font-size: 1.1em;
            font-weight: bold;
            color: #283593;
            margin-bottom: 5px;
        }}

        .zhouyi-quote {{
            font-style: italic;
            color: #3949ab;
            margin: 8px 0;
        }}

        .zhouyi-meaning {{
            color: #5c6bc0;
            font-size: 0.95em;
        }}

        /* 文学出处 */
        .literature-item {{
            padding: 12px 15px;
            background: #fce4ec;
            border-radius: 10px;
            margin-bottom: 8px;
        }}

        .literature-char {{
            font-weight: bold;
            color: #c62828;
            margin-right: 10px;
        }}

        .literature-source {{
            color: #d32f2f;
        }}

        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
        }}

        /* 响应式 */
        @media (max-width: 768px) {{
            .bazi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .bazi-details {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .scores-container {{
                grid-template-columns: 1fr;
            }}
            .reasons-list {{
                grid-template-columns: 1fr;
            }}
            .name-title {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>中华取名大师</h1>
            <div class="subtitle">基于八字五行 · 三才五格 · 经典文学 · 周易智慧</div>
            <div class="info-tags">
                <span class="info-tag">👤 姓氏：{input_info.get('surname', '')}</span>
                <span class="info-tag">⚧ 性别：{gender_str}</span>
                <span class="info-tag">📅 出生：{birth_str}</span>
                <span class="info-tag">🎨 风格：{style_str}</span>
                <span class="info-tag">📅 报告生成：{gen_time}</span>
            </div>
        </div>

        {bazi_section}

        <div class="section" style="background:rgba(255,255,255,0.95);border-radius:20px;padding:30px;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.08);">
            <h2 class="section-title">✨ 推荐名字（共{len(candidates)}个）</h2>
            <p style="color:#666;margin-bottom:20px;">以下名字根据八字喜用神、五格数理、音韵寓意等多维度综合评分排序</p>
        </div>

        {cards_html}

        <div class="footer">
            <p>中华取名大师 · 传承千年命名智慧</p>
            <p>基于姓名学原理，结合现代数据分析，仅供参考</p>
        </div>
    </div>
</body>
</html>'''

    return html


def _get_score_color(score):
    """根据分数返回颜色"""
    if score >= 90:
        return '#4CAF50'  # 绿色
    elif score >= 80:
        return '#8BC34A'  # 浅绿
    elif score >= 70:
        return '#FFC107'  # 黄色
    elif score >= 60:
        return '#FF9800'  # 橙色
    else:
        return '#F44336'  # 红色


if __name__ == '__main__':
    # 测试生成报告
    from name_generator import generate_names

    result = generate_names(
        surname='李',
        gender='male',
        birth_year=2024, birth_month=3, birth_day=15, birth_hour=10,
        name_length=2,
        top_n=10,
        style='大气'
    )

    output = generate_html_report(result)
    print(f'报告已生成：{output}')
    webbrowser.open(f'file://{os.path.abspath(output)}')
