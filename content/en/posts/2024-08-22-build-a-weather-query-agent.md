---
title: Build a weather query agent
date: 2024-08-22T11:53:08+08:00
slug: build-a-weather-query-agent
categories: 
- ai
featured: true
---
In the field of artificial intelligence, intelligent agents (Agent) are one of the cutting-edge applications of Large Language Models (LLM). They are not only capable of performing specific tasks but also able to provide services or execute tasks through interactions with users or other systems. The core advantages of intelligent agents lie in their autonomy and interactivity, enabling them to perform tasks without human intervention while understanding and responding to user commands and needs.

Following the previous discussion on the basic concepts and application potential of intelligent agents, this article will share how to build a locally running weather query intelligent agent based on Ollama and langchain, to query the weather conditions of target locations in real-time.

## Installing Ollama

The installation steps for Ollama can be referred to in previous articles. Currently, the latest open-sourced llama model version by Meta is 3.1, and the installation command is as follows:

```bash
ollama pull llama3.1
```

## Applying for a Weather API

This article uses the QWeather API. The steps to apply for the weather API are as follows.

1. Log in to the QWeather Developer Console https://console.qweather.com/.

2. Create a project and obtain an API KEY.

   ![WX20240822-111632](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/WX20240822-111632.png)

3. Copy the API KEY for later use.

   ![WX20240822-111658](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/WX20240822-111658.png)

4. The QWeather API documentation address is: https://dev.qweather.com/docs/api/weather/weather-now/. This article uses Postman to test the interface, taking Beijing's address code as an example, successfully obtaining the weather conditions and update time.

   ![WX20240822-111732@2x](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/WX20240822-111732%402x.png)

## Building the Agent

Create a new Python project and install the following dependencies:

```
bash复制
pip install requests langchain langchain_core langchain_ollama langgraph
```

### Building the Weather Query Tool

By inheriting the `BaseTool` class provided by langchain, you can quickly develop custom tools. The following is a code example of the weather query tool:

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
           url = f"https://devapi.qweather.com/v7/weather/now?key=YOUR KEY&location={location_id}"
           response = requests.get(url)
           data = response.json()
           if data["code"] != "200":
               raise ValueError(f"Failed to query weather data for location {location}")
           return json.dumps(data["now"])
   ```

  It should be noted that `description` is crucial. Through `description`, LLM can understand what the current tool can accomplish. It is recommended to use the following template to write `description`:

   ```
   use this tool when you need to PUT YOUR TASK HERE
   ```

## Initializing Agent Components

An intelligent agent mainly consists of three components: LLM, Memory, and Tool. The following is the code to initialize these components:

```python
# Initialize LLM
llm = ChatOllama(temperature=0, model='llama3.1')
# Initialize Agent
memory = MemorySaver()
tools = [WeatherTool()]
agent_executor = create_react_agent(llm, tools, checkpointer=memory)
```

## Running the Agent

When running the intelligent agent, provide a task ID parameter so that LLM can remember the context. The following is the code to run the intelligent agent:

```python
config = {"configurable": {"thread_id": "abc2"}}
results = agent_executor.invoke(
    {"messages": [
        SystemMessage(
            content="You are a helpful assistant! "
        ),
        HumanMessage(
            content="Tell me the weather in beijing"
        ),
    ]},
    config=config
)

