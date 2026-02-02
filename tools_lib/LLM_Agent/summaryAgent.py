import json
from tools_lib.LLM_Agent.local_llm import qwen3_14b
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from tools_lib.LLM_Agent.Prompt import SUMMARY_PROMPT
    
class SummaryAgent:
    def __init__(self):
        self.summaryagent = create_agent(
            model=qwen3_14b,
            system_prompt= SUMMARY_PROMPT,
        )
    
    def summary(self, batch_texts,topic):
        # 应该为批处理，否则此处必 炸
        
        return ""




# 使用示例
if __name__ == "__main__":
    # 创建Agent实例
    pass
    # 启动循环对话
    # agent.chat_loop("conversation_1")
    
    # 或者启动带历史记录的循环对话
