import requests
import time
import json
import os
import hashlib
import urllib.parse
from functools import reduce
from config import HEADERS, TARGET_UIDS, SESSDATA

# 创建数据存储目录
if not os.path.exists('data'):
    os.makedirs('data')

# ==========================================
# 🔐 Wbi 签名算法 (这是 B 站反爬的核心破解逻辑)
# 这一段看不懂没关系，这是标准的解密公式
# ==========================================
MixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]

def getMixinKey(orig: str):
    '对 imgKey 和 subKey 进行字符顺序打乱编码'
    return reduce(lambda s, i: s + orig[i], MixinKeyEncTab, '')[:32]

def encWbi(params: dict, img_key: str, sub_key: str):
    '为请求参数进行 wbi 签名'
    mixin_key = getMixinKey(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time # 添加时间戳
    # 参数排序
    params = dict(sorted(params.items()))
    # 过滤不用签名的字符
    params = {
        k : ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v in params.items()
    }
    # 拼接参数
    query = urllib.parse.urlencode(params)
    # 计算签名
    w_rid = hashlib.md5((query + mixin_key).encode(encoding='utf-8')).hexdigest()
    params['w_rid'] = w_rid
    return params

def getWbiKeys():
    '获取最新的加密钥匙 (img_key, sub_key)'
    try:
        resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=HEADERS)
        resp.raise_for_status()
        json_content = resp.json()
        img_url = json_content['data']['wbi_img']['img_url']
        sub_url = json_content['data']['wbi_img']['sub_url']
        img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
        return img_key, sub_key
    except Exception as e:
        print(f"❌ 获取密钥失败: {e}")
        return None, None

# ==========================================
# 🕷️ 核心爬虫逻辑 (已升级)
# ==========================================

def fetch_videos(uid, name):
    print(f"🎬 正在分析: {name} (UID: {uid})")
    
    # 1. 每次抓取前，先去获取一把“钥匙”
    img_key, sub_key = getWbiKeys()
    if not img_key or not sub_key:
        print("   -> 无法获取签名密钥，跳过此UP主")
        return

    all_videos = []
    page = 1
    
    while True:
        url = "https://api.bilibili.com/x/space/wbi/arc/search"
        
        # 基础参数
        params = {
            "mid": uid,
            "ps": 30,
            "tid": 0,
            "pn": page,
            "order": "pubdate",
            "keyword": ""
        }
        
        # ⚡️ 关键动作：给参数签名 (加上 w_rid)
        signed_params = encWbi(params, img_key, sub_key)

        # 动态修改 Referer (B站检查这个)
        current_headers = HEADERS.copy()
        current_headers['Referer'] = f"https://space.bilibili.com/{uid}/"

        try:
            response = requests.get(url, headers=current_headers, params=signed_params)
            data = response.json()

            if data['code'] != 0:
                print(f"❌ 接口报错: {data['message']}")
                # 如果是权限不足，可能是 Cookie 过期，或者反爬太严
                break

            vlist = data['data']['list']['vlist']
            
            if not vlist:
                print(f"✅ {name} 抓取完成，共 {len(all_videos)} 个视频")
                break

            all_videos.extend(vlist)
            print(f"   -> 第 {page} 页抓取成功，本页 {len(vlist)} 条 | 最新视频: {vlist[0]['title'][:15]}...")

            page += 1
            # 随机休眠 1.5 到 3 秒，模仿人类行为，防止太快被封
            time.sleep(2)

        except Exception as e:
            print(f"❌ 发生异常: {e}")
            break

    # 保存
    if all_videos:
        filename = f"data/{name}_{uid}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, ensure_ascii=False, indent=4)
        print(f"💾 数据已保存到: {filename}\n")
    else:
        print(f"⚠️ {name} 没有抓取到任何数据\n")

if __name__ == "__main__":
    print("🚀 启动 Bilibili 爬虫 (Wbi签名版)...")
    print(f"🔑 当前使用的 SESSDATA 结尾: ...{SESSDATA[-6:]}")
    print("-" * 50)
    
    for uid, name in TARGET_UIDS.items():
        fetch_videos(uid, name)
        
    print("🎉 所有任务结束！")