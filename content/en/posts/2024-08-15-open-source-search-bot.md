---
title: Build Your AI Search Bot with LLM and Search Engines
date: 2024-08-15T15:57:11+08:00
tags:
- rag
categories: 
- ai
featured: true
---
In the tide of artificial intelligence, the combination of large language models (LLMs) and search engines has brought revolutionary changes to the field of information retrieval. This article will provide a detailed introduction on how to use these technologies to build an intelligent information retrieval assistant—an AI search bot. We will delve into various aspects such as project background, core principles, code implementation, usage examples, and open-source addresses.

<!--more-->

## Project Background

With the explosive growth of information on the internet, it has become increasingly difficult for users to find answers in the vast sea of data. Although traditional search engines are powerful, they still have limitations in understanding and processing complex queries. To address this issue, the AI search bot project introduced in this article utilizes the deep semantic understanding of LLMs and the extensive information retrieval capabilities of search engines to provide users with a new solution for information retrieval.

## Core Principles

The core principles of the AI search bot can be summarized in the following steps:

1. **Search Engine Retrieval:** Use a search engine to retrieve relevant information and extract the top 10 web page contents.
2. **Content Extraction and Integration:** Extract useful information from the search results and integrate it.
3. **LLM Processing:** Input the integrated information into the LLM for in-depth analysis and understanding.
4. **Intelligent Answer Generation:** Generate intelligent answers based on the analysis results of the LLM.
5. **Result Feedback:** Provide intelligent answers to users along with the source link.

## Code Implementation

Below is the core code implementation of the AI search bot project, including key parts such as search engine integration, content extraction, LLM integration, and result generation.

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



def retrieve_content(item, verbose):
    url = item['url']
    title = item['title']
    try:
        if verbose:
            print(f"retrieving content from {title}")
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8' 
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        return f"{soup.get_text(strip=True)}\nOriginURL: {url}"
    except Exception as e:
        if verbose:
            print(f"failed to retrieve content from {title}: {e}")
        return ""

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

## Usage Example

```python
from searchbot.rag import search

query = "What is the capital of France?"
bot_name = "bing"
lang = "chinese"
verbose = True

answer = search(query, bot_name=bot_name, lang=lang, verbose=verbose)
print(answer)
```

Output

```text
# [Omitted for brevity]...
The capital of France is Paris.
```

## Open Source Address

The source code of the AI search bot is open-sourced on GitHub. Interested developers can visit the following address to obtain the complete code and documentation:

https://github.com/xialeistudio/SearchBot

## Conclusion

The AI search bot is an innovative project that combines the latest artificial intelligence technologies with the capabilities of search engines. It not only improves the efficiency and accuracy of information retrieval but also provides users with a more intelligent and personalized search experience. As technology continues to develop, we look forward to the AI search bot playing a greater role in the future, bringing new changes to the field of information retrieval.