DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD_HERE', 
    'database': 'bilibili_data'
}
SESSDATA = "YOUR_SESSDATA_HERE"

# 构造请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": f"SESSDATA={SESSDATA}",  
    "Referer": "https://space.bilibili.com/"
}

# 3. 目标账号列表 
TARGET_UIDS = {
    946974: "影视飓风",        # 主号
    407054668: "亿点点不一样", # 亿点点不一样！
    1780480185: "飓多多StormCrew" # 飓多多StormCrew
}