print(results)
```

The execution result is as follows:

```json
{
  "messages": [
    {
      "type": "SystemMessage",
      "content": "You are a helpful assistant!",
      "id": "b68b933f-e6f8-4b6d-a2fb-f9f6fb6487d1"
    },
    {
      "type": "HumanMessage",
      "content": "Tell me the weather in beijing",
      "id": "d46cc9c8-8d20-46a4-a285-4bb75ef30694"
    },
    {
      "type": "AIMessage",
      "content": "",
      "response_metadata": {
        "model": "llama3.1",
        "created_at": "2024-08-22T04:32:18.667703Z",
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
        "total_duration": 10619205875,
        "load_duration": 9403068584,
        "prompt_eval_count": 164,
        "prompt_eval_duration": 683355000,
        "eval_count": 18,
        "eval_duration": 526748000
      },
      "id": "run-0e1857a1-6385-411c-93e2-aa8b512fb1e2-0",
      "tool_calls": [
        {
          "name": "Weather tool",
          "args": {
            "location": "beijing"
          },
          "id": "73850eaf-4258-46f3-8374-934ea6cb3938",
          "type": "tool_call"
        }
      ],
      "usage_metadata": {
        "input_tokens": 164,
        "output_tokens": 18,
        "total_tokens": 182
      }
    },
    {
      "type": "ToolMessage",
      "content": "{\"obsTime\": \"2024-08-22T12:24+08:00\", \"temp\": \"33\", \"feelsLike\": \"34\", \"icon\": \"100\", \"text\": \"晴\", \"wind360\": \"45\", \"windDir\": \"东北风\", \"windScale\": \"2\", \"windSpeed\": \"11\", \"humidity\": \"45\", \"precip\": \"0.0\", \"pressure\": \"999\", \"vis\": \"30\", \"cloud\": \"6\", \"dew\": \"21\"}",
      "name": "Weather tool",
      "id": "6f42c4df-6b12-43d2-bdb3-e63e73829997",
      "tool_call_id": "73850eaf-4258-46f3-8374-934ea6cb3938"
    },
    {
      "type": "AIMessage",
      "content": "The current weather in Beijing is:\n\nTemperature: 33°C\nFeels like: 34°C\nHumidity: 45%\nWind direction: Northeast (45°)\nWind speed: 11 km/h\nPrecipitation: 0.0 mm\nAtmospheric pressure: 999 hPa\nVisibility: 30 km\nCloud cover: 6/10\n\nNote: The weather conditions are based on the output of the 'Weather tool' and may not reflect the actual current weather in Beijing.",
      "response_metadata": {
        "model": "llama3.1",
        "created_at": "2024-08-22T04:32:22.957491Z",
        "message": {
          "role": "assistant",
          "content": "The current weather in Beijing is:\n\nTemperature: 33°C\nFeels like: 34°C\nHumidity: 45%\nWind direction: Northeast (45°)\nWind speed: 11 km/h\nPrecipitation: 0.0 mm\nAtmospheric pressure: 999 hPa\nVisibility: 30 km\nCloud cover: 6/10\n\nNote: The weather conditions are based on the output of the 'Weather tool' and may not reflect the actual current weather in Beijing."
        },
        "done_reason": "stop",
        "done": true,
        "total_duration": 4024144416,
        "load_duration": 36296958,
        "prompt_eval_count": 212,
        "prompt_eval_duration": 672784000,
        "eval_count": 103,
        "eval_duration": 3307060000
      },
      "id": "run-9ac727c3-812a-43e3-8ca7-8d5dd109ccad-0",
      "usage_metadata": {
        "input_tokens": 212,
        "output_tokens": 103,
        "total_tokens": 315
      }
    }
  ]
}
```

The agent successfully used the tool we developed to query the QWeather API and constructed a response that conforms to the rules of natural language based on the output. Newbee!

In general, we can simply use the `content` of the last message as the output. It is important to note that the `messages` list must contain the key `tool_calls` to indicate that our tool has been truly invoked; otherwise, it may be the LLM fabricating the information.

## Full Code

```python
import json
import requests
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

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
        url = f"https://devapi.qweather.com/v7/weather/now?key=776ba7b3a49345808cd4b41ac9eb2714&location={location_id}"
        response = requests.get(url)
        data = response.json()
        if data["code"] != "200":
            raise ValueError(f"Failed to query weather data for location {location}")
        return json.dumps(data["now"])



llm = ChatOllama(temperature=0,model='llama3.1')

memory = MemorySaver()
tools = [WeatherTool()]
agent_executor = create_react_agent(llm, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "abc2"}}

results = agent_executor.invoke(
    {"messages": [
        SystemMessage(
            content="You are a helpful assistant! "
        ),
        HumanMessage(
            content="Tell me the weather in beijing"
        ),
    ]},
    config=config
)

print(results)

```

## Conclusion

Through the introduction in this article, we have successfully constructed an intelligent agent capable of real-time weather inquiries. This intelligent agent not only demonstrates the powerful capabilities of LLM but also reflects the potential of intelligent agents in practical applications. In the future, intelligent agents will play a unique role in more fields, providing users with more convenient and intelligent services.
