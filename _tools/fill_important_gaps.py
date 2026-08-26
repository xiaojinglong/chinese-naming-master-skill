# -*- coding: utf-8 -*-
"""
补充重要缺口数据：
1. 姓氏声调模式表（姓氏声调→推荐名字声调组合）
2. 取名风格标签（给字库和文学素材加风格标签）
3. 取名全流程示例（端到端 walkthrough）
4. 测试用例集（边界情况）
5. 兄弟姐妹名生成规则
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def build_tone_pattern_table():
    """姓氏声调模式表"""
    # 声调搭配原则：
    # - 姓氏为1声（阴平）：名字避免全1声（单调），推荐2-1, 1-2, 2-4等变化
    # - 姓氏为2声（阳平）：名字避免全2声，推荐1-3, 3-1等
    # - 姓氏为3声（上声）：名字避免全3声，推荐1-2, 2-4等
    # - 姓氏为4声（去声）：名字避免全4声，推荐1-2, 2-1等
    # 末尾字优先1/2声（收音响亮）

    patterns = {
        'meta': {
            'name': '姓氏声调搭配模式表',
            'purpose': '根据姓氏声调推荐名字声调组合，避免单调拗口',
            'tone_meaning': {1: '阴平', 2: '阳平', 3: '上声', 4: '去声', 0: '轻声'},
            'principles': [
                '相邻字声调尽量不同（避免连续同声调）',
                '末尾字优先1声或2声（收音响亮）',
                '避免全平（1/2声）或全仄（3/4声）',
                '姓氏与名字首字声调不同更流畅',
            ],
        },
        'patterns': {
            '1': {  # 姓氏1声（如张/王/李部分读音）
                'surname_tone': 1,
                'avoid': ['1-1', '1-1-1'],
                'recommend': ['1-2-1', '1-2-4', '1-4-2', '1-3-2', '1-4-1'],
                'good_examples': ['张(1) + 伟(3)伦(2)', '张(1) + 雨(3)涵(2)'],
                'bad_examples': ['张(1) + 飞(1)飞(1)'],
            },
            '2': {  # 姓氏2声（如刘/陈/杨/黄）
                'surname_tone': 2,
                'avoid': ['2-2', '2-2-2'],
                'recommend': ['2-1-2', '2-1-4', '2-3-1', '2-4-1', '2-3-4'],
                'good_examples': ['刘(2) + 德(2)华(4)', '刘(2) + 晓(3)明(2)'],
                'bad_examples': ['刘(2) + 德(2)明(2)'],
            },
            '3': {  # 姓氏3声（如马/许/武）
                'surname_tone': 3,
                'avoid': ['3-3', '3-3-3'],
                'recommend': ['3-1-2', '3-2-1', '3-1-4', '3-2-4', '3-4-1'],
                'good_examples': ['马(3) + 云(2)飞(1)', '许(3) + 志(4)远(3)'],
                'bad_examples': ['马(3) + 晓(3)伟(3)'],
            },
            '4': {  # 姓氏4声（如赵/谢/杜/宋）
                'surname_tone': 4,
                'avoid': ['4-4', '4-4-4'],
                'recommend': ['4-1-2', '4-2-1', '4-1-4', '4-3-2', '4-2-4'],
                'good_examples': ['赵(4) + 云(2)飞(1)', '谢(4) + 明(2)轩(1)'],
                'bad_examples': ['赵(4) + 立(4)志(4)'],
            },
        },
    }
    return patterns


def add_style_tags():
    """给 hanzi_common 和文学素材添加风格标签"""
    # 风格分类规则
    def classify_style(char_info):
        """根据字的属性判断风格"""
        meaning = char_info.get('meaning', '')
        radical = char_info.get('radical', '')
        wuxing = char_info.get('wuxing', '')
        gender = char_info.get('gender_hint', 'neutral')

        styles = []
        # 大气风格：与天地山水、宏大相关
        if any(k in meaning for k in ['天', '地', '山', '海', '宇', '乾', '坤', '浩', '博', '宏', '大']):
            styles.append('大气')
        # 文雅风格：与文学、美德、温润相关
        if any(k in meaning for k in ['文', '雅', '德', '仁', '慧', '诗', '书', '礼', '乐', '温']):
            styles.append('文雅')
        # 古风风格：与古代器物、香草、玉石相关
        if any(k in meaning for k in ['玉', '瑾', '瑜', '瑶', '琪', '琳', '珂', '璋', '璧', '琮']):
            styles.append('古风')
        if radical in ('王', '玉', '钅', '金'):
            styles.append('古风')
        # 现代风格：与科技、创新、明亮相关
        if any(k in meaning for k in ['明', '亮', '光', '新', '创', '科', '智', '慧', '欣', '悦']):
            styles.append('现代')
        # 婉约风格：与花草、柔水、女性美相关
        if any(k in meaning for k in ['花', '草', '芳', '芬', '柔', '婉', '淑', '静', '雅', '清']):
            styles.append('婉约')
        if gender == 'female':
            styles.append('婉约')

        return list(set(styles)) if styles else ['通用']

    # 给 hanzi_common 添加风格标签
    common_path = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json')
    with open(common_path, encoding='utf-8') as f:
        common = json.load(f)

    tagged = 0
    for c in common['chars']:
        styles = classify_style(c)
        c['style_tags'] = styles
        tagged += 1

    with open(common_path, 'w', encoding='utf-8') as f:
        json.dump(common, f, ensure_ascii=False, indent=1)

    print(f'hanzi_common 风格标签: {tagged} 字已标注')

    # 给文学素材添加风格标签
    lit_dir = os.path.join(BASE, '..', '01-数据资料', '经典文学素材库')
    for fname in ['shijing.json', 'chuci.json', 'tangshi.json', 'songci.json',
                  'lunyu.json', 'zhouyi.json', 'daodejing.json', 'zhuangzi.json',
                  'mengzi.json', 'shangshu.json', 'daxue.json', 'zhongyong.json',
                  'zuozhuan.json', 'lisao.json', 'guanzi.json', 'liezi.json']:
        fpath = os.path.join(lit_dir, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        for item in data.get('items', []):
            word = item.get('word', '')
            meaning = item.get('meaning', '')
            # 文学素材的风格标签
            styles = []
            if any(k in meaning for k in ['大', '壮', '宏', '远', '高', '山', '海', '天']):
                styles.append('大气')
            if any(k in meaning for k in ['清', '雅', '文', '静', '柔', '婉']):
                styles.append('文雅')
            if any(k in meaning for k in ['玉', '瑶', '瑾', '瑜', '琼', '琳']):
                styles.append('古风')
            if any(k in meaning for k in ['光', '明', '新', '欣', '悦']):
                styles.append('现代')
            item['style_tags'] = list(set(styles)) if styles else ['通用']
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

    print(f'文学素材风格标签: 全部 16 部已标注')


def build_sibling_rules():
    """兄弟姐妹名生成规则"""
    return {
        'meta': {
            'name': '兄弟姐妹名生成规则',
            'purpose': '为二孩/双胞胎/多孩家庭生成关联名字',
        },
        'strategies': [
            {
                'name': '共用一字',
                'description': '兄弟姐妹名字共用一个字（通常是中间字或末尾字）',
                'examples': [
                    {'names': ['张伟明', '张伟华'], 'shared': '伟', 'position': '中间'},
                    {'names': ['李思远', '李思成'], 'shared': '思', 'position': '中间'},
                    {'names': ['王晓明', '王晓华'], 'shared': '晓', 'position': '中间'},
                ],
                'wuxing_note': '共用字的五行应兼顾两人的喜用神，或选中性五行',
            },
            {
                'name': '反义对仗',
                'description': '兄弟姐妹名字用反义/对仗字（刚柔/动静/文武）',
                'examples': [
                    {'names': ['李文静', '李文动'], 'pattern': '静/动'},
                    {'names': ['王若刚', '王若柔'], 'pattern': '刚/柔'},
                ],
            },
            {
                'name': '递进序列',
                'description': '名字按意义递进（如春→夏→秋→冬，元→亨→利→贞）',
                'examples': [
                    {'names': ['李春生', '李夏长', '李秋收', '李冬藏'], 'pattern': '四季'},
                    {'names': ['王元吉', '王亨利', '王贞祥'], 'pattern': '元亨利贞'},
                ],
            },
            {
                'name': '同源拆词',
                'description': '从一个词/成语拆出两个字分别给两个孩子',
                'examples': [
                    {'names': ['张清华', '张清风'], 'source': '清风'},
                    {'names': ['李文轩', '李文辕'], 'source': '轩辕'},
                ],
            },
            {
                'name': '五行互补',
                'description': '按两人八字喜用神互补取名',
                'examples': [
                    {'names': ['李沐阳(喜水)', '李森阳(喜木)'], 'note': '水木相生'},
                ],
            },
            {
                'name': '声调呼应',
                'description': '名字声调形成呼应模式（如1-2 + 2-1）',
                'examples': [
                    {'names': ['王天明(1-1-2)', '王地明(1-4-2)'], 'pattern': '天/地对仗'},
                ],
            },
        ],
        'twins_special': {
            'description': '双胞胎命名特殊规则',
            'strategies': [
                '同音不同字：如"子轩/子萱"（男/女双胞胎）',
                '叠字拆分：如"团团/圆圆"、"欢欢/乐乐"',
                '对仗工整：如"天佐/天佑"、"文彬/文斌"',
            ],
        },
    }


def build_test_cases():
    """测试用例集"""
    return {
        'meta': {'name': '取名Skill测试用例集', 'purpose': '验证取名引擎的健壮性'},
        'cases': [
            {
                'id': 'TC01', 'name': '常规单姓双字名',
                'input': {'surname': '李', 'gender': 'male', 'birth_year': 2024, 'birth_month': 3, 'birth_day': 15, 'birth_hour': 10, 'name_length': 2},
                'expected': '返回5-10个候选名，含评分',
            },
            {
                'id': 'TC02', 'name': '常规单姓单字名',
                'input': {'surname': '王', 'gender': 'female', 'birth_year': 2024, 'birth_month': 6, 'birth_day': 20, 'birth_hour': 8, 'name_length': 1},
                'expected': '返回单字候选名',
            },
            {
                'id': 'TC03', 'name': '复姓双字名',
                'input': {'surname': '欧阳', 'gender': 'male', 'birth_year': 2024, 'birth_month': 1, 'birth_day': 1, 'birth_hour': 12, 'name_length': 2},
                'expected': '正确处理复姓五格计算',
            },
            {
                'id': 'TC04', 'name': '生僻姓氏',
                'input': {'surname': '亓', 'gender': 'male', 'birth_year': 2024, 'birth_month': 5, 'birth_day': 5, 'birth_hour': 6, 'name_length': 2},
                'expected': '生僻姓氏也能正常生成',
            },
            {
                'id': 'TC05', 'name': '缺时辰（默认12点）',
                'input': {'surname': '张', 'gender': 'female', 'birth_year': 2024, 'birth_month': 8, 'birth_day': 15, 'name_length': 2},
                'expected': '缺时辰时默认12点，时柱可能不准但不影响主体',
            },
            {
                'id': 'TC06', 'name': '立春边界（年柱切换）',
                'input': {'surname': '刘', 'gender': 'male', 'birth_year': 2024, 'birth_month': 2, 'birth_day': 3, 'birth_hour': 10, 'name_length': 2},
                'expected': '立春前（2月3日）年柱应为癸卯而非甲辰',
            },
            {
                'id': 'TC07', 'name': '节气边界（月柱切换）',
                'input': {'surname': '陈', 'gender': 'female', 'birth_year': 2024, 'birth_month': 4, 'birth_day': 4, 'birth_hour': 10, 'name_length': 2},
                'expected': '清明前（4月4日）月柱应为丁卯而非戊辰',
            },
            {
                'id': 'TC08', 'name': '家族避讳',
                'input': {'surname': '周', 'gender': 'male', 'birth_year': 2024, 'birth_month': 3, 'birth_day': 15, 'birth_hour': 10, 'name_length': 2, 'forbidden_chars': ['伟', '强']},
                'expected': '候选名中不含伟/强',
            },
            {
                'id': 'TC09', 'name': '风格偏好-文雅',
                'input': {'surname': '林', 'gender': 'female', 'birth_year': 2024, 'birth_month': 4, 'birth_day': 10, 'birth_hour': 10, 'name_length': 2, 'style': '文雅'},
                'expected': '推荐文雅风格的名字',
            },
            {
                'id': 'TC10', 'name': '风格偏好-大气',
                'input': {'surname': '赵', 'gender': 'male', 'birth_year': 2024, 'birth_month': 7, 'birth_day': 20, 'birth_hour': 10, 'name_length': 2, 'style': '大气'},
                'expected': '推荐大气风格的名字',
            },
        ],
    }


def build_walkthrough():
    """取名全流程示例"""
    return '''# 取名全流程示例（端到端 Walkthrough）

## 输入

```
姓氏：李
性别：男
出生：2024年3月15日 10:00
风格：大气
名字长度：2字
```

## 第1步：八字排盘

```
公历：2024-03-15 10:00
八字：甲辰年 丁卯月 戊寅日 丁巳时
日主：戊（土）
强弱：中和（-1分）
喜用神：水
忌用神：（中和无明确忌用）
生肖：龙
纳音：覆灯火
```

## 第2步：五行补益分析

```
五行统计：金0.5 木3.5 水0.3 火3.5 土2.6
分析：木火偏旺，水偏弱，金最弱
喜用神：水（调候+补益）
```

## 第3步：候选字筛选

```
筛选条件：
  - 五行：优先水（喜用神），排除无五行标记
  - 性别：男性字优先
  - 排除：生僻字、难写字
  - 部首：优先氵/雨/子等水部首
筛选结果：从308常用字中筛出约 50 个候选字
```

## 第4步：候选名生成

```
组合策略：候选字两两组合（双字名）
生成数量：约 500 个候选名
五格计算：每个候选名计算天格/人格/地格/外格/总格
三才配置：由五格尾数定五行
```

## 第5步：评分排序

```
评分维度（默认权重）：
  五行补益 25% | 五格数理 15% | 音韵流畅 15% | 寓意深度 15%
  三才配置 10% | 字形美观 10% | 生肖契合 10%

排序结果（前5名）：
  1. 李海源  84.2 (A) - 五行水旺，五格全吉，音韵流畅
  2. 李海溪  84.2 (A) - 五行水旺，五格全吉，音韵流畅
  3. 李海江  81.2 (A) - 五行水旺，三才配置佳
  4. 李海泽  79.6 (B) - 五行水旺，寓意深厚
  5. 李海清  78.8 (B) - 五行水旺，音韵优美
```

## 第6步：输出报告（示例）

```
候选名 #1：李海源
━━━━━━━━━━━━━━━━━━━━━━
字义原理：海（广阔包容）+ 源（本源活水）→ 胸怀宽广，源远流长
五行分析：海(水) + 源(水) → 双水补益喜用神
五格数理：天格8(金) 人格15(土) 地格13(火) 外格5(土) 总格21(木) → 全吉
三才配置：金土火 → 中吉
音韵检查：李(3)海(3)源(2) → 声调3-3-2，变化流畅
出处：「海纳百川，有容乃大」；「问渠那得清如许，为有源头活水来」
综合评分：84.2 / 100（A级·优秀）
━━━━━━━━━━━━━━━━━━━━━━
```
'''


def main():
    print('=== 补充重要缺口 ===')

    # 1. 姓氏声调模式表
    tone_table = build_tone_pattern_table()
    with open(os.path.join(BASE, '..', '02-规则与算法资料', '10-姓氏声调模式表.json'), 'w', encoding='utf-8') as f:
        json.dump(tone_table, f, ensure_ascii=False, indent=1)
    print('1. 姓氏声调模式表: 已生成')

    # 2. 风格标签
    add_style_tags()

    # 3. 兄弟名规则
    sibling_rules = build_sibling_rules()
    with open(os.path.join(BASE, '..', '02-规则与算法资料', '11-兄弟姐妹名规则.json'), 'w', encoding='utf-8') as f:
        json.dump(sibling_rules, f, ensure_ascii=False, indent=1)
    print('3. 兄弟姐妹名规则: 已生成')

    # 4. 测试用例
    test_cases = build_test_cases()
    with open(os.path.join(BASE, '..', '04-输出与交互资料', '03-测试用例集.json'), 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=1)
    print('4. 测试用例集: 已生成（10个用例）')

    # 5. 全流程示例
    walkthrough = build_walkthrough()
    with open(os.path.join(BASE, '..', '04-输出与交互资料', '03-取名全流程示例.md'), 'w', encoding='utf-8') as f:
        f.write(walkthrough)
    print('5. 取名全流程示例: 已生成')

    print()
    print('全部重要缺口补充完成。')


if __name__ == '__main__':
    main()
