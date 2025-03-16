import os
import argparse
from volcenginesdkarkruntime import Ark  # 修改导入方式

# 初始化方舟客户端
client = Ark(
    api_key=os.environ.get("ARK_API_KEY")  # 从环境变量读取API Key
)

def chat_with_ai(prompt):
    """
    向AI服务发送请求并获取响应
    """
    try:
        completion = client.chat.completions.create(
            model="deepseek-v3-241226",  # 
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # 提取响应内容（假设响应结构与OpenAI兼容）
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def interactive_chat():
    """
    终端交互式对话功能
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
    主函数
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