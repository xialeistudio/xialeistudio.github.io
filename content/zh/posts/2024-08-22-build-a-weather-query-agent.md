---
title: 构建一个天气查询Agent
date: 2024-08-22T11:53:08+08:00
slug: build-a-weather-query-agent
categories: 
- ai
featured: true
---
在人工智能领域，智能代理（Agent）是大型语言模型（LLM）应用的前沿之一，它不仅能够执行特定任务，还能通过与用户或其他系统的交互来提供服务或执行任务。智能代理的核心优势在于其自主性和交互性，能够在无需人工干预的情况下执行任务，同时理解和响应用户的指令和需求。

继之前探讨智能代理的基本概念及其应用潜力之后，本文将分享如何基于Ollama以及langchain构建一个本地运行的天气查询智能代理，以实时查询目标地点的天气情况。
<!--more-->

## 安装Ollama

Ollama的安装步骤可参考之前的文章。目前，Meta最新开源的llama模型版本为3.1，安装命令如下：

```bash
ollama pull llama3.1
```

## 申请天气API

本文采用和风天气API，申请天气API的步骤如下。

1. 登录和风天气开发者控制台 https://console.qweather.com/。

2. 创建项目并获取API KEY。

   ![WX20240822-111632](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/WX20240822-111632.png)

3. 将API KEY拷贝备用。

   ![WX20240822-111658](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/WX20240822-111658.png)

4. 和风天气API文档地址：https://dev.qweather.com/docs/api/weather/weather-now/。本文使用Postman测试接口，以北京的地址代码为例，成功获取到天气情况及更新时间。

   ![WX20240822-111732@2x](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/WX20240822-111732%402x.png)

## 构建Agent

新建一个Python项目，并安装以下依赖：

   ```bash
   pip install requests langchain langchain_core langchain_ollama langgraph
   ```

### 构建天气查询工具

通过继承langchain提供的`BaseTool`类，可以快速开发自定义工具。以下是天气查询工具的代码示例：

   ```python
   class WeatherTool(BaseTool):
       name = "Weather tool"
       description = "use this tool when you need to query the weather of a city"
   
       def _run(self, location: str) -> str:
           database = {
               'beijing': 101010100
           }
   
           if location not in database:
               raise ValueError(f"Location {location} not found in the database")
           location_id = database[location]
           # 请求天气API
           url = f"https://devapi.qweather.com/v7/weather/now?key=替换和风天气KEY&location={location_id}"
           response = requests.get(url)
           data = response.json()
           # 解析响应
           if data["code"] != "200":
               raise ValueError(f"Failed to query weather data for location {location}")
           return json.dumps(data["now"])
   ```

   需要注意的是`description`是关键所在，通过`description`，LLM能知道当前工具能完成什么工作，建议使用以下模板来编写`description`

   ```
   use this tool when you need to 需要完成的工作
   ```

## 初始化智能代理组件

智能代理主要由LLM、Memory、Tool三大组件构成。以下是初始化这些组件的代码：

```python
# 初始化LLM
llm = ChatOllama(temperature=0,model='llama3.1')
# 初始化Agent
memory = MemorySaver()
tools = [WeatherTool()]
agent_executor = create_react_agent(llm, tools, checkpointer=memory)
```

## 运行Agent

运行智能代理时，提供一个任务ID参数，以便LLM记住上下文。以下是运行智能代理的代码：

```python
config = {"configurable": {"thread_id": "abc2"}}
# 向agent发送指令
results = agent_executor.invoke(
    {"messages": [
        SystemMessage(
            content="You are a helpful assistant! You must use Chinese to reply user's question."
        ),
        HumanMessage(
            content="Tell me the weather in beijing"
        ),
    ]},
    config=config
)

print(results)
```

执行结果输出如下：

