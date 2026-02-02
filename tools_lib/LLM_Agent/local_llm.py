# -*- coding: utf-8 -*-
from langchain_ollama import ChatOllama
# 1. 本地模型
qwen3_14b = ChatOllama(model="qwen3:14b",temperature=0.7,
)
