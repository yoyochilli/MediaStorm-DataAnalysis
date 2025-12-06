# 🎬 Bilibili 影视飓风频道数据分析项目 (MediaStorm Data Analysis)

## 📖 项目简介
本项目针对 B 站头部科技媒体**“影视飓风”**及其矩阵号（亿点点不一样、飓多多StormCrew），设计并实现了一套完整的数据采集与分析系统。通过分析 **1000+** 条视频数据，挖掘其流量密码、发布规律及矩阵号运营策略。

## 🛠️ 技术架构 (Tech Stack)
- **数据采集 (Crawler)**: Python `Requests` (破解 Wbi 签名加密 / 自动处理分页与反爬)
- **数据清洗 (ETL)**: `Pandas` (时间戳转换 / 异常值处理 / 数据去重)
- **数据存储 (Database)**: `MySQL 8.0` + `SQLAlchemy` (设计数仓模型 / 自动化入库)
- **可视化 (Visualization)**: `Seaborn` + `Matplotlib` (输出商业洞察报表)

## 📊 核心发现 (Insights)
1.  **矩阵效应**: 影视飓风主号占比 **67%**，副号“亿点点不一样”占比 **21.5%**，已形成健康的矩阵流量结构。
2.  **黄金发布时间**: 虽周末流量大，但 **周一中午 11:00-12:00** 存在显著的流量高峰（午休红利）。
3.  **时长策略**: **10-20分钟** 的中长视频表现最稳，且 40分钟+ 的长视频完播粘性极高。

## 🚀 如何运行 (How to run)

### 1. 克隆项目
首先将项目下载到本地并进入文件夹：
```bash
git clone https://github.com/yoyochilli/MediaStorm-DataAnalysis.git
cd MediaStorm-DataAnalysis


   
   
   