```json
{
  "messages": [
    {
      "type": "SystemMessage",
      "content": "You are a helpful assistant! You must use Chinese to reply user's question.",
      "id": "2a4ca92d-8e12-484e-aad6-114e52ddd58c"
    },
    {
      "type": "HumanMessage",
      "content": "Tell me the weather in beijing",
      "id": "65c97f06-be90-4c35-8e80-00e9ea8cb60f"
    },
    {
      "type": "AIMessage",
      "content": "",
      "response_metadata": {
        "model": "llama3.1",
        "created_at": "2024-08-22T03:39:13.038247Z",
        "message": {
          "role": "assistant",
          "content": "",
          "tool_calls": [
            {
              "function": {
                "name": "Weather tool",
                "arguments": {
                  "location": "beijing"
                }
              }
            }
          ]
        },
        "done_reason": "stop",
        "done": true,
        "total_duration": 3440772541,
        "load_duration": 35426416,
        "prompt_eval_count": 173,
        "prompt_eval_duration": 2318558000,
        "eval_count": 18,
        "eval_duration": 1082738000
      },
      "id": "run-af855081-402d-4c55-ac65-873686832300-0",
      "tool_calls": [
        {
          "name": "Weather tool",
          "args": {
            "location": "beijing"
          },
          "id": "49c63454-7cd3-4c4e-a210-a034a6d98f78",
          "type": "tool_call"
        }
      ],
      "usage_metadata": {
        "input_tokens": 173,
        "output_tokens": 18,
        "total_tokens": 191
      }
    },
    {
      "type": "ToolMessage",
      "content": "{\"obsTime\": \"2024-08-22T11:33+08:00\", \"temp\": \"32\", \"feelsLike\": \"34\", \"icon\": \"100\", \"text\": \"晴\", \"wind360\": \"0\", \"windDir\": \"北风\", \"windScale\": \"2\", \"windSpeed\": \"9\", \"humidity\": \"48\", \"precip\": \"0.0\", \"pressure\": \"999\", \"vis\": \"30\", \"cloud\": \"8\", \"dew\": \"21\"}",
      "name": "Weather tool",
      "id": "cdffe5eb-7005-45f4-9fd7-b59b5e595d1c",
      "tool_call_id": "49c63454-7cd3-4c4e-a210-a034a6d98f78"
    },
    {
      "type": "AIMessage",
      "content": "根据天气工具的输出，北京当前的天气状况是：\n\n温度：32摄氏度\n感温：34摄氏度\n风向：东北风（0度）\n风力：2级\n相对湿度：48%\n降水量：0.0毫米\n气压：999海帕\n视程：30公里\n云量：8层\n\n因此，北京的天气状况是晴朗且炎热。",
      "response_metadata": {
        "model": "llama3.1",
        "created_at": "2024-08-22T03:39:17.061073Z",
        "message": {
          "role": "assistant",
          "content": "根据天气工具的输出，北京当前的天气状况是：\n\n温度：32摄氏度\n感温：34摄氏度\n风向：东北风（0度）\n风力：2级\n相对湿度：48%\n降水量：0.0毫米\n气压：999海帕\n视程：30公里\n云量：8层\n\n因此，北京的天气状况是晴朗且炎热。"
        }
      },
      "id": "run-7d21a1b2-ba42-49b1-b0e1-48ff0a412978-0",
      "usage_metadata": {
        "input_tokens": 216,
        "output_tokens": 97,
        "total_tokens": 313
      }
    }
  ]
}
```

Agent成功使用我们编写的Tool查询了和风天气API，并基于输出构造了一段符合自然语言规则的响应。Newbee!

一般情况下，我们采用最后一条消息的`content`作为输出即可，需要特别注意，`messages`列表中必须包含`tool_calls`这个key，才是真正调用了我们编写的Tool，否则可能是LLM在编造信息。

## 本文完整代码

```python
import json
import requests
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


# 天气查询Tool
class WeatherTool(BaseTool):
    name = "Weather tool"
    description = "use this tool when you need to query the weather of a city"

    def _run(self, location: str) -> str:
        database = {
            'beijing': 101010100
        }

        if location not in database:
            raise ValueError(f"Location {location} not found in the database")
        location_id = database[location]
        # 请求天气API
        url = f"https://devapi.qweather.com/v7/weather/now?key=和风天气KEY&location={location_id}"
        response = requests.get(url)
        data = response.json()
        # 解析响应
        if data["code"] != "200":
            raise ValueError(f"Failed to query weather data for location {location}")
        return json.dumps(data["now"])


# 初始化LLM
llm = ChatOllama(temperature=0,model='llama3.1')
# 初始化Agent
memory = MemorySaver()
tools = [WeatherTool()]
agent_executor = create_react_agent(llm, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "abc2"}}
# 向agent发送指令
results = agent_executor.invoke(
    {"messages": [
        SystemMessage(
            content="You are a helpful assistant! You must use Chinese to reply user's question."
        ),
        HumanMessage(
            content="Tell me the weather in beijing"
        ),
    ]},
    config=config
)

print(results)
```

## 结论

通过本文的介绍，我们成功构建了一个能够实时查询天气情况的智能代理。这个智能代理不仅展示了LLM的强大能力，也体现了智能代理在实际应用中的潜力。未来，智能代理将在更多领域发挥其独特的作用，为用户提供更加便捷和智能的服务。
