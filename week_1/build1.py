import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=os.environ["OPENROUTER_API_KEY"],)

def call_model(prompt: str) -> str:
    # taking the input from user and performing the next sequence of work
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        messages=[{"role":"system","content":"Output your answer in a single sentense and keep it short."},
                {"role":"user","content":prompt}])
    print("Response Object")
    print(response)
    return response.choices[0].message.content

if __name__ == "__main__":
    response = call_model("Who is Virat Kohli and what is his role in RCB over the past few years?")
    print(response)
