import os
from openai import OpenAI
import argparse

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),  # 从环境变量中读取 API Key
    base_url="https://ark.cn-beijing.volces.com/api/v3",  # 替换为实际的 API 地址
)

def chat_with_ai(prompt):
    """
    向 AI 服务发送请求并获取响应
    """
    try:
        completion = client.chat.completions.create(
            model="deepseek-v3-241226",  # 替换为实际的模型 ID
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def interactive_chat():
    """
    实现终端交互式对话
    """
    print("Welcome to the AI Terminal Chat! Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            ai_response = chat_with_ai(user_input)
            print(f"AI: {ai_response}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

def main():
    """
    主函数，解析命令行参数并启动对话
    """
    parser = argparse.ArgumentParser(description="Terminal AI Agent")
    parser.add_argument("ag", nargs="?", help="Start the AI chat agent")
    args = parser.parse_args()

    if args.ag:
        interactive_chat()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()