import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from config import DB_CONFIG

# ==========================================
# 0. 准备工作：设置中文字体和绘图风格
# ==========================================
# 解决中文显示为方块的问题 (Windows通常是SimHei或Microsoft YaHei)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

# 设置 Seaborn 主题，让图表更好看
sns.set_theme(style="whitegrid", font='SimHei')

# 创建输出文件夹
if not os.path.exists('output'):
    os.makedirs('output')

# ==========================================
# 1. 从 MySQL 读取数据
# ==========================================
def get_data_from_mysql():
    print("🔌 正在从数据库读取数据...")
    db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    engine = create_engine(db_url)
    
    # 直接读取整张表
    df = pd.read_sql("SELECT * FROM videos", engine)
    print(f"✅ 成功加载 {len(df)} 条数据")
    return df

# ==========================================
# 2. 分析图表制作
# ==========================================

def plot_account_comparison(df):
    """分析1: 三个账号的总播放量对比 (饼图)"""
    print("📊 正在绘制：账号流量占比...")
    
    # 按账号分组求和
    account_stats = df.groupby('source_account')['views'].sum().reset_index()
    
    plt.figure(figsize=(10, 6))
    # 绘制饼图
    plt.pie(account_stats['views'], labels=account_stats['source_account'], autopct='%1.1f%%', 
            startangle=140, colors=sns.color_palette("pastel"))
    
    plt.title('影视飓风矩阵号 - 总播放量占比', fontsize=16)
    plt.savefig('output/1_account_comparison.png')
    plt.close() # 关闭画布释放内存

def plot_publish_heatmap(df):
    """分析2: 发布时间热力图 (周几 vs 几点)"""
    print("📊 正在绘制：发布时间热力图...")
    
    # 确保时间列是 datetime 类型
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    
    # 提取 "星期几" (0是周一, 6是周日) 和 "小时"
    df['weekday'] = df['pub_date'].dt.day_name()
    df['hour'] = df['pub_date'].dt.hour
    
    # 排序：让周一排在前面
    week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # 透视表：计算每个时间段的平均播放量
    heatmap_data = df.pivot_table(index='weekday', columns='hour', values='views', aggfunc='mean')
    # 重新索引，保证星期顺序正确
    heatmap_data = heatmap_data.reindex(week_order)
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap='OrRd', linewidths=.5, fmt='.0f')
    
    plt.title('什么时候发视频播放量最高？(平均播放量热力图)', fontsize=16)
    plt.xlabel('发布时间 (小时)')
    plt.ylabel('星期')
    plt.tight_layout()
    plt.savefig('output/2_publish_time_heatmap.png')
    plt.close()

def plot_duration_vs_views(df):
    """分析3: 视频时长与播放量的关系 (散点图)"""
    print("📊 正在绘制：时长与播放量关系图...")
    
    plt.figure(figsize=(12, 6))
    
    # 过滤掉极端的长视频（比如超过60分钟的直播录屏），以免图表被拉得太长看不清
    # 过滤掉播放量极高的个别爆款，看整体趋势
    plot_df = df[(df['duration_sec'] < 3600) & (df['views'] < 5000000)]
    
    # 转换成分钟方便阅读
    plot_df['duration_min'] = plot_df['duration_sec'] / 60
    
    # 散点图
    sns.scatterplot(data=plot_df, x='duration_min', y='views', hue='source_account', alpha=0.6)
    
    plt.title('视频越长播放越高吗？(时长 vs 播放量)', fontsize=16)
    plt.xlabel('视频时长 (分钟)')
    plt.ylabel('播放量')
    plt.legend(title='账号')
    plt.tight_layout()
    plt.savefig('output/3_duration_analysis.png')
    plt.close()

def plot_top_10(df):
    """分析4: 全站播放量最高的 Top 10 视频"""
    print("📊 正在绘制：Top 10 榜单...")
    
    # 排序取前10
    top10 = df.sort_values(by='views', ascending=False).head(10)
    
    plt.figure(figsize=(12, 8))
    # 横向柱状图
    sns.barplot(data=top10, y='title', x='views', hue='source_account', dodge=False)
    
    plt.title('影视飓风全矩阵 - 播放量 Top 10 视频', fontsize=16)
    plt.xlabel('播放量')
    plt.ylabel('') # 标题太长，隐藏Y轴标签
    plt.tight_layout()
    plt.savefig('output/4_top_videos.png')
    plt.close()

if __name__ == "__main__":
    # 1. 获取数据
    df = get_data_from_mysql()
    
    # 2. 执行分析
    plot_account_comparison(df)
    plot_publish_heatmap(df)
    plot_duration_vs_views(df)
    plot_top_10(df)
    
    print("\n🚀 所有分析图表已生成！请查看 output 文件夹！")