import pandas as pd
import json
import os
import glob
from sqlalchemy import create_engine
from datetime import datetime
from config import DB_CONFIG

# ==========================================
# 🛠️ 辅助函数：处理数据格式
# ==========================================

def process_timestamp(ts):
    """把 B站的 Unix 时间戳 (秒) 转换为标准日期时间格式"""
    if pd.isna(ts):
        return None
    try:
        return datetime.fromtimestamp(int(ts))
    except:
        return None

def time_str_to_seconds(t_str):
    try:
        parts = str(t_str).split(':')
        if len(parts) == 2: # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3: # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    except:
        return 0

# ==========================================
# 1. 提取与转换 (Extract & Transform)
# ==========================================

def load_and_clean_data():
    print("🧹 开始 ETL 数据清洗流程...")
    
    # 1. 读取 data 文件夹下所有的 .json 文件
    json_files = glob.glob(os.path.join("data", "*.json"))
    if not json_files:
        print("❌ 错误: data 文件夹里没有找到 JSON 文件！")
        print("💡 提示: 请先运行 scraper.py 抓取数据。")
        return None

    all_videos = []
    
    # 2. 循环读取每个文件
    for file in json_files:
        print(f"   -> 正在读取文件: {file}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 从文件名提取UP主名字 (例如 "影视飓风_946974.json" -> "影视飓风")
                source_name = os.path.basename(file).split('_')[0]
                
                # 给每条数据打上标签，标记来源
                for v in data:
                    v['source_account'] = source_name
                
                all_videos.extend(data)
        except Exception as e:
            print(f"⚠️ 读取文件 {file} 出错: {e}")

    print(f"📦 原始数据加载完毕，共 {len(all_videos)} 条")

    # 3. 转换为 Pandas DataFrame
    df = pd.DataFrame(all_videos)

    # 4. 字段筛选与补全
    # 我们需要的核心字段
    keep_cols = ['bvid', 'title', 'created', 'length', 'play', 'video_review', 'comment', 'source_account', 'pic']
    
    # 防止某些视频缺少字段导致报错，如果缺少就填 0
    for col in keep_cols:
        if col not in df.columns:
            df[col] = 0
            
    # 只保留我们需要的列
    df = df[keep_cols]

    # 5. 重命名列 (让数据库字段更专业)
    df.rename(columns={
        'created': 'pub_date',      # 发布时间
        'video_review': 'danmaku',  # 弹幕数
        'play': 'views',            # 播放量
        'pic': 'cover_url'          # 封面链接
    }, inplace=True)

    # 6. 数据类型转换
    print("   -> 正在转换时间格式和时长...")
    df['pub_date'] = df['pub_date'].apply(process_timestamp)
    df['duration_sec'] = df['length'].apply(time_str_to_seconds)

    # 7. 去重 (以 bvid 视频ID 为准，防止重复抓取的数据堆积)
    original_count = len(df)
    df.drop_duplicates(subset=['bvid'], keep='first', inplace=True)
    print(f"   -> 去重完成: 删除了 {original_count - len(df)} 条重复数据")

    print(f"✨ 清洗完成！准备入库有效数据: {len(df)} 条")
    return df

# ==========================================
# 2. 加载入库 (Load to MySQL)
# ==========================================

def save_to_mysql(df):
    try:
        # 构建 MySQL 连接字符串
        # 格式: mysql+mysqlconnector://用户名:密码@地址/数据库名
        db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
        
        # 创建数据库引擎
        engine = create_engine(db_url)
        
        print("🔌 正在连接 MySQL 数据库...")
        
        # 写入数据
        # if_exists='replace': 如果表存在，就删除重建 (适合全量刷新)
        # index=False: 不把 pandas 的索引写入数据库
        df.to_sql(name='videos', con=engine, if_exists='replace', index=False)
        
        print("✅ ===========================================")
        print(f"🎉 成功！已将 {len(df)} 条视频数据存入 MySQL 的 [videos] 表中。")
        print("✅ ===========================================")
        
    except Exception as e:
        print(f"❌ 数据库写入失败: {e}")
        print("\n💡 故障排查:")
        print("1. 请检查 config.py 里的密码是否填对 (应该是 101510)")
        print("2. 请检查是否已经在 MySQL 里创建了 bilibili_data 数据库")

if __name__ == "__main__":
    # 执行流程
    df = load_and_clean_data()
    if df is not None:
        save_to_mysql(df)