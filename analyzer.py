import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from config import DB_CONFIG

# ==========================================
# 🎨 0. 极客审美：MediaStorm 定制皮肤
# ==========================================

def set_mediastorm_style():
    """配置极客暗黑风格的绘图参数"""
    # 基础风格：暗色背景
    plt.style.use('dark_background')
    
    # 自定义颜色 (Hex Codes)
    colors = {
        'bg': '#1E1E1E',       # 深灰背景 (类似达芬奇界面)
        'text': '#E0E0E0',     # 亮白文字
        'grid': '#333333',     # 隐约的网格线
        'accent1': '#00ADB5',  # 极客蓝 (用于影视飓风)
        'accent2': '#FF5722',  # 活力橙 (用于亿点点)
        'accent3': '#9C27B0'   # 赛博紫 (用于飓多多)
    }
    
    # 全局参数覆写
    plt.rcParams.update({
        'figure.facecolor': colors['bg'],
        'axes.facecolor': colors['bg'],
        'axes.edgecolor': colors['bg'],     # 去掉边框
        'axes.labelcolor': colors['text'],
        'text.color': colors['text'],
        'xtick.color': colors['text'],
        'ytick.color': colors['text'],
        'grid.color': colors['grid'],
        'grid.linestyle': '--',
        'grid.alpha': 0.5,
        'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'Arial'], # 优先用微软雅黑
        'axes.unicode_minus': False,
        'figure.dpi': 150,                  # 高清输出
        'figure.autolayout': True           # 自动调整布局防遮挡
    })
    return colors

# 初始化风格
COLORS = set_mediastorm_style()
# 定义专属调色盘
CUSTOM_PALETTE = [COLORS['accent1'], COLORS['accent2'], COLORS['accent3']]

if not os.path.exists('output_pro'):
    os.makedirs('output_pro')

# ==========================================
# 1. 数据读取 (和之前一样)
# ==========================================
def get_data():
    db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    engine = create_engine(db_url)
    return pd.read_sql("SELECT * FROM videos", engine)

# ==========================================
# 2. 高级可视化图表
# ==========================================

def plot_donut_chart(df):
    """图表1：环形图 (比饼图更高级)"""
    print("🎨 正在绘制：流量占比环形图...")
    
    stats = df.groupby('source_account')['views'].sum().reset_index()
    stats = stats.sort_values(by='views', ascending=False)
    
    plt.figure(figsize=(10, 8))
    
    # 绘制环形
    wedges, texts, autotexts = plt.pie(
        stats['views'], 
        labels=stats['source_account'], 
        autopct='%1.1f%%', 
        startangle=90,
        colors=CUSTOM_PALETTE,
        pctdistance=0.85,  #百分比距离圆心的距离
        wedgeprops={'width': 0.4, 'edgecolor': COLORS['bg'], 'linewidth': 2}, # 关键：width<1 变成环形
        textprops={'fontsize': 12, 'color': COLORS['text']}
    )
    
    # 修改百分比字体的颜色和粗细
    for text in autotexts:
        text.set_color('white')
        text.set_weight('bold')

    plt.title('MEDIASTORM MATRIX TRAFFIC\n全矩阵播放量占比', fontsize=18, fontweight='bold', pad=20)
    # 中间加个 Logo 感觉的文字
    plt.text(0, 0, 'Total\nViews', ha='center', va='center', fontsize=14, color='white', fontweight='bold')
    
    plt.savefig('output_pro/1_Traffic_Donut.png')
    plt.close()

def plot_heatmap_dark(df):
    """图表2：暗夜热力图"""
    print("🎨 正在绘制：发布时间热力图...")
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    df['weekday'] = df['pub_date'].dt.day_name()
    df['hour'] = df['pub_date'].dt.hour
    week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    heatmap_data = df.pivot_table(index='weekday', columns='hour', values='views', aggfunc='mean')
    heatmap_data = heatmap_data.reindex(week_order)
    
    plt.figure(figsize=(14, 7))
    
    # 使用 'rocket' 或 'magma' 这种深色系渐变，更有科技感
    sns.heatmap(heatmap_data, cmap='rocket', linewidths=0.5, linecolor=COLORS['bg'],
                cbar_kws={'label': 'Average Views'})
    
    plt.title('PRIME TIME ANALYSIS\n最佳发布时间热力分布', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('')
    plt.savefig('output_pro/2_Time_Heatmap.png')
    plt.close()

def plot_scatter_glow(df):
    """图表3：带“荧光感”的散点图"""
    print("🎨 正在绘制：时长分布散点图...")
    plt.figure(figsize=(12, 7))
    
    plot_df = df[(df['duration_sec'] < 3600) & (df['views'] < 5000000)].copy()
    plot_df['duration_min'] = plot_df['duration_sec'] / 60
    
    # 使用 hue 区分账号，style 区分形状
    sns.scatterplot(
        data=plot_df, 
        x='duration_min', 
        y='views', 
        hue='source_account', 
        palette=CUSTOM_PALETTE,
        alpha=0.8,       # 透明度
        s=60,            # 点的大小
        edgecolor=None   # 去掉点的边框，看起来更柔和
    )
    
    plt.title('DURATION vs PERFORMANCE\n时长与播放量关系 (黄金区间分析)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Duration (Minutes)', fontsize=12)
    plt.ylabel('Views', fontsize=12)
    plt.legend(frameon=False, labelcolor='white') # 去掉图例边框
    plt.grid(True, alpha=0.2) # 弱化网格
    
    plt.savefig('output_pro/3_Scatter_Tech.png')
    plt.close()

def plot_bar_ranking(df):
    """图表4：极简风 Top 10 条形图"""
    print("🎨 正在绘制：Top 10 榜单...")
    top10 = df.sort_values(by='views', ascending=False).head(10)
    
    plt.figure(figsize=(12, 8))
    
    # 使用单一渐变色或按账号着色
    bar_plot = sns.barplot(
        data=top10, 
        y='title', 
        x='views', 
        hue='source_account',
        palette=CUSTOM_PALETTE,
        dodge=False
    )
    
    # 去掉所有边框
    sns.despine(left=True, bottom=True)
    
    # 在柱子末尾添加数字标签
    for container in bar_plot.containers:
        bar_plot.bar_label(container, fmt='%.0f', padding=5, color='white', fontsize=10)
    
    plt.title('TOP 10 BLOCKBUSTERS\n全站播放量榜首视频', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('')
    plt.ylabel('')
    plt.xticks([]) # 隐藏X轴刻度（因为已经标在柱子上了）
    plt.legend(frameon=False, loc='lower right')
    
    plt.savefig('output_pro/4_Ranking_Pro.png')
    plt.close()

if __name__ == "__main__":
    df = get_data()
    plot_donut_chart(df)
    plot_heatmap_dark(df)
    plot_scatter_glow(df)
    plot_bar_ranking(df)
    print("\n✨ 请查看 output_pro 文件夹！")