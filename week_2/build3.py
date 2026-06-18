"""
Build 3: Extend Your Week 1 Chatbot into a TUI
===============================================
Take the multi-turn chatbot you built in Week 1 and give it a full-screen terminal UI
using Textual. The chat logic stays the same; you're just changing the interface.

Requirements:
  - A scrollable chat log that shows conversation history
  - An input box at the bottom for the user to type
  - Keyboard shortcuts:
      Ctrl+L  →  clear the chat display (not the conversation history)
      Ctrl+K  →  compact: clear conversation history too (fresh start)
      Ctrl+Q  →  quit the application
  - Messages displayed with clear role labels: [You] and [Agent]
  - The UI must not freeze while waiting for an API response

Stretch goals:
  - Show the model name and token count in the Header or Footer
  - Add a Ctrl+S binding to save the conversation to a text file
  - Display a "thinking..." indicator while the API call is in progress

Important: API calls are blocking. Use run_worker(thread=True) to keep the UI alive
while waiting for responses. See Lesson 4 for the pattern.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header,Footer,Input,RichLog
from textual.containers import Vertical
from textual import work

load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=os.environ["OPENROUTER_API_KEY"],)
model = "openrouter/free"
max_history_len = 20

def call_model(messages: list[dict]) -> str:
    response = client.chat.completions.create(model=model,messages=messages)
    return response.choices[0].message.content

def trim_history(messages: list[dict],max_history_len:int) -> list[dict]:
    if(len(messages) > 1+max_history_len):
        messages = [messages[0]] + messages[-1*max_history_len:]
    return messages

class ChatApp(App):
    """A full-screen terminal chatbot."""

    TITLE = "Week 2 Chatbot TUI"
    CSS = """
    Screen {
        layout: vertical;
    }

    RichLog {
        height: 1fr;
        border: solid $primary;
        padding: 0 1;
    }

    Input {
        dock: bottom;
        height: 3;
    }
    """

    BINDINGS = [
        Binding("ctrl+l", "clear_display", "Clear display"),
        Binding("ctrl+k", "clear_history", "Clear history",priority=True),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.messages: list[dict] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(id="log", wrap=True, markup=True, highlight=True)
        yield Input(placeholder="Type a message and press Enter...")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#log", RichLog)
        log.write("[bold green]Chat started.[/bold green]\nCtrl+Q to quit chat\nCtrl+L to clear dashboard\nCtrl+K to clear history and dashboard\n")
        self.query_one(Input).focus()

    def on_input_submitted(self,event:Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return
        event.input.clear()
        log = self.query_one("#log", RichLog)
        log.write(f"[blue][You][/blue] {user_text}\n")
        log.write("[gray]Thinking .. [/gray]\n")
        self.messages.append({"role": "user", "content": user_text})
        self.messages = trim_history(self.messages,max_history_len)
        self._get_response()

    @work(thread=True)
    def _get_response(self) -> None:
        log = self.query_one("#log", RichLog)
        try :
            bot_output = call_model(self.messages)
            self.messages.append({"role":"assistant","content":bot_output})
            self.messages = trim_history(self.messages,max_history_len)
            self.call_from_thread(log.write,f"[bold blue][AGENT][/bold blue] : {bot_output}\n")
        except Exception as e:
            self.call_from_thread(log.write,f"[bold red]Error can't connect to API beacuse[/bold red] {str(e)}\n")    

    def action_clear_display(self) -> None:
        log = self.query_one("#log",RichLog)
        log.clear()
        log.write("[green]Display Cleared.[/green]\n")

    def action_clear_history(self) -> None:
        self.messages = [self.messages[0]]
        log = self.query_one("#log",RichLog)
        log.clear()
        log.write("[green]Display and History Cleared.[/green]\n")

if __name__ == "__main__":
    ChatApp().run()