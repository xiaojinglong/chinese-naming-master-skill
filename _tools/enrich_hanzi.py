# -*- coding: utf-8 -*-
"""为 hanzi_common.json 补充扩展字段：rare_flag / difficult_flag / homophone_risk / gender_hint"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(BASE, "01-数据资料", "汉字字库", "hanzi_common.json")

# 明显男性倾向用字
MALE = set("铭锋锐钦钰铠鑫钟钊钧铮镜锡琛璞珩刚超靖捷森林松柏枫楠梓桐栋梁楷檀栩桢榕荣茂彬彦彪嘉凯赫毅健康勇强海江河泽润源浩瀚波涛洋泓浚澜洲津湘淳滨沧渊泱武博弘宏飞鹏鹤鸿卿昊曦曜晖旭昕晟烨煜炜炫灿焕炎智哲志德彤昱炅烈煌煊晞晏昭熙灼炽龙麟耀泰通畅坤均培基坚城堂岳峰峻崇嵩山岩磊宇佑伟硕屹峥嵘懿维勋翔轩宸航")
# 明显女性倾向用字
FEMALE = set("婷婉娴嫣芳茗茉莉荷莲蕊萱芷蕙薇蕾芊茜菁菲蓝若菊朵柔淑洁雯露霜霏霓湉汐妍妙鸾燕韵怡晗晴梦璇瑶璐琳琪琼莹珺璧玟樱槿艺秀惠慧美祯")

# 谐音风险组合中的名用字（单字本身无害，但组合需排查）
HOMOPHONE = {
    "伟": "杨伟→阳痿",
    "德": "吴德→无德",
    "珍": "史珍香→屎真香",
    "香": "史珍香→屎真香",
    "泉": "黄泉不吉",
    "金": "潘金莲/金莲",
    "莲": "潘金莲/李莲英",
    "高": "赵高/高潮",
    "英": "李莲英（组合慎用）",
    "寿": "秦寿→禽兽",
}

d = json.load(open(FP, encoding="utf-8"))
updated = 0
for c in d["chars"]:
    s_simp = c["strokes_simplified"]
    s_kan = c["strokes_kangxi"]
    c["rare_flag"] = False                      # 本库全为常用字（一级字表内）
    c["difficult_flag"] = s_simp > 20           # 以简体书写难度判定（繁体高但简体低的字不标）
    c["homophone_risk"] = HOMOPHONE.get(c["char"], "")  # 空串=无已知风险
    if c["char"] in MALE:
        c["gender_hint"] = "male"
    elif c["char"] in FEMALE:
        c["gender_hint"] = "female"
    else:
        c["gender_hint"] = "neutral"
    updated += 1

d["meta"]["version"] = "1.1"
d["meta"]["extended_fields"] = ["rare_flag", "difficult_flag", "homophone_risk", "gender_hint"]
json.dump(d, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 统计
from collections import Counter
g = Counter(c["gender_hint"] for c in d["chars"])
df = [c["char"] for c in d["chars"] if c["difficult_flag"]]
hr = [c["char"] for c in d["chars"] if c["homophone_risk"]]
print("更新完成:", updated, "字")
print("性别倾向分布:", dict(g))
print("difficult_flag(简体>20画):", df)
print("homophone_risk 标注:", hr)
