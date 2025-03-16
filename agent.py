#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import time
import requests
from threading import Event, Thread
from openai import OpenAI
from bs4 import BeautifulSoup

# 配置信息
MODEL_ID = "deepseek-v3-241226"
API_KEY = os.environ.get("ARK_API_KEY")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
LOG_FILE = "ai_log.txt"
HOT_SITES = ['zhihu', 'weibo', 'github', 'juejin']

# 初始化 OpenAI 客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

class Spinner:
    """加载动画类"""
    def __init__(self):
        self.spinner_chars = '|/-\\'
        self.stop_event = Event()

    def spin(self):
        """显示旋转动画"""
        i = 0
        while not self.stop_event.is_set():
            sys.stdout.write(f'\r{self.spinner_chars[i]} 正在思考...  ')
            sys.stdout.flush()
            i = (i + 1) % 4
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * 20 + '\r')  # 清除动画

def log_interaction(query, response):
    """记录对话到日志文件"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"Q: {query}\nA: {response}\n\n")

def get_hot_list():
    """获取热榜数据"""
    try:
        url = "https://tophub.today"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {}
        for site in HOT_SITES:
            div = soup.find('div', id=site)
            if div:
                items = div.select('.table tbody tr')[:3]
                results[site] = [
                    (tr.select_one('td a').text.strip(),
                     tr.select_one('td a')['href'])
                    for tr in items
                ]
        return results
    except Exception as e:
        return f"Error fetching hot list: {str(e)}"

def translate_text(text, target_lang):
    """执行翻译并格式化输出"""
    prompt = f"将以下内容翻译成{target_lang}，保持格式不变:\n{text}"
    spinner = Spinner()
    spinner.stop_event.clear()
    
    try:
        # 启动加载动画线程
        t = Thread(target=spinner.spin)
        t.start()

        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}]
        )
        response = completion.choices[0].message.content.strip()
        
        # 停止动画并记录日志
        spinner.stop_event.set()
        t.join()
        
        # 格式化输出
        print("\n原文:")
        print(text)
        print("\n译文:")
        print(response)
        log_interaction(prompt, response)
        return response
    except Exception as e:
        spinner.stop_event.set()
        print(f"\nError: {str(e)}")
        return None

def interactive_chat(long_context=False):
    """交互式对话模式"""
    messages = []
    if long_context:
        messages.append({"role": "system", "content": "你是一个能干的助手，需要记住对话历史"})
    
    print("进入对话模式（输入 exit 退出）")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            # 显示加载动画
            spinner = Spinner()
            spinner.stop_event.clear()
            t = Thread(target=spinner.spin)
            t.start()

            # 维护上下文
            messages.append({"role": "user", "content": user_input})
            completion = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages[-10:]  # 保留最近10条消息
            )
            response = completion.choices[0].message.content.strip()
            
            # 停止动画并显示结果
            spinner.stop_event.set()
            t.join()
            
            print(f"A: {response}")
            messages.append({"role": "assistant", "content": response})
            log_interaction(user_input, response)

        except KeyboardInterrupt:
            print("\n再见！")
            break

def ai_mode():
    """AI模式主逻辑"""
    parser = argparse.ArgumentParser(description="AI终端助手", add_help=False)
    parser.add_argument('-l', '--long', action='store_true', help="开启长对话模式")
    parser.add_argument('-t', '--translate', nargs=1, metavar='LANG', help="翻译模式")
    parser.add_argument('-h', '--hot', action='store_true', help="显示今日热榜")
    
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            # 解析输入
            args = parser.parse_args(user_input.split())

            # 热榜查询
            if args.hot:
                print("正在获取今日热榜...")
                hot_data = get_hot_list()
                if isinstance(hot_data, dict):
                    for site, items in hot_data.items():
                        print(f"\n{site.upper()} 热榜前三:")
                        for idx, (title, link) in enumerate(items, 1):
                            print(f"{idx}. {title}")
                            print(f"   {link}")
                else:
                    print(hot_data)
                continue

            # 翻译模式
            if args.translate:
                target_lang = args.translate[0]
                text = ' '.join(user_input.split()[2:]) if len(user_input.split()) > 2 else input("请输入要翻译的内容: ")
                if not text:
                    print("错误: 需要提供翻译内容")
                    continue
                translate_text(text, target_lang)
                continue

            # 长对话模式
            if args.long:
                interactive_chat(long_context=True)
                continue

            # 默认单次问答
            spinner = Spinner()
            spinner.stop_event.clear()
            t = Thread(target=spinner.spin)
            t.start()

            completion = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": user_input}]
            )
            response = completion.choices[0].message.content.strip()
            
            spinner.stop_event.set()
            t.join()
            
            print(f"A: {response}")
            log_interaction(user_input, response)

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {str(e)}")

def main():
    # 如果没有参数或第一个参数不是ag，则直接执行系统命令
    '''
    if len(sys.argv) == 1 or sys.argv[1] != 'ag':
        cmd = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'echo "请输入命令"'
        result = subprocess.run(cmd, shell=True, text=True)
        sys.exit(result.returncode)
    '''
    # 进入AI模式
    print("进入AI模式（输入 exit 退出）")
    ai_mode()

if __name__ == "__main__":
    main()