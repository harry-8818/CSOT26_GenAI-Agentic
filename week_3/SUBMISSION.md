# Setup
1. pip install -r requirements.txt
2. Create a .env file with OPENROUTER_API_KEY and SERPER_API_KEY
3. Run the REPL with python agent.py, or the TUI with python tui.py
.gitignore excludes .env, __pycache__, and the .agent/ folder 

# BUILD 1 - session save/load + AGENTS.md loader

I used week 1 chatbot.py to make a bot that will respond to user's questions.
I made two functions save_session and load_session

## save_session
This function takes the session id and message list and saves it in the hard drive as a json file using json.dump in .agent/sessions/ folder
## load_session
This function loads a pre existing session from the hard drive as a python list using json.load from .agent/sessions/ folder.

## AGENTS.md loader
First I checked if a file named AGENTS.md exists.
If this file exists then I used the whole text in as a string and concatenated it to the base system prompt but if there is no such file I will use the base system prompt as it is.
One problem I encountered that made the final system prompt sometimes unreadable so I added two new lines to make it as a readable paragraph.


# BUILD 2 - Agent + REPLAgent with tools

As mentioned in the task we have to make two separate classes Agent and REPLAgent 
The Agent is the brain of the whole task and the REPLAgent is responsible for interaction with the user

## ANY number of tools at one time
At first I used an if else block to run the tools but the problem in that was I could only run one tool at a time and the agent was hallucinating the other tool calls to resolve that I made changes in my code.

I looped over the every tool_call if message.tool_calls is non-empty and after the running the tool , I append the result with the id of the toll_call and after we have executed all the required tools then I extracted the output from the message object using content and passed back to the the messages list

## JSON schema's -
To bridge the gaps between the python code and LLM I used JSON schema for each and every function and integrated all the schemas to a single list to pass to the agent.

### Files Tool :
#### 1. list_files ->
I used os.listdir to get the list of the files in the provided directory and then returned it by converting into a string
#### 2. read_file ->
I opened the file by the provided path of the file and returned contents in it using .read() in form of a string
#### 3. write_file ->
This function is only for writing a file from the scratch as opening in mode "w" deletes everything that exists earlier.
#### 4. edit_file ->
I used the difflib library to show the diff preview changes in the response.
I added the specific description of the replace delete and append types of edit in the schema so that the agent knows how to do the task.

### Web Tool :
#### 1. web_search ->
I stored the response of the serper using organic to ignore the extra stuff like ads, related searches and images etc.Now it only provides the regular search results.
#### 2. web_fetch ->
I first parsed the web_link provided to check if the website provides an AI friendly version else we will use the regular fetch and extracted the readable etxt using trafilatura library.

### Paper Tool :
#### 1. paper_search ->
I used my agent to search papers considering the API will return me list of papers but sometimes it was also returning dict object so I explicitly checked if the data returned by API is a list or not and to avoid memory issues I only returned the top 3 papers.
#### 2. read_paper ->
Academic papers are available in different version due to new research so to avoid 404 error we use the base ID of paper.
I also included a 404 status check so that if a paper exists on arXiv but not indexed by Hugging Face yet, it triggers a fallback to web fetching.
The API call only give us the the title,authors and the summary of the paper. To get the whole context we need to use a second call.

##### I addedd strict character limits across all the reading tools so that the LLM's context window does not crash.

# BUILD 3 - TUI with textual

Just like the gemini pro has two windows one main chat and the other showing thinking which contains all the info about executing tools and processing stuff behind the scenes, I also tried to make two panels one chat_panel and the other tool_panel doing the exact work respectively.
To solve the frozen UI problem I used the @work decorator.
I also added the three keyboard shortcuts.
Ctrl+L: Clears the UI but keeps the session memory.
Ctrl+K: Clears the UI and clear the session memory.
Ctrl+Q: Quits the UI.

## Connecting the tool_panel to agent
Earlier I was using print statement for detecting the tool activity which was not able to reach a tui.
I fixed this issue using a callback.
the Agent accepts an on_tool_event function and its log_tool calls the function if it exists otherwise it falls back to the print statement(REPL).
The tui passes handle_tool_event as the callback and because the turn function runs on a background worker thread so to give the message to UI thread handle_tool_event uses self.call_from_thread. Now tool panel updates while while agent is working on tui too.