import os
import uuid
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.files import list_files,read_file,write_file,edit_file,file_tools_schema
from tools.web import web_search,web_fetch,web_tools_schema
from tools.papers import paper_search,read_paper,papers_tools_schema

full_toolset = file_tools_schema + web_tools_schema + papers_tools_schema
class Agent:
    def __init__(self,session_id=None,on_tool_event=None):
        load_dotenv()
        self.on_tool_event = on_tool_event
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=os.environ.get("OPENROUTER_API_KEY"))
        os.makedirs(".agent/sessions",exist_ok=True)

        system_prompt = "You are a helpful research assistant."
        if (os.path.exists("AGENTS.md")) :
            with open("AGENTS.md","r") as f :
                agent_rules = f.read()
                self.system_prompt = system_prompt + '\n\n' + agent_rules
        else :
            self.system_prompt = system_prompt

        if (session_id) :
            loaded_messages = self.load_session(session_id)
            if (loaded_messages) :
                self.messages = loaded_messages
                self.session_id = session_id
            else :
                print("\nFailed to load the session requested.")
                exit()
        else :
            self.session_id = str(uuid.uuid4())
            self.messages = [{"role":"system","content":self.system_prompt}]  

    def log_tool(self,text):
        if self.on_tool_event:
            self.on_tool_event(text)
        else:
            print(text)     

    def save_session(self):
        path = f".agent/sessions/{self.session_id}.json"
        with open(path,"w",encoding="utf-8") as f :
            json.dump(self.messages,f,indent=8)

    def load_session(self,session_id):
        path = f".agent/sessions/{session_id}.json"
        if (os.path.exists(path)) :
            with open(path,"r",encoding="utf-8") as f :
                return json.load(f)
        else :
            return None

    def turn(self,user_input):
        self.messages.append({"role":"user","content":user_input})
        for _ in range(10):
            response = self.client.chat.completions.create(model="openrouter/free",messages=self.messages,tools=full_toolset)
            message = response.choices[0].message
            if message.tool_calls:
                self.messages.append(message.model_dump())
                for tool_call in message.tool_calls : 
                    name = tool_call.function.name
                    try :
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError :
                        arguments = {}    
                    tool_result = "" 
                    if name == "list_files" :
                        self.log_tool(f"\n[SYSTEM]: Agent is looking at your files in: {arguments.get('directory', '.')}")
                        tool_result = list_files(directory=arguments.get("directory","."))
                    elif name == "read_file":
                        self.log_tool(f"\n[SYSTEM]: Agent is reading file: {arguments.get('file_path')}")
                        tool_result = read_file(file_path=arguments.get("file_path"))
                    elif name == "write_file":
                        self.log_tool(f"\n[SYSTEM]: Agent is writing to file: {arguments.get('file_path')}")
                        tool_result = write_file(file_path=arguments.get("file_path"),content=arguments.get("content"))
                    elif name == "edit_file":
                        self.log_tool(f"\n[SYSTEM]: Agent is editing the file: {arguments.get('file_path')}")
                        tool_result = edit_file(file_path=arguments.get("file_path"),old_content=arguments.get("old_content"),new_content=arguments.get("new_content"))    
                    elif name == "web_search" :
                        self.log_tool(f"\n[SYSTEM]: Agent is searching the web for: {arguments.get('search_text')}")
                        tool_result = web_search(search_text=arguments.get("search_text"))
                    elif name == "web_fetch" :
                        self.log_tool(f"\n[SYSTEM]: Agent is reading webpage: {arguments.get('web_link')}")
                        tool_result = web_fetch(web_link=arguments.get("web_link"))
                    elif name == "paper_search":
                        self.log_tool(f"\n[SYSTEM]: Agent is querying arXiv for: {arguments.get('search_text')}")
                        tool_result = paper_search(search_text=arguments.get("search_text"))
                    elif name == "read_paper":
                        self.log_tool(f"\n[SYSTEM]: Agent is fetching details for paper ID: {arguments.get('paper_id')}")
                        tool_result = read_paper(paper_id=arguments.get("paper_id"))
                    else:
                        tool_result = f"[ERROR]: Tool {name} not found."
                    self.messages.append({"role": "tool","tool_call_id": tool_call.id,"content": str(tool_result)})
            else :
                bot_output = message.content    
                self.messages.append({"role":"assistant","content":bot_output})
                self.save_session()
                return bot_output
        return "[ERROR]: Stopped after too many tool steps without a final answer."

class REPLAgent:
    def __init__(self):
        user_choice = input("Enter 1 for a new session or 2 to resume an old session: ")
        if (user_choice=='2') :
            session_id = input("Enter the session ID: ")
            self.agent = Agent(session_id=session_id)
            print(f"Resuming session: {self.agent.session_id}")  
        else :
            self.agent = Agent()
            print(f"Started new session: {self.agent.session_id}")    
    def chat(self):
        while True:
            user_input = input("\n[YOU]: ")
            if (user_input in ('exit','quit')):
                print("Thks for chatting. Enjoy your rest of day. Goodbye!!")
                break                    
            bot_output = self.agent.turn(user_input)
            print(f"\n[AGENT]: {bot_output}")

def main():
    REPL = REPLAgent()
    REPL.chat()

if __name__ == "__main__" :
    main()        