# -*- coding: utf-8 -*-
"""生成天干地支与八字数据: tiangan.json / dizhi.json / shengxiao.json / nayin.json"""
import json, os

def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01-数据资料", "天干地支与八字"))

    # ---- 十天干 ----
    tiangan = {
        "meta": {"name": "十天干", "version": "1.0", "note": "用于年/月/日/时柱天干；天干五行是八字五行统计的一部分"},
        "tiangan": [
            {"gan": "甲", "pinyin": "jiǎ", "wuxing": "木", "yin_yang": "阳", "direction": "东方", "zodiac_part": "头", "notes": "栋梁之木"},
            {"gan": "乙", "pinyin": "yǐ", "wuxing": "木", "yin_yang": "阴", "direction": "东方", "zodiac_part": "颈", "notes": "花草之木"},
            {"gan": "丙", "pinyin": "bǐng", "wuxing": "火", "yin_yang": "阳", "direction": "南方", "zodiac_part": "肩", "notes": "太阳之火"},
            {"gan": "丁", "pinyin": "dīng", "wuxing": "火", "yin_yang": "阴", "direction": "南方", "zodiac_part": "胸", "notes": "灯烛之火"},
            {"gan": "戊", "pinyin": "wù", "wuxing": "土", "yin_yang": "阳", "direction": "中央", "zodiac_part": "胁", "notes": "城墙之土"},
            {"gan": "己", "pinyin": "jǐ", "wuxing": "土", "yin_yang": "阴", "direction": "中央", "zodiac_part": "腹", "notes": "田园之土"},
            {"gan": "庚", "pinyin": "gēng", "wuxing": "金", "yin_yang": "阳", "direction": "西方", "zodiac_part": "脐", "notes": "刀剑之金"},
            {"gan": "辛", "pinyin": "xīn", "wuxing": "金", "yin_yang": "阴", "direction": "西方", "zodiac_part": "股", "notes": "首饰之金"},
            {"gan": "壬", "pinyin": "rén", "wuxing": "水", "yin_yang": "阳", "direction": "北方", "zodiac_part": "胫", "notes": "江河之水"},
            {"gan": "癸", "pinyin": "guǐ", "wuxing": "水", "yin_yang": "阴", "direction": "北方", "zodiac_part": "足", "notes": "雨露之水"},
        ],
    }
    with open(os.path.join(base, "tiangan.json"), "w", encoding="utf-8") as f:
        json.dump(tiangan, f, ensure_ascii=False, indent=2)

    # ---- 十二地支 ----
    dizhi = {
        "meta": {"name": "十二地支", "version": "1.0", "note": "地支藏干用于八字五行统计（'含藏'的干按比例计入五行）；月令用于月柱划分"},
        "dizhi": [
            {"zhi": "子", "pinyin": "zǐ", "wuxing": "水", "yin_yang": "阳", "canggan": ["癸"], "zodiac": "鼠", "month": "十一月", "hour": "23:00-01:00", "direction": "正北"},
            {"zhi": "丑", "pinyin": "chǒu", "wuxing": "土", "yin_yang": "阴", "canggan": ["己", "癸", "辛"], "zodiac": "牛", "month": "十二月", "hour": "01:00-03:00", "direction": "东北"},
            {"zhi": "寅", "pinyin": "yín", "wuxing": "木", "yin_yang": "阳", "canggan": ["甲", "丙", "戊"], "zodiac": "虎", "month": "正月", "hour": "03:00-05:00", "direction": "东北"},
            {"zhi": "卯", "pinyin": "mǎo", "wuxing": "木", "yin_yang": "阴", "canggan": ["乙"], "zodiac": "兔", "month": "二月", "hour": "05:00-07:00", "direction": "正东"},
            {"zhi": "辰", "pinyin": "chén", "wuxing": "土", "yin_yang": "阳", "canggan": ["戊", "乙", "癸"], "zodiac": "龙", "month": "三月", "hour": "07:00-09:00", "direction": "东南"},
            {"zhi": "巳", "pinyin": "sì", "wuxing": "火", "yin_yang": "阴", "canggan": ["丙", "庚", "戊"], "zodiac": "蛇", "month": "四月", "hour": "09:00-11:00", "direction": "东南"},
            {"zhi": "午", "pinyin": "wǔ", "wuxing": "火", "yin_yang": "阳", "canggan": ["丁", "己"], "zodiac": "马", "month": "五月", "hour": "11:00-13:00", "direction": "正南"},
            {"zhi": "未", "pinyin": "wèi", "wuxing": "土", "yin_yang": "阴", "canggan": ["己", "丁", "乙"], "zodiac": "羊", "month": "六月", "hour": "13:00-15:00", "direction": "西南"},
            {"zhi": "申", "pinyin": "shēn", "wuxing": "金", "yin_yang": "阳", "canggan": ["庚", "壬", "戊"], "zodiac": "猴", "month": "七月", "hour": "15:00-17:00", "direction": "西南"},
            {"zhi": "酉", "pinyin": "yǒu", "wuxing": "金", "yin_yang": "阴", "canggan": ["辛"], "zodiac": "鸡", "month": "八月", "hour": "17:00-19:00", "direction": "正西"},
            {"zhi": "戌", "pinyin": "xū", "wuxing": "土", "yin_yang": "阳", "canggan": ["戊", "辛", "丁"], "zodiac": "狗", "month": "九月", "hour": "19:00-21:00", "direction": "西北"},
            {"zhi": "亥", "pinyin": "hài", "wuxing": "水", "yin_yang": "阴", "canggan": ["壬", "甲"], "zodiac": "猪", "month": "十月", "hour": "21:00-23:00", "direction": "西北"},
        ],
    }
    with open(os.path.join(base, "dizhi.json"), "w", encoding="utf-8") as f:
        json.dump(dizhi, f, ensure_ascii=False, indent=2)

    # ---- 生肖 ----
    shengxiao = {
        "meta": {"name": "生肖地支对应", "version": "1.0", "note": "生肖用于生肖喜忌筛选；地支五行用于八字；详细喜忌偏旁见 02-规则与算法资料/03-生肖喜忌偏旁表.json"},
        "shengxiao": [
            {"zodiac": "鼠", "zhi": "子", "wuxing": "水", "hour": "23:00-01:00", "month": "十一月", "direction": "正北"},
            {"zodiac": "牛", "zhi": "丑", "wuxing": "土", "hour": "01:00-03:00", "month": "十二月", "direction": "东北"},
            {"zodiac": "虎", "zhi": "寅", "wuxing": "木", "hour": "03:00-05:00", "month": "正月", "direction": "东北"},
            {"zodiac": "兔", "zhi": "卯", "wuxing": "木", "hour": "05:00-07:00", "month": "二月", "direction": "正东"},
            {"zodiac": "龙", "zhi": "辰", "wuxing": "土", "hour": "07:00-09:00", "month": "三月", "direction": "东南"},
            {"zodiac": "蛇", "zhi": "巳", "wuxing": "火", "hour": "09:00-11:00", "month": "四月", "direction": "东南"},
            {"zodiac": "马", "zhi": "午", "wuxing": "火", "hour": "11:00-13:00", "month": "五月", "direction": "正南"},
            {"zodiac": "羊", "zhi": "未", "wuxing": "土", "hour": "13:00-15:00", "month": "六月", "direction": "西南"},
            {"zodiac": "猴", "zhi": "申", "wuxing": "金", "hour": "15:00-17:00", "month": "七月", "direction": "西南"},
            {"zodiac": "鸡", "zhi": "酉", "wuxing": "金", "hour": "17:00-19:00", "month": "八月", "direction": "正西"},
            {"zodiac": "狗", "zhi": "戌", "wuxing": "土", "hour": "19:00-21:00", "month": "九月", "direction": "西北"},
            {"zodiac": "猪", "zhi": "亥", "wuxing": "水", "hour": "21:00-23:00", "month": "十月", "direction": "西北"},
        ],
    }
    with open(os.path.join(base, "shengxiao.json"), "w", encoding="utf-8") as f:
        json.dump(shengxiao, f, ensure_ascii=False, indent=2)

    # ---- 六十甲子纳音 ----
    # (干支, 纳音)
    NAYIN = [
        ("甲子","海中金"),("乙丑","海中金"),("丙寅","炉中火"),("丁卯","炉中火"),("戊辰","大林木"),("己巳","大林木"),
        ("庚午","路旁土"),("辛未","路旁土"),("壬申","剑锋金"),("癸酉","剑锋金"),("甲戌","山头火"),("乙亥","山头火"),
        ("丙子","涧下水"),("丁丑","涧下水"),("戊寅","城头土"),("己卯","城头土"),("庚辰","白蜡金"),("辛巳","白蜡金"),
        ("壬午","杨柳木"),("癸未","杨柳木"),("甲申","泉中水"),("乙酉","泉中水"),("丙戌","屋上土"),("丁亥","屋上土"),
        ("戊子","霹雳火"),("己丑","霹雳火"),("庚寅","松柏木"),("辛卯","松柏木"),("壬辰","长流水"),("癸巳","长流水"),
        ("甲午","沙中金"),("乙未","沙中金"),("丙申","山下火"),("丁酉","山下火"),("戊戌","平地木"),("己亥","平地木"),
        ("庚子","壁上土"),("辛丑","壁上土"),("壬寅","金箔金"),("癸卯","金箔金"),("甲辰","覆灯火"),("乙巳","覆灯火"),
        ("丙午","天河水"),("丁未","天河水"),("戊申","大驿土"),("己酉","大驿土"),("庚戌","钗钏金"),("辛亥","钗钏金"),
        ("壬子","桑柘木"),("癸丑","桑柘木"),("甲寅","大溪水"),("乙卯","大溪水"),("丙辰","沙中土"),("丁巳","沙中土"),
        ("戊午","天上火"),("己未","天上火"),("庚申","石榴木"),("辛酉","石榴木"),("壬戌","大海水"),("癸亥","大海水"),
    ]
    nayin = {
        "meta": {"name": "六十甲子纳音表", "version": "1.0", "usage": "年柱纳音用于'纳音五行'参考（取名时一般仅作辅助信息）"},
        "count": len(NAYIN),
        "nayin": [{"ganzhi": g, "nayin": n} for g, n in NAYIN],
    }
    with open(os.path.join(base, "nayin.json"), "w", encoding="utf-8") as f:
        json.dump(nayin, f, ensure_ascii=False, indent=2)

    print("tiangan/dizhi/shengxiao/nayin 生成完毕")

if __name__ == "__main__":
    main()
