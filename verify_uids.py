import requests

def get_user_info(mid):
    url = f"https://api.bilibili.com/x/space/acc/info?mid={mid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data['code'] == 0:
            print(f"MID: {mid}, Name: {data['data']['name']}")
        else:
            print(f"MID: {mid}, Error: {data['message']}")
    except Exception as e:
        print(f"MID: {mid}, Exception: {e}")

# Test potential UIDs
get_user_info(946974)
get_user_info(10318081)
get_user_info(163637592) # From my initial plan, maybe correct?
