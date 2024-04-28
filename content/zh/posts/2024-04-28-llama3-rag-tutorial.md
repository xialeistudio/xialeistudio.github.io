---
title: 基于llama3和langchain使用RAG搭建你的私有知识库！
slug: llama3-rag-tutorial
date: 2024-04-28T08:30:57+08:00
tags: 
- llama3
- rag
categories:
- ai
featured: true
---

LLM存在时效性和幻觉问题，在 [如何用解决大模型时效性和准确性问题？RAG技术核心原理](https://www.ddhigh.com/2024/04/24/retrieval-augmented-generation/) 一文中我介绍了RAG的核心原理，本文将分享如何基于llama3和langchain搭建本地私有知识库。

<!--more-->

## 先决条件

+ 安装ollama和llama3模型，参看 [超越GPT-3.5!Llama3个人电脑本地部署教程](https://www.ddhigh.com/2024/04/20/%E8%B6%85%E8%B6%8Agpt-3.5llama3%E4%B8%AA%E4%BA%BA%E7%94%B5%E8%84%91%E6%9C%AC%E5%9C%B0%E9%83%A8%E7%BD%B2%E6%95%99%E7%A8%8B/)
+ 安装python3.9
+ 安装langchain用于协调LLM
+ 安装weaviate-client用于向量数据库

```bash
pip3 install langchain weaviate-client
```

## RAG实践

RAG需要从向量数据库检索上下文然后输入LLM进行生成，因此需要提前将文本数据向量化并存储到向量数据库。主要步骤如下：

1. 准备文本资料
2. 将文本分块
3. 嵌入以及存储块到向量数据库

新建一个python3项目以及`index.py`文件，导入需要用到的模块：

```python
from langchain_community.document_loaders import TextLoader # 文本加载器
from langchain.text_splitter import CharacterTextSplitter # 文本分块器
from langchain_community.embeddings import OllamaEmbeddings # Ollama向量嵌入器
import weaviate # 向量数据库
from weaviate.embedded import EmbeddedOptions # 向量嵌入选项
from langchain.prompts import ChatPromptTemplate # 聊天提示模板
from langchain_community.chat_models import ChatOllama # ChatOllma聊天模型
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser # 输出解析器
from langchain_community.vectorstores import Weaviate # 向量数据库
import requests
```

### 下载&加载语料

这里使用拜登总统2022年的国情咨文作为示例。文件链接https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt。langchain提供了多个文档加载器，这里我们使用`TextLoaders`即可。

```python
# 下载文件
url = "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt"
res = requests.get(url)
with open("state_of_the_union.txt", "w") as f:
    f.write(res.text)
# 加载文件
loader = TextLoader('./state_of_the_union.txt')
documents = loader.load()
```

### 语料分块

由于原始文档过大，超出了LLM的上下文窗口，需要将其分块才能让LLM识别。LangChain 提供了许多内置的文本分块工具，这里用`CharacterTextSplitter`作为示例：

```python
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
```

### 嵌入以及存储到向量数据库

为了对语料分块进行搜索，需要为每个块生成向量并嵌入文档，最后将文档和向量一起存储。这里使用Ollama&llama3生成向量，并存储到Weaviate向量数据库。

```python
client = weaviate.Client(
    embedded_options=EmbeddedOptions()
)
print("store vector")
vectorstore = Weaviate.from_documents(
    client=client,
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3"),
    by_text=False
)
```

### 检索 & 增强

向量数据库加载数据后，可以作为检索器，通过用户查询和嵌入向量之间的语义相似性获取数据，然后使用一个固定的聊天模板即可。

```python
# 检索器
retriever = vectorstore.as_retriever()
# LLM提示模板
template = """You are an assistant for question-answering tasks. 
   Use the following pieces of retrieved context to answer the question. 
   If you don't know the answer, just say that you don't know. 
   Use three sentences maximum and keep the answer concise.
   Question: {question} 
   Context: {context} 
   Answer:
   """
prompt = ChatPromptTemplate.from_template(template)
```

### 生成

最后，将检索器、聊天模板以及LLM组合成RAG链就可以了。

```python
llm = ChatOllama(model="llama3", temperature=10)
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} # 上下文信息
        | prompt
        | llm
        | StrOutputParser()
)
# 开始查询&生成
query = "What did the president mainly say?"
print(rag_chain.invoke(query))
```

上面的示例中我问了LLM总统主要说了什么，LLM回答如下：

```
The president mainly talked about continuing efforts to combat COVID-19, including vaccination rates and measures to prepare for new variants. They also discussed investments in workers, communities, and law enforcement, with a focus on fairness and justice. The tone was hopeful and emphasized the importance of taking action to improve Americans' lives.
```

可以看到还是像那么回事的，LLM使用的输入预料的内容答复了一些关于新冠疫情以及工作、社区等内容。

> langchain支持多种LLM，有需要的读者可以尝试下使用OpenAI提供的LLM。

读者可以根据需要替换下输入预料，构造自己的私有知识检索库。

本文所有代码如下：

```python
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
import weaviate
from weaviate.embedded import EmbeddedOptions
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import Weaviate
import requests
# 下载数据
url = "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt"
res = requests.get(url)
with open("state_of_the_union.txt", "w") as f:
    f.write(res.text)
# 加载数据
loader = TextLoader('./state_of_the_union.txt')
documents = loader.load()
# 文本分块
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
# 初始化向量数据库并嵌入目标文档
client = weaviate.Client(
    embedded_options=EmbeddedOptions()
)
vectorstore = Weaviate.from_documents(
    client=client,
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3"),
    by_text=False
)
# 检索器
retriever = vectorstore.as_retriever()
# LLM提示模板
template = """You are an assistant for question-answering tasks. 
   Use the following pieces of retrieved context to answer the question. 
   If you don't know the answer, just say that you don't know. 
   Use three sentences maximum and keep the answer concise.
   Question: {question} 
   Context: {context} 
   Answer:
   """
prompt = ChatPromptTemplate.from_template(template)
llm = ChatOllama(model="llama3", temperature=10)
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)
# 开始查询&生成
query = "What did the president mainly say?"
print(rag_chain.invoke(query))
```