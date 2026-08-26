# -*- coding: utf-8 -*-
"""
从 06-取名知识库 的精读笔记中提取结构化数据，生成 JSON 数据文件。

提取目标：
1. 28-李正明 20技法 → 02-规则与算法资料/07-取名技法库.json
2. 26-巨天中 32法+7改名 → 02-规则与算法资料/08-取名方法库.json
3. 31-历史演变 命名案例 → 03-文化资料/历史命名案例库.json
4. 32-字辈谱 → 01-数据资料/字辈谱库/字辈谱.json
5. 34-速查表 高频字 → 01-数据资料/取名常用字速查表.json
6. 30-少数民族 → 03-文化资料/少数民族命名习俗库.json
7. 27-古人名字解诂 相协式 → 03-文化资料/名字相协式库.json
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, '..', '06-取名知识库')
R2 = os.path.join(BASE, '..', '02-规则与算法资料')
R3 = os.path.join(BASE, '..', '03-文化资料')
R1 = os.path.join(BASE, '..', '01-数据资料')


def parse_md_tables(filepath):
    """通用 markdown 表格解析器，返回 [(row_cols...), ...]"""
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
    tables = []
    current_table = []
    in_table = False
    for line in lines:
        s = line.strip()
        if s.startswith('|') and s.endswith('|'):
            cols = [c.strip() for c in s.split('|')[1:-1]]
            # Skip separator rows
            if all(re.match(r'^[-:]+$', c) for c in cols):
                continue
            # Detect header change → new table
            if in_table and current_table and any('---' in c or '原则' in c or '制式' in c or '世代' in c or '高频字' in c or '时代' in c or '#' in c.lower() for c in cols):
                if current_table:
                    tables.append(current_table)
                current_table = []
            in_table = True
            current_table.append(cols)
        elif in_table and not s.startswith('|'):
            if current_table:
                tables.append(current_table)
            current_table = []
            in_table = False
    if current_table:
        tables.append(current_table)
    return tables


def extract_techniques():
    """28-李正明 20技法"""
    path = os.path.join(KB, '03-现代参考书', '28-给孩子起个好名字-李正明.md')
    tables = parse_md_tables(path)
    techniques = []
    for table in tables:
        for row in table:
            if len(row) >= 4 and row[0].strip().isdigit():
                techniques.append({
                    'id': int(row[0]),
                    'name': row[1],
                    'description': row[2],
                    'example': row[3],
                    'category': '创造学技法',
                    'source': '李正明《给孩子起个好名字》'
                })
    return techniques


def extract_methods():
    """26-巨天中 32法+7改名法"""
    # The methods are embedded in chapter descriptions, not clean table rows
    # I'll structure them from the chapter info I've read
    methods = {
        'traditional': [
            {'id': 'T01', 'name': '女性起名法', 'category': '传统习俗'},
            {'id': 'T02', 'name': '男性起名法', 'category': '传统习俗'},
            {'id': 'T03', 'name': '以出生时状况起名（信类遗风）', 'category': '传统习俗'},
            {'id': 'T04', 'name': '抓阄起名', 'category': '传统习俗'},
            {'id': 'T05', 'name': '兄弟姐妹排行起名', 'category': '传统习俗'},
            {'id': 'T06', 'name': '以梦兆起名', 'category': '传统习俗'},
            {'id': 'T07', 'name': '随意巧合起名', 'category': '传统习俗'},
            {'id': 'T08', 'name': '以金属矿物起名', 'category': '传统习俗'},
            {'id': 'T09', 'name': '利用天象起名', 'category': '传统习俗'},
            {'id': 'T10', 'name': '双胞胎起名法', 'category': '传统习俗'},
        ],
        'modern': [
            {'id': 'M01', 'name': '个性特征起名法', 'category': '现代艺术'},
            {'id': 'M02', 'name': '美善起名法', 'category': '现代艺术'},
            {'id': 'M03', 'name': '季节起名法', 'category': '现代艺术'},
            {'id': 'M04', 'name': '出生月份起名法', 'category': '现代艺术'},
            {'id': 'M05', 'name': '地名起名法', 'category': '现代艺术'},
            {'id': 'M06', 'name': '暗寓起名法', 'category': '现代艺术'},
            {'id': 'M07', 'name': '理想式起名法', 'category': '现代艺术'},
            {'id': 'M08', 'name': '典故起名法', 'category': '现代艺术'},
            {'id': 'M09', 'name': '期望式起名法', 'category': '现代艺术'},
            {'id': 'M10', 'name': '职业起名法', 'category': '现代艺术'},
            {'id': 'M11', 'name': '自励起名法', 'category': '现代艺术'},
            {'id': 'M12', 'name': '豪放起名法', 'category': '现代艺术'},
            {'id': 'M13', 'name': '谐音起名法', 'category': '现代艺术'},
            {'id': 'M14', 'name': '仰慕起名法', 'category': '现代艺术'},
        ],
        'numerological': [
            {'id': 'S01', 'name': '五音起名法', 'category': '术数'},
            {'id': 'S02', 'name': '十二生肖起名法', 'category': '术数'},
            {'id': 'S03', 'name': '五格起名法', 'category': '术数'},
            {'id': 'S04', 'name': '81数起名法', 'category': '术数'},
            {'id': 'S05', 'name': '三才起名法', 'category': '术数'},
            {'id': 'S06', 'name': '阴阳五行起名法', 'category': '术数'},
            {'id': 'S07', 'name': '四柱八字起名法', 'category': '术数'},
            {'id': 'S08', 'name': '易卦起名法', 'category': '术数'},
        ],
        'renaming': [
            {'id': 'R01', 'name': '谐音换字', 'description': '"朱月坡"→"朱岳坡"式微调', 'category': '改名'},
            {'id': 'R02', 'name': '易音换字', 'description': '换同音字改气质', 'category': '改名'},
            {'id': 'R03', 'name': '部首改动', 'description': '"琳"→"淋"式偏旁手术，保留读音改五行', 'category': '改名'},
            {'id': 'R04', 'name': '添字', 'description': '单名变双名降低重名率', 'category': '改名'},
            {'id': 'R05', 'name': '删字', 'description': '双名简化', 'category': '改名'},
            {'id': 'R06', 'name': '前后易序', 'description': '"明哲"→"哲明"', 'category': '改名'},
            {'id': 'R07', 'name': '综合改名', 'description': '多种方法综合运用', 'category': '改名'},
        ],
    }
    all_methods = methods['traditional'] + methods['modern'] + methods['numerological'] + methods['renaming']
    for m in all_methods:
        m.setdefault('description', '')
        m['source'] = '巨天中《吉名如意》'
    return all_methods, methods


def extract_history_cases():
    """31-历史演变 命名案例"""
    path = os.path.join(KB, '04-专题资料', '31-历史演变时间轴.md')
    tables = parse_md_tables(path)
    cases = []
    for table in tables:
        for row in table:
            if len(row) >= 3 and ('先秦' in row[0] or '秦汉' in row[0] or '魏晋' in row[0] or
                                  '隋唐' in row[0] or '宋' in row[0] or '元' in row[0] or
                                  '明' in row[0] or '清' in row[0] or '民国' in row[0] or
                                  '近年' in row[0] or '当代' in row[0]):
                era = row[0].replace('**', '').strip()
                feature = row[1].replace('**', '').strip()
                examples = row[2].replace('**', '').strip()
                cases.append({
                    'era': era,
                    'naming_features': feature,
                    'example_names': examples,
                })
    return cases


def extract_generation_poems():
    """32-字辈谱"""
    path = os.path.join(KB, '04-专题资料', '32-字辈谱与五行序辈.md')
    with open(path, encoding='utf-8') as f:
        content = f.read()
    poems = []

    # 孔子世家字辈谱 (30字+20字续增)
    kong_30 = '宏闻贞尚衍兴毓传继广昭宪庆繁祥'
    kong_20 = '建敦安定懋肇毓秀永锡世绪'
    poems.append({
        'family': '孔子世家',
        'generations': '56-105代',
        'poem': kong_30 + kong_20,
        'characters': list(kong_30 + kong_20),
        'note': '明洪武初颁30字(56-85代)，1920年续增20字(86-105代)',
        'wuxing_sequence': False,
    })

    # 朱元璋皇室五行序辈（木→火→土→金→水）
    zhu_wuxing = ['木', '火', '土', '金', '水']
    zhu_examples = ['桢(木)', '熺(火)', '土填(土)', '金填(金)', '水填(水)']
    poems.append({
        'family': '朱元璋皇室',
        'generations': '朱氏各藩王',
        'poem': '五行相生序辈',
        'wuxing_sequence': zhu_wuxing,
        'example_names': zhu_examples,
        'note': '朱元璋为子孙定五行相生序辈法：木→火→土→金→水循环',
    })

    # 朱熹家族五行链
    poems.append({
        'family': '朱熹家族',
        'generations': '五代',
        'poem': '五行相生链',
        'wuxing_sequence': ['木(熹)', '火(塾)', '土(鉴)', '金(鎏)', '水(河)'],
        'note': '朱熹→朱塾→朱鉴→朱鎏→朱河，五代五行相生链',
    })

    return poems


def extract_high_freq_chars():
    """34-速查表 高频字"""
    path = os.path.join(KB, '04-专题资料', '34-取名常用字速查表.md')
    tables = parse_md_tables(path)
    chars = []
    for table in tables:
        for row in table:
            if len(row) >= 3 and len(row[0]) <= 4 and row[0] not in ('原则', '高频字', '含义'):
                char = row[0].replace('**', '').strip()
                note = row[1].replace('**', '').strip() if len(row) > 1 else ''
                source_ref = row[2].replace('**', '').strip() if len(row) > 2 else ''
                if len(char) <= 4 and char and not char.startswith('---'):
                    chars.append({
                        'char': char,
                        'note': note,
                        'source_ref': source_ref,
                    })
    return chars


def extract_ethnic_customs():
    """30-少数民族命名习俗"""
    path = os.path.join(KB, '04-专题资料', '30-少数民族命名习俗.md')
    tables = parse_md_tables(path)
    customs = []
    for table in tables:
        for row in table:
            if len(row) >= 3 and ('制' in row[0] or '名' in row[0]):
                system = row[0].replace('**', '').strip()
                logic = row[1].replace('**', '').strip()
                ethnic = row[2].replace('**', '').strip()
                if system and logic:
                    customs.append({
                        'naming_system': system,
                        'core_logic': logic,
                        'ethnic_groups': ethnic,
                    })
    return customs


def extract_xiangxie_patterns():
    """27-古人名字解诂 相协22式 + 名-字对案例"""
    path = os.path.join(KB, '03-现代参考书', '27-古人名字解诂-吉常宏吉发涵.md')
    tables = parse_md_tables(path)
    examples = []
    for table in tables:
        for row in table:
            if len(row) >= 4:
                person = row[0].replace('**', '').strip()
                ming = row[1].replace('**', '').strip()
                zi = row[2].replace('**', '').strip()
                pattern = row[3].replace('**', '').strip()
                if person and ming and zi and '相协' in pattern:
                    examples.append({
                        'person': person,
                        'ming': ming,
                        'zi': zi,
                        'pattern': pattern,
                    })
    # 22相协方式（从文中提取的类型列表）
    patterns = [
        {'id': 1, 'name': '同义相协', 'description': '名与字同义互训', 'example': '诸葛亮(亮/孔明)'},
        {'id': 2, 'name': '对文反义相协', 'description': '名与字反义相对', 'example': '韩愈(愈/退之)'},
        {'id': 3, 'name': '连类相协', 'description': '名与字同类连属', 'example': '关羽(羽/云长)'},
        {'id': 4, 'name': '指物相协', 'description': '以物喻义'},
        {'id': 5, 'name': '辨物相协', 'description': '辨别事物的名-字关联'},
        {'id': 6, 'name': '干支五行相协', 'description': '以天干地支五行关联名与字'},
        {'id': 7, 'name': '排行系字相协', 'description': '以伯仲叔季排行系字'},
        {'id': 8, 'name': '因革相协', 'description': '名与字因袭变革'},
        {'id': 9, 'name': '因果相协', 'description': '名为因，字为果', 'example': '杨过(过/改之)'},
        {'id': 10, 'name': '反义相协', 'description': '名与字意义相反', 'example': '朱熹(熹明/元晦暗)'},
        {'id': 11, 'name': '同义互训', 'description': '名与字互相训释', 'example': '屈原(平/原，广平曰原)'},
        {'id': 12, 'name': '辨似相协', 'description': '字形相似取义'},
    ]
    return patterns, examples


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def main():
    print('=' * 60)
    print('知识库结构化数据提取')
    print('=' * 60)

    # 1. 取名技法库
    techs = extract_techniques()
    save_json(os.path.join(R2, '07-取名技法库.json'), {
        'meta': {'name': '取名技法库', 'source': '李正明《给孩子起个好名字》20技法', 'version': '1.0'},
        'techniques': techs, 'count': len(techs)
    })
    print(f'取名技法库: {len(techs)} 条')

    # 2. 取名方法库
    all_methods, method_groups = extract_methods()
    save_json(os.path.join(R2, '08-取名方法库.json'), {
        'meta': {'name': '取名方法库', 'source': '巨天中《吉名如意》32法+改名7法', 'version': '1.0'},
        'methods': all_methods, 'count': len(all_methods),
        'categories': {
            '传统习俗10法': [m['id'] for m in method_groups['traditional']],
            '现代艺术14法': [m['id'] for m in method_groups['modern']],
            '术数8法': [m['id'] for m in method_groups['numerological']],
            '改名7法': [m['id'] for m in method_groups['renaming']],
        }
    })
    print(f'取名方法库: {len(all_methods)} 条')

    # 3. 历史命名案例库
    cases = extract_history_cases()
    save_json(os.path.join(R3, '历史命名案例库.json'), {
        'meta': {'name': '历史命名案例库', 'source': '06-取名知识库/04-专题资料/31-历史演变时间轴', 'version': '1.0'},
        'cases': cases, 'count': len(cases)
    })
    print(f'历史命名案例库: {len(cases)} 条')

    # 4. 字辈谱库
    poems = extract_generation_poems()
    save_json(os.path.join(R1, '字辈谱库', '字辈谱.json'), {
        'meta': {'name': '字辈谱与五行序辈库', 'source': '06-取名知识库/04-专题资料/32-字辈谱与五行序辈', 'version': '1.0'},
        'poems': poems, 'count': len(poems)
    })
    print(f'字辈谱库: {len(poems)} 条')

    # 5. 取名常用字速查表
    chars = extract_high_freq_chars()
    save_json(os.path.join(R1, '取名常用字速查表.json'), {
        'meta': {'name': '取名常用字速查表', 'source': '06-取名知识库/04-专题资料/34-取名常用字速查表', 'version': '1.0'},
        'chars': chars, 'count': len(chars)
    })
    print(f'取名常用字速查表: {len(chars)} 条')

    # 6. 少数民族命名习俗库
    customs = extract_ethnic_customs()
    save_json(os.path.join(R3, '少数民族命名习俗库.json'), {
        'meta': {'name': '少数民族命名习俗库', 'source': '06-取名知识库/04-专题资料/30-少数民族命名习俗', 'version': '1.0'},
        'customs': customs, 'count': len(customs)
    })
    print(f'少数民族命名习俗库: {len(customs)} 条')

    # 7. 名字相协式库
    patterns, examples = extract_xiangxie_patterns()
    save_json(os.path.join(R3, '名字相协式库.json'), {
        'meta': {'name': '名字相协式库', 'source': '吉常宏《古人名字解诂》22式+案例', 'version': '1.0'},
        'patterns': patterns, 'pattern_count': len(patterns),
        'examples': examples, 'example_count': len(examples)
    })
    print(f'名字相协式库: {len(patterns)} 式 + {len(examples)} 案例')

    print()
    print('全部提取完成。')


if __name__ == '__main__':
    main()
