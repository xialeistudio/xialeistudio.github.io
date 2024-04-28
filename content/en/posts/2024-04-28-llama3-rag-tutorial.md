---
title: Use RAG to build your private knowledge base based on llama3 and langchain!
slug: llama3-rag-tutorial
date: 2024-04-28T08:30:57+08:00
tags: 
- llama3
- rag
categories:
- ai
featured: true
---

LLM has timeliness and phantom problems, in [How to solve the problem of large model timeliness and accuracy with? the core principle of RAG technology](https://www.ddhigh.com/en/2024/04/24/retrieval-augmented-generation/) article I introduced the core principle of RAG, this article will share how to build a local private knowledge base based on llama3 and langchain.

<!--more-->

## Prerequisites.

+ Installation of ollama and llama3 models, see [Beyond GPT-3.5! Llama3 PC Local Deployment Tutorial](https://www.ddhigh.com/en/2024/04/24/beyond-gpt-3.5-llama3-personal-computer-local-deployment-tutorial./) 
+ Install python 3.9.
+ Install langchain for LLM coordination.
+ Install weaviate-client for vector databases

```bash
pip3 install langchain weaviate-client
```

## RAG in-action

The RAG needs to retrieve the context from the vector database and then input it into the LLM for generation, so it is necessary to vectorize the text data and store it into the vector database in advance. The main steps are as follows:

1. Prepare the text data
2. chunk the text
3. Embed and store the chunks into the vector database

Create a new python3 project and `index.py` file, import the required modules:

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
```

### Download & Load Data

President Biden's 2022 State of the Union address is used here as an example. Document link https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt. langchain provides several document loaders. Here we will just use `TextLoaders`.

```python
url = "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt"
res = requests.get(url)
with open("state_of_the_union.txt", "w") as f:
    f.write(res.text)

loader = TextLoader('./state_of_the_union.txt')
documents = loader.load()
```

### Chunking the corpus

Since the original document is too large for LLM's context window, it needs to be chunked in order to be recognized by LLM. LangChain provides a number of built-in text chunking tools, here we use `CharacterTextSplitter` as an example:

```python
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
```

### Embedding and storing into a vector database

In order to search the corpus in chunks, vectors need to be generated for each chunk and embedded in the documents, and finally the documents are stored along with the vectors. Here Ollama&llama3 is used to generate the vectors and store them to Weaviate vector database.

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

### Retrieve & Enhance

Once the vector database is loaded with data, it can be used as a retriever to fetch the data by semantic similarity between the user query and the embedded vector, and then just use a fixed chat template.

```python
retriever = vectorstore.as_retriever()
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

### Generate

Finally, the combination of the Retriever, the Chat Template, and the LLM into a RAG chain is all that is needed.

```python
llm = ChatOllama(model="llama3", temperature=10)
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

query = "What did the president mainly say?"
print(rag_chain.invoke(query))
```

In the example above I asked LLM what the president mainly said, and LLM answered as follows:

```
The president mainly talked about continuing efforts to combat COVID-19, including vaccination rates and measures to prepare for new variants. They also discussed investments in workers, communities, and law enforcement, with a focus on fairness and justice. The tone was hopeful and emphasized the importance of taking action to improve Americans' lives.
```

As you can see it's still like that, LLM used the input anticipation to reply with something about the new crown epidemic as well as work, community, etc.

> langchain supports a variety of LLMs, and readers who need it can try using the LLMs provided by OpenAI.

Readers can construct their own private knowledge retrieval bases by replacing the lower input anticipation as needed.

All the code in this paper is as follows:

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

url = "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt"
res = requests.get(url)
with open("state_of_the_union.txt", "w") as f:
    f.write(res.text)

loader = TextLoader('./state_of_the_union.txt')
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

client = weaviate.Client(
    embedded_options=EmbeddedOptions()
)
vectorstore = Weaviate.from_documents(
    client=client,
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3"),
    by_text=False
)

retriever = vectorstore.as_retriever()

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

query = "What did the president mainly say?"
print(rag_chain.invoke(query))
```