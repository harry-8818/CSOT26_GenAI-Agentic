"""
Build 2: Tool Calling with the OpenAI SDK
==========================================
Build 1 had you implement the tool-call round-trip by hand using a custom text format.
This build does the same thing the production way: using the OpenAI SDK's native
`tools` parameter, `tool_calls` response field, and `"role": "tool"` messages.

The mechanics are identical. You're still parsing a tool name, running a function,
and sending the result back. The difference is that the SDK handles the encoding
and the model is trained to produce structured JSON tool calls rather than freeform XML.

Implement the same two tools as Build 1:
  - get_weather(city: str) -> dict
  - calculate(expression: str) -> dict

Then complete the agent loop and watch the pattern become clean.

Stretch goals (not required):
  - Add a third tool: get_time(timezone: str) -> dict
  - Handle multiple tool_calls in a single response (the model can call several at once)
  - Add a token counter that prints total tokens used after the loop ends
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=os.environ["OPENROUTER_API_KEY"],)
model = "openrouter/free"
system_prompt = "You are a helpful agent with a polite tone. You can use any tool and as much tools you want to use"
tools_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Returns the current weather for a given city. "
                "Call this whenever the user asks about weather, temperature, or climate. "
                "Do not guess weather. Always call this tool."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. 'Delhi' or 'San Francisco'",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit. Default to celsius.",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Evaluates a mathematical expression and returns the result. "
                "Use this for any arithmetic the user asks about. "
                "Pass the expression as a string, e.g. '1337 * 42 + 7'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A Python arithmetic expression, e.g. '100 / 4 + 3'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

def get_weather(city: str, unit: str = "celsius") -> dict:
    data = {"delhi": {"temp":42,"condition":"Sunny"},"mumbai": {"temp":22,"condition":"Rainy"},"kanpur": {"temp":30,"condition":"Cloudy"}}
    city_lower = city.lower()
    if city_lower in data:
        return {"city":city,"weather":data[city_lower],"unit": unit}
    return {"city":city,"weather":"unknown"}


def calculate(expression: str) -> dict:
    try:
        result = eval(expression,{"__builtins__":None},{})
        return {"expression":expression,"result":result}
    except Exception as e:
        return {"error": f"I am not able to calculate beacause: {str(e)}"}

tools_available = {"get_weather":get_weather,"calculate":calculate}

def dispatch(tool_call) -> str:
    name = tool_call.function.name
    arguments = tool_call.function.arguments
    
    if name not in tools_available:
        return json.dumps({"error": f"Unknown tool: {name}"})
        
    try:
        arguments = json.loads(arguments)
        function = tools_available[name]
        result = function(**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})
    
max_calls = 8

def run_agent(user_message: str) -> str:
    messages = [{"role": "system", "content": "You are a helpful assistant. Use tools when appropriate."},{"role": "user", "content": user_message}]
    for _ in range(max_calls):
        response = client.chat.completions.create(model=model,messages=messages,tools=tools_schemas)
        message = response.choices[0].message
        messages.append(message)
        finish_reason = response.choices[0].finish_reason
        if ( finish_reason == "tool_calls"):
            for tool_call in message.tool_calls:
                print(f" -> [Agent] Executing tool: {tool_call.function.name}")
                result = dispatch(tool_call)
                messages.append({"role":"tool","tool_call_id":tool_call.id,"content":result})
        elif (finish_reason == "stop"):
            return message.content
        else:
            return message.content
    return f"[AGENT] stopped after {max_calls} calls without providing a final answer"    

if __name__ == "__main__":
    test_queries = [
        "What's the weather in Delhi?",
        "Calculate: (2**10) - 1",
        "Compare the weather in London and Delhi, and tell me what 451 * 3 is.",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        result = run_agent(query)
        print(f"\nAnswer:\n{result}")