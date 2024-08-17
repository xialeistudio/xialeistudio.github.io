---
title: 基于LLM和搜索引擎构建你的AI搜索机器人
date: 2024-08-15T15:57:11+08:00
slug: build-your-ai-search-bot-with-llm-and-search-engines
tags:
- rag
categories: 
- ai
featured: true
---
在人工智能的浪潮中，大型语言模型（LLM）和搜索引擎的结合为信息检索领域带来了革命性的变化。本文将详细介绍如何利用这些技术构建一个智能信息检索助手——AI搜索机器人。我们将从项目背景、核心原理、代码实现、使用示例以及开源地址等方面进行深入探讨。

<!--more-->

## 项目背景

随着互联网信息量的爆炸性增长，用户在海量数据中寻找答案变得越来越困难。传统的搜索引擎虽然强大，但在理解和处理复杂查询方面仍有局限。为了解决这一问题，本文介绍的AI搜索机器人项目，它利用LLM的深度语义理解和搜索引擎的广度信息检索能力，为用户提供了一个全新的信息检索解决方案。

## 核心原理

AI搜索机器人的核心原理可以概括为以下几个步骤：

1. **搜索引擎检索**：利用搜索引擎检索相关信息并提取TOP10网页内容。
2. **内容提取与整合**：从检索结果中提取有用信息，并进行整合。
3. **LLM处理**：将整合后的信息输入到LLM中，进行深度分析和理解。
4. **智能回答生成**：根据LLM的分析结果，生成智能回答。
5. **结果反馈**：将智能回答反馈给用户，并提供信息来源的链接。

## 代码实现

bot.py

```python
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


# 获取页面body内容
def retrieve_content(item, verbose):
    url = item['url']
    title = item['title']
    try:
        if verbose:
            print(f"retrieving content from {title}")
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'  # 设置编码
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')
        return f"{soup.get_text(strip=True)}\nOriginURL: {url}"  # 获取文本并去除空白字符
    except Exception as e:
        if verbose:
            print(f"failed to retrieve content from {title}: {e}")
        return ""


# 抓取页面列表
def retrieve_pages(links: list, verbose=False) -> str:
    with ThreadPoolExecutor(max_workers=len(links)) as executor:
        contents = list(executor.map(lambda item: retrieve_content(item, verbose=verbose), links))
    return "\n".join(contents)


class SearchBot:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def search(self, query: str) -> Optional[str]:
        links = self.retrieve_urls(query)
        if len(links) == 0:
            return None
        contents = retrieve_pages(links, verbose=self.verbose)
        if self.verbose:
            print(f"search completed, context length: {len(contents)} characters\nGenerating...")
        return contents

    def retrieve_urls(self, query: str) -> list:
        pass


class BingSearchBot(SearchBot):
    def retrieve_urls(self, query: str) -> list:
        encoded_query = quote_plus(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.get_text(strip=True)
        if "blocked" in body:
            raise Exception("Blocked by Bing")

        results = []
        for item in soup.select('.b_algo h2 a'):
            title = item.get_text(strip=True)
            link = item['href']
            results.append({'title': title, 'url': link})
        if len(results) == 0:
            return []
        if self.verbose:
            print(f"searched {len(results)} results")
        return results


class BaiduSearchBot(SearchBot):
    def retrieve_urls(self, query: str) -> list:
        encoded_query = quote_plus(query)
        url = f"https://www.baidu.com/s?wd={encoded_query}"
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('h3.c-title a'):
            title = item.get_text(strip=True)
            link = item['href']
            results.append({'title': title, 'url': link})
        if len(results) == 0:
            return []
        if self.verbose:
            print(f"searched {len(results)} results")
        return results


def make_bot(name: str, verbose=True) -> SearchBot:
    if name == "bing":
        return BingSearchBot(verbose=verbose)
    elif name == "baidu":
        return BaiduSearchBot(verbose=verbose)
    else:
        raise ValueError(f"Unsupported search engine: {name}")
```

rag.py

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaLLM
from . import bot
from . import retriever
from . import template


def search(query, bot_name='baidu', lang='chinese', verbose=False, llm=OllamaLLM(model='llama3.1', temperature=0.3)):
    # Set the language template
    if lang == 'chinese':
        prompt_template = template.chinese
    else:
        prompt_template = template.english

    # Create the prompt
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Create the retriever
    search_bot = bot.make_bot(bot_name, verbose=verbose)  # Default to Baidu bot
    r = retriever.SearchBotRetriever(bot=search_bot)

    # Construct the RAG chain
    rag_chain = (
            {"context": r, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    # Invoke the RAG chain with the query
    answer = rag_chain.invoke(query)
    return answer
```

retriever.py

```python
from typing import Optional

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output

from . import bot as botmodule


class SearchBotRetriever(Runnable):
    def __init__(self, bot: botmodule.SearchBot):
        self.bot = bot

    def retrieve(self, query: str):
        return self.bot.search(query)

    def invoke(self, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        return self.retrieve(input)
```

template.py

```python
chinese = """
你是一个帮助用户完成信息检索的智能助理，你的职责是根据提供的上下文回答用户的问题。
此外，你还需要遵守下列约定：
1.如果你不知道问题的答案，直接说不知道
2.回答需要附上来源链接
上下文: {context} 
问题是: {question} 
"""

english = """
You are an AI assistant that helps users with information retrieval. 
Your job is to answer user questions based on the provided context.
Additionally, you are expected to follow these conventions:
1. If you don't know the answer to a question, say "I don't know"
2. Answers should include the source link

Context: {context}
Question: {question}
"""
```

## 使用示例

```python
from searchbot.rag import search

query = "法国的首都是哪里？"
bot_name = "bing"
lang = "chinese"
verbose = True

answer = search(query, bot_name=bot_name, lang=lang, verbose=verbose)
print(answer)
```

输出如下

```text
searched 9 results
retrieving content from 法国(法兰西共和国) - 百度百科
retrieving content from 法国的首都是什么?_百度教育
retrieving content from 法国的首都是哪里-爱问教育
retrieving content from 法国的首都是( )A.伦敦B.巴黎C.罗马D.柏林 题目和参考答案...
retrieving content from 法国“文化首都”竟不是巴黎?这9座城市“杀”疯了!|勒芒|...
retrieving content from 落地法国第一站戴高乐机场|看完这篇不迷路,最全攻略拿走吧
retrieving content from 法国最佳求学城市大盘点!巴黎竟然不是第一名 - 知乎
retrieving content from 波城大学——一所开放的大学!
retrieving content from 图文解读法国地理和历史(法国最全地图收藏) - 知乎
search completed, context length: 55657 characters
Generating...
法国的首都是巴黎。
```

## 开源地址

AI搜索机器人的源代码已在GitHub上开源，感兴趣的开发者可以访问以下地址获取完整代码和文档：

https://github.com/xialeistudio/SearchBot

## 结语

AI搜索机器人是一个结合了最新人工智能技术和搜索引擎能力的创新项目。它不仅提高了信息检索的效率和准确性，还为用户提供了更加智能和个性化的搜索体验。随着技术的不断发展，我们期待AI搜索机器人在未来能够发挥更大的作用，为信息检索领域带来新的变革。