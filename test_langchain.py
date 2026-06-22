"""测试 LangChain + DashScope 集成"""
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 设置 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')

# DashScope OpenAI 兼容模式配置
API_KEY = "sk-c3486a14e5e64610b8cd7caaa117d21a"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3.7-plus"

def test_langchain():
    """测试 LangChain 调用"""
    print("Initializing LLM...")

    llm = ChatOpenAI(
        model=MODEL,
        temperature=0.7,
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    print("Sending request...")

    messages = [
        SystemMessage(content="你是一个智能学习助手。"),
        HumanMessage(content="请用一句话介绍什么是机器学习。")
    ]

    try:
        response = llm.invoke(messages)
        print(f"\nResponse:\n{response.content}")
        return True
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    print("Testing LangChain + DashScope integration...\n")
    if test_langchain():
        print("\nIntegration test successful!")
    else:
        print("\nIntegration test failed!")
