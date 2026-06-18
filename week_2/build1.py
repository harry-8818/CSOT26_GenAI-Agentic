import os
import re
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=os.environ["OPENROUTER_API_KEY"],)
model = "openrouter/free"
system_prompt = """You are a helpful file assistant with access to the following tools:

- read_file(path: str): reads a file from disk and returns its content
- write_file(path: str, content: str): writes content to a file on disk

When you need to use a tool, emit EXACTLY this format and nothing else after it:

<tool_call>
{"name": "TOOL_NAME", "arguments": {"arg1": "value1"}}
</tool_call>

After you receive the tool result in a <tool_response> block, continue your response
normally. Do not emit a tool_call and prose in the same turn. Pick one or the other.
"""
def read_file(path: str) -> dict:
    try:
        with open(path,'r',encoding="utf-8") as f:
            return {"content":f.read(),"path":path}
    except Exception as e:
        return{"error":str(e)}
def write_file(path: str, content: str) -> dict:
    try:
        with open(path,'w',encoding="utf-8") as f:
            bytes_written = f.write(content)
        return {"success": True,"path":path,"bytes_written": bytes_written}
    except Exception as e:
        return {"error":str(e)}    


def parse_tool_call(response_text: str) -> dict | None:
    to_find = r"<tool_call>(.*?)</tool_call>"
    match = re.search(to_find,response_text,re.DOTALL)
    if match:
        json_body = match.group(1).strip()
        try:
            return json.loads(json_body)
        except Exception as e:
            return {"error":str(e)}
    return None    
def strip_tool_call(response_text: str) -> str:
    to_find = r"<tool_call>(.*?)</tool_call>"
    return re.sub(to_find,"",response_text,flags=re.DOTALL).strip()

tools_available = {"read_file": read_file,"write_file": write_file,}
def dispatch(name: str, arguments: dict) -> str:
    if name not in tools_available:
        return json.dumps({"error":f"Unknown Tool : {name}"})
    try :
        tool = tools_available[name]
        result = tool(**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error":str(e)})


max_calls = 6
def run_agent(user_message: str) -> str:
    messages = [{"role": "system", "content": system_prompt},{"role": "user", "content": user_message},]
    for i in range(max_calls):
        response = client.chat.completions.create(model=model,messages=messages)
        text_response = response.choices[0].message.content
        messages.append({"role":"assistant","content":text_response})
        tool_call = parse_tool_call(text_response)
        if tool_call:
            name = tool_call.get("name")
            arguements = tool_call.get("arguments",{})
            print(f"[Agent] Iteration {i} : Calling:'{name}'", file=sys.stderr)
            tool_text_response = dispatch(name,arguements)
            formatted_response = f"<tool_response>\n{tool_text_response}\n</tool_response>"
            messages.append({"role": "user", "content": formatted_response})
        else:
            return strip_tool_call(text_response)    
    return f"[Agent stopped after {max_calls} iterations]"

if __name__ == "__main__":
    with open("sample.txt", "w") as f:
        f.write("IIT Delhi was established in 1961. It is one of the premier engineering institutions in India.\n")
        f.write("The campus spans 325 acres in Hauz Khas, New Delhi.\n")

    test_queries = ["Read sample.txt and summarise what it says.","Read sample.txt and write a one-sentence version of its content to summary.txt.",]
    for query in test_queries:
        print(f"Query: {query}")
        result = run_agent(query)
        print(f"Answer: {result}")