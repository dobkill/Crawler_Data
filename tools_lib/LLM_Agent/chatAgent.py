from langchain.agents.middleware import AgentMiddleware
from langchain.agents import create_agent
from tools_lib.LLM_Agent.local_llm import qwen3_14b
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, AgentState
from langgraph.runtime import Runtime
from typing import Any
from tools_lib.Web_tools.GoogleSearchAPI import search_google,open_web_page
from tools_lib.LLM_Agent.Prompt import USE_TOOLS_PROMPT
# ==================== 工具定义 ====================
class HelloMiddleware(AgentMiddleware):
    """记录每次模型调用的自定义中间件"""
    
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # 在模型调用前记录日志
        text = state['messages'][-1].text
        type = state['messages'][-1].type
        print(f"调用模型前，消息数量: {len(state['messages'])}")
        return None
    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # 在模型响应后记录日志
        print(f"模型已响应")
        return None
class Agent:
    def __init__(self):
        self.config = {"configurable": {"thread_id": "1"}}
        self.checkpointer = InMemorySaver()
        tools = [search_google, open_web_page]
        self.agent = create_agent(
            model=qwen3_14b,
            tools=tools,
            system_prompt= USE_TOOLS_PROMPT,
            middleware=[HelloMiddleware()],
            checkpointer=self.checkpointer,
        )
    
    def chat(self, query, id):
        self.config["configurable"]["thread_id"] = id
        result = self.agent.invoke(
            {"messages": [HumanMessage(content=query)]},
            config=self.config
        )
        ai_message = result["messages"][-1]
        return ai_message.content
    
    def chat_loop(self, thread_id="1"):
        """
        启动循环对话
        
        Args:
            thread_id (str): 会话ID，默认为"1"
        """
        print("Agent对话已启动，输入 '退出' 或 'quit' 结束对话")
        print("-" * 40)
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n请输入您的问题: ").strip()
                
                # 检查退出条件
                if user_input.lower() in ['退出', 'quit', 'exit', '']:
                    print("对话结束，再见！")
                    break
                
                # 执行对话
                response = self.chat(user_input, thread_id)
                
                # 输出AI回复
                print(f"\nAgent回复: {response}")
                
            except KeyboardInterrupt:
                print("\n\n检测到中断信号，结束对话...")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                print("请重试或输入 '退出' 结束对话")
    def get_chat_history(self, thread_id="1"):
        state = self.agent.get_state( {"configurable": {"thread_id": thread_id}})
        messages = state.values.get("messages", [])
        all_history = []
        for msg in messages:
            if msg.__class__.__name__ == "AIMessage":
                all_history.append({"type": "ai","content": msg.content})
            if msg.__class__.__name__ == "HumanMessage":
                all_history.append({"type": "user","content": msg.content})
        print(all_history)
        return all_history
    def clear_history(self, thread_id="1"):
        self.checkpointer.delete_thread(thread_id)
        return "ok"
    def chat_loop_with_history(self, thread_id="1"):
        """
        带历史记录提示的循环对话
        
        Args:
            thread_id (str): 会话ID，默认为"1"
        """
        print("Agent对话已启动（带历史记录）")
        print("命令:")
        print("  '退出' 或 'quit' - 结束对话")
        print("  '历史' 或 'history' - 查看对话历史")
        print("  '清空' 或 'clear' - 清空当前对话历史")
        print("-" * 40)
        
        # 保存当前会话的历史记录
        
        while True:
            try:
                user_input = input("\n请输入您的问题: ").strip()
            
                # 处理特殊命令
                if user_input.lower() in ['退出', 'quit', 'exit', '']:
                    print("对话结束，再见！")
                    break
                elif user_input.lower() in ['历史', 'history']:
                    historry = self.get_chat_history(thread_id)
                    print(historry)
                    continue
                # 执行对话
                response = self.chat(user_input, thread_id)
                print(f"\nAgent回复: {response}")
            except KeyboardInterrupt:
                print("\n\n检测到中断信号，结束对话...")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                print("请重试或输入 '退出' 结束对话")

# 使用示例
if __name__ == "__main__":
    # 创建Agent实例
    agent = Agent()
    
    # 启动循环对话
    # agent.chat_loop("conversation_1")
    
    # 或者启动带历史记录的循环对话
    agent.chat_loop_with_history("conversation_1")