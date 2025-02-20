import sqlite3

# Connect to database
conn = sqlite3.connect('added.db')
c = conn.cursor()
names = ["第 21 场 强者挑战赛", "EPXLQ 2024 fall round", "【LGR-210-Div.3】洛谷基础赛 #19 & ALFR Round 3", "东北大学秦皇岛分校第十二届“图灵杯”程序设计竞赛", "【UM-01】COCI 2024/2025 #3 Unofficial Mirror", "第 5 场 算法季度赛", "【LGR-212-Div.2】洛谷 12 月月赛 II & Cfz Round 5"]

for name in names:
    c.execute("delete from events where name=?", (name,))
    conn.commit()
    
conn.close()
