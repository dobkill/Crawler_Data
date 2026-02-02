import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import BaseModel, Field
from langchain_core.tools import Tool,  tool
from tools_lib.LLM_Agent.summaryAgent import SummaryAgent


class search_googleInput(BaseModel):
    query: str = Field(description="搜索关键词")

@tool( # 告诉AI 这个 tool的作用
        description="""
        使用Goole搜索引擎进行网络搜索，返回与查询相关的搜索结果。
        输入是您想要搜索的关键词或问题。
        """
        ,
        args_schema=search_googleInput
)
def search_google(query):
  url = "https://api.tavily.com/search"
  payload = {
    "api_key": "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",
    "query":query,
    "max_results": 5,
    "search_depth": "basic"
  }
  ans = requests.post(url, json=payload, timeout=15).json()
  return ans["results"]


summaryagent = SummaryAgent()

class OpenWebPageInput(BaseModel):
    url: str = Field(description="网页地址")
    topic: str = Field(description="搜索主题")
@tool( # 告诉AI 这个 tool的作用
        description="""
        输入网页地址url与寻找的内容topic，返回网页中与主题相关的内容
        """
        ,
        args_schema=OpenWebPageInput
)
def OpenWebPage_withAgent(url: str, topic: str,agent) -> str:
    # 获取网页内容
    html = open_web_page(url)
    
    # 文本分割策略：每3000字符一段，重叠1000字符
    chunk_size = 3000
    overlap = 1000
    
    # 将HTML内容拆分为重叠的文本块
    chunks = []
    for i in range(0, len(html), chunk_size - overlap):
        chunk = html[i:i + chunk_size]
        chunks.append(chunk)
        if i + chunk_size >= len(html):
            break
    # 使用LLM为每个块生成与主题相关的摘要
    summaries = []
    for chunk in chunks:
        # 调用LLM生成摘要（这里假设有一个全局的LLM实例）
        summary = summaryagent.summary(chunk, topic)
        summaries.append(summary)
    # 合并所有摘要
    final_output = "\n".join(summaries)
    return final_output
# 打开网页，并返回网页内容
def open_web_page(url)->str:
    """
    打开指定URL的网页并返回网页内容
    Args:
        url (str): 要访问的网页URL
    Returns:
        str: 网页的文本内容
    Raises:
        requests.RequestException: 当网络请求失败时抛出异常
    """
    try:
        # 创建session并设置重试策略
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送GET请求获取网页内容
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # 如果响应状态不是200会抛出异常
        
        # 尝试从响应中获取编码，否则使用utf-8
        encoding = response.encoding if response.encoding else 'utf-8'
        content = response.text
        
        return content
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"无法访问网页 {url}: {str(e)}")
    except Exception as e:
        raise Exception(f"处理网页内容时发生错误: {str(e)}")
__all__ = [
  "search",
  "open_web_page"
]


if __name__ == "__main__":
  ans =search_google("北京最近天气")
