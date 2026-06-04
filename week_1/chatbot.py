import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
class ChatAgent:
    def __init__(self,model,system_prompt,max_calls = 8):
        self.model = model
        self.max_calls = max_calls
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=os.environ["OPENROUTER_API_KEY"],)
        self.messages = [{"role":"system","content":system_prompt}]

    def call_model(self):
        try:
            api_call = self.client.chat.completions.create(model=self.model,messages=self.messages)
            return api_call.choices[0].message.content
        except Exception as e:
            return None
        
    def trim_history(self):
        if (len(self.messages)-1>2*self.max_calls):
            self.messages = [self.messages[0]]+self.messages[-2*self.max_calls:] 

    def chat(self):
        print("Chat started. Type 'exit' or 'quit' to leave .")
        print("To reset the chat enter '/reset'.")
        while True:
            user_input = input("[YOU] ")
            if( user_input.strip().lower() in("exit","quit")):
                print("Good Bye!")
                break
            elif (user_input == '/reset'):
                self.messages = [self.messages[0]]
                print("History Cleared")
                continue
            self.messages.append({"role":"user","content":user_input})
            bot_output = self.call_model()
            if bot_output is None:
                print("Model is unavailable or not working now. Try again later or choose another model")
                self.messages.pop()
                continue
            self.messages.append({"role":"assistant","content":bot_output})
            self.trim_history()
            print("[Bot]",bot_output)
    
if __name__ == "__main__":

    available_models=["google/gemma-4-26b-a4b-it:free","nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free","openai/gpt-oss-120b:free","liquid/lfm-2.5-1.2b-thinking:free"]
    print("Chose a model from below and type the number corresponding to it")
    for i,model in enumerate(available_models):
        print(f"{i+1} : {model}")
    user_choice = input("Enter your chosen number : ")
    agent = ChatAgent(available_models[int(user_choice)-1],"Keep your tone polite and provide you answers in a structural way but also keep them short")
    agent.chat()
