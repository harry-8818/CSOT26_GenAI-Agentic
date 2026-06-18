from textual.app import App,ComposeResult
from textual.binding import Binding
from textual.widgets import Header,Footer,Input,RichLog
from textual.containers import Horizontal
from textual import work 
from agent import Agent 


class AgentApp(App):
    BINDINGS = [Binding("ctrl+l","clear_chat","Clear Screen"),Binding("ctrl+k","clear_history","Clear History"),Binding("ctrl+q","quit","Quit")]

    CSS = "Horizontal{height:1fr;}#chat_panel{width:70%;border:solid darkblue;padding:2;}#tool_panel{width:30%;border:solid darkgreen;padding:1;}Input{dock:bottom;border:solid darkblue;height:5;}"
    def __init__(self):
        super().__init__()
        self.ai_agent = Agent(on_tool_event=self.handle_tool_event)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            yield RichLog(id="chat_panel",wrap=True,markup=True)
            yield RichLog(id="tool_panel",wrap=True,markup=True)
        yield Input(placeholder="ASK ME ..",id="user_input")
        yield Footer()

    def handle_tool_event(self,text:str) :
        self.call_from_thread(self.write_tool,text)

    def write_tool(self,text:str):
        self.query_one("#tool_panel",RichLog).write(text)        

    def on_mount(self):
        chat_panel = self.query_one("#chat_panel",RichLog)
        tool_panel = self.query_one("#tool_panel", RichLog)
        chat_panel.write("[orange] Ready when YOU are [/orange]")
        chat_panel.write(f"Session ID: {self.ai_agent.session_id}\n")
        tool_panel.write("Tool Execution\n")

    def action_clear_chat(self) -> None:
        """Triggered by Ctrl+L. Only clears the UI, keeps memory."""
        self.query_one("#chat_panel",RichLog).clear()
        self.query_one("#tool_panel",RichLog).clear()
        self.query_one("#chat_panel",RichLog).write(f"Session ID: {self.ai_agent.session_id}\n")
        self.query_one("#tool_panel", RichLog).write("Tool Execution\n")

    def action_clear_history(self) -> None:
        """Triggered by Ctrl+K. Wipes the UI AND the Agent's memory."""
        self.ai_agent = Agent(on_tool_event=self.handle_tool_event)
        chat_panel = self.query_one("#chat_panel",RichLog)
        tool_panel = self.query_one("#tool_panel",RichLog)
        chat_panel.clear()
        tool_panel.clear()
        self.query_one("#chat_panel",RichLog).write(f"Session ID: {self.ai_agent.session_id}\n")
        self.query_one("#tool_panel", RichLog).write("Tool Execution\n")

    async def on_input_submitted(self, event: Input.Submitted):
        user_text = event.value.strip()
        if not(user_text) :
            return
        chat_panel = self.query_one("#chat_panel",RichLog)
        tool_panel = self.query_one("#tool_panel",RichLog)
        input_box = self.query_one("#user_input",Input)
        input_box.value = ""
        chat_panel.write(f"\n[blue][YOU]: {user_text}[/blue]")
        tool_panel.write(f"\n[grey]Processing request...[/grey]")
        input_box.disabled = True 
        self.process_agent_turn(user_text)

    @work(exclusive=True, thread=True)
    def process_agent_turn(self, user_text: str):
        bot_response = self.ai_agent.turn(user_text)
        self.call_from_thread(self.display_result, bot_response)

    def display_result(self, bot_response: str):
        chat_panel = self.query_one("#chat_panel",RichLog)
        input_box = self.query_one("#user_input",Input)
        chat_panel.write(f"\n[magenta][AGENT]: {bot_response}\n[/magenta]")
        tool_panel = self.query_one("#tool_panel",RichLog)
        tool_panel.write("[grey] Turn completed.[/grey]\n")
        input_box.disabled = False
        input_box.focus()

if __name__ == "__main__":
    app = AgentApp()
    app.run()