import pandas as pd
import json
import re
from datetime import datetime, timedelta

xls = pd.ExcelFile('C:/Users/01/Downloads/卡女士减脂情况汇总.xlsx')
df = pd.read_excel(xls, sheet_name='卡女士减脂汇总', header=None)

def parse_date(v):
    if pd.isna(v): return None
    if isinstance(v, datetime): return v.strftime('%Y-%m-%d')
    return str(v)[:10]

def safe(v):
    return '' if pd.isna(v) else str(v).strip()

def parse_exercise(text):
    """从运动文本中提取结构化数据"""
    if not text or text == 'NaN': return None
    ex = {'type': '运动', 'notes': text[:200]}
    
    # 距离
    m = re.search(r'(\d+\.?\d*)\s*(公里|km)', text)
    if m: ex['distance'] = float(m.group(1))
    
    # 时长
    m = re.search(r'用时\s*(\d+)\s*分(?:钟)?\s*(\d+)?\s*秒?', text)
    if m:
        ex['duration'] = int(m.group(1)) + (int(m.group(2)) / 60 if m.group(2) else 0)
    
    # 消耗
    m = re.search(r'消耗\s*(\d+)\s*(大卡|千卡|kcal)', text)
    if m: ex['calories'] = int(m.group(1))
    
    # 类型判断（注意顺序：休息优先，晨跑也包含跑步）
    if re.search(r'休息|暂停训练|主动休息', text):
        ex['type'] = '休息'
    elif re.search(r'晨跑|跑步|慢跑|户外跑', text):
        ex['type'] = '跑步'
    elif re.search(r'快走|走路', text):
        ex['type'] = '快走'
    elif '普拉提' in text:
        ex['type'] = '普拉提'
    elif '无氧' in text:
        ex['type'] = '无氧'
    
    return ex

def parse_meal(text, meal_name):
    """解析一餐的内容"""
    if not text or text == 'NaN': return None
    # 尝试提取时间
    m = re.search(r'(\d{1,2}:\d{2})', text)
    time_str = m.group(1) if m else ''
    desc = text.strip()
    return {'time': time_str, 'name': meal_name, 'description': desc[:300]}

def parse_bowel(text):
    if not text or text == 'NaN': return None
    t = str(text)
    # 排除无实际记录的情况
    if re.search(r'无记录|NaN|^$', t): return None
    if re.search(r'无|未排|没有|不正常|不通畅', t): return False
    return True

# 解析每一行
logs = {}
meal_cols = [(5, '早餐'), (6, '上午加餐'), (7, '午餐'), (8, '下午加餐'), (9, '晚餐')]

for idx, row in df.iterrows():
    if idx < 2: continue  # skip headers
    
    date_str = parse_date(row[0])
    if not date_str: continue
    
    day_data = {
        'meals': [],
        'exercise': None,
        'waterEntries': [],
        'bowel': None,
        'weightEntries': [],
        'wake_time': None,
        'sleep_time': None
    }
    
    # 体重
    morning_w = row[2]
    if not pd.isna(morning_w) and isinstance(morning_w, (int, float)):
        day_data['weightEntries'].append({'time': '07:00', 'value': float(morning_w), 'type': 'morning'})
    
    night_w = row[3]
    if not pd.isna(night_w) and isinstance(night_w, (int, float)):
        day_data['weightEntries'].append({'time': '22:00', 'value': float(night_w), 'type': 'night'})
    
    # 运动
    ex_text = safe(row[4])
    day_data['exercise'] = parse_exercise(ex_text)
    
    # 三餐
    for col, name in meal_cols:
        meal = parse_meal(safe(row[col]), name)
        if meal:
            # 试图从运动文本中推断早餐时间
            if name == '早餐' and not meal['time']:
                m = re.search(r'(\d{1,2}:\d{2})', ex_text)
                if m: meal['time'] = m.group(1)
            day_data['meals'].append(meal)
    
    # 排便
    day_data['bowel'] = parse_bowel(safe(row[10]))
    
    logs[date_str] = day_data

# 输出 JSON
output = {'logs': logs}
with open('C:/Users/01/WorkBuddy/Claw/import_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ 已解析 {len(logs)} 天数据")
for d in sorted(logs.keys()):
    l = logs[d]
    meals_count = len(l['meals'])
    w = l['weightEntries'][0]['value'] if l['weightEntries'] else '?'
    ex = l['exercise']['type'] if l['exercise'] else '无'
    print(f"  {d} | 体重:{w}kg | {meals_count}餐 | 运动:{ex} | 排便:{l['bowel']}")
