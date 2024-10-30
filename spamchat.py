import requests
import time
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

def get_headers(access_token):
    return {
        'authority': 'gql.twitch.tv',
        'accept': '*/*',
        'accept-language': 'en-GB',
        'authorization': f'OAuth {access_token}',
        'client-id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
        'client-session-id': '26d2ef6932fcbcb7',
        'client-version': '062c06fe-6f90-4119-ad8a-a52f522ec60c',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://m.twitch.tv',
        'referer': 'https://m.twitch.tv/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'x-device-id': 'VNwu0VNCnd4kIKfyzFIzJBsSLIssjlgq'
    }

def get_proxies():
    try:
        response = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http,socks5&timeout=3000&country=all&simplified=true")
        if response.status_code == 200:
            return response.text.strip().splitlines()
    except requests.RequestException:
        return []
    return []

def load_tokens(filename="tokensaccs.txt"):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

async def get_streamer_info(channel_id, headers):
    url = f"https://api.twitch.tv/helix/users?id={channel_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data'][0]
        print(Fore.GREEN + Style.BRIGHT + f"\n    VIEWS ➤ {data.get('view_count')}")
        print(f"    USERNAME ➤ {data.get('display_name')}")
        print(f"    BIO STREAMER ➤ {data.get('description')}\n")

async def send_message(channel_id, message, access_token):
    headers = get_headers(access_token)
    url = 'https://gql.twitch.tv/gql'
    proxies_list = get_proxies()
    data = {
        "operationName": "sendChatMessage",
        "variables": {
            "input": {
                "channelID": channel_id,
                "message": message,
                "nonce": "8b6f9a6b4d56eaf0d154aa021e31e0c8",
                "replyParentMessageID": None
            }
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0435464292cf380ed4b3d905e4edcb73078362e82c06367a5b2181c76c822fa2"
            }
        }
    }
    for proxy in proxies_list:
        proxy_dict = {'http': f"http://{proxy}", 'https': f"http://{proxy}"}
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy_dict, timeout=1)
            if response.status_code == 200:
                print(f"Message sent successfully with proxy {proxy}")
                break
        except requests.RequestException:
            continue
        await asyncio.sleep(0.1)

async def main():
    tokens = load_tokens()
    if tokens:
        print(Fore.GREEN + Style.BRIGHT + "➤ ✅ ALL Access TOKENS READY FOR SEND SPAM CHAT")
    else:
        print(Fore.RED + "No tokens found in tokensaccs.txt")
        return

    channel_id = input(Fore.GREEN + "➤ @ Type Your Streamer Channel id here: ")
    message = input(Fore.GREEN + "➤ ENTER MESSAGES U WANT TO SEND TO STREAMER [STATUS OF TOKENS?: READY]: ")
    repeat_count = int(input("➤ Type how much u need to send the message: "))

    await get_streamer_info(channel_id, get_headers(tokens[0]))

    tasks = []
    for _ in range(repeat_count):
        for token in tokens:
            tasks.append(send_message(channel_id, message, token))
            if len(tasks) >= 100:
                await asyncio.gather(*tasks)
                tasks = []

    if tasks:
        await asyncio.gather(*tasks)

asyncio.run(main())
