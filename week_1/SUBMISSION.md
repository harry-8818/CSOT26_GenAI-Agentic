# Key Safety :
The API key is loaded from a .env file via python-dotenv and never written in source.
.env is listed in .gitignore so it's never committed too.


# Learnings from Build 1 :
I first tried to understand the structure of the model and how we call different models from OpenRouter using an API key.
The chat.completions call takes the input given by the user and generates a response object which contains the whole piece of information regarding the answer to the prompt and the backend (token usage).
I also tried adding a system role that forces the bot to return the response in only one sentence.

## Contents in Response object:
It contains the unique ID generated during every call, type of data returned, and model used.

### response.choices:
This contains the one or more generated results.
finish_reason tells us why the generation stopped:
if it is equal to "stop" that means it has naturally finished its thought,
or if it is equal to "length" that means it ran out of room.
It also contains the final response to the query specified by role="assistant".

### response.usage:
This contains the info regarding the tokens used for the query and the tokens used for writing the response, and finally stores the total tokens used in each call. It only reports the counts for that single call and does not track any account-wide budget.

After this I tried changing the question, like "Who is the wife of Virat Kohli?" and "Who is Virat Kohli and what is his role in RCB?"
In the output I got the answer in a multi-sentence paragraph because I told the agent to output the answer in a single line, so it gave the answer without any new lines rather than as a single sentence — i.e. it takes our set of rules literally.
Hence, we must be very specific about the set of rules and instructions.
One more thing I noticed using different models is that non-reasoning models returned reasoning=None, while reasoning models returned a step-by-step monologue and a count of reasoning_tokens too, which this time was about 80 percent of the completion tokens.
This shows that reasoning models generate a costly thinking part which is different from message.content (the final answer).

# Towards Build 2 :
I visited the official OpenRouter website to check the available free models and I listed a few of them.
Then I asked the user to select any one of the models of his/her choice.
Then I made the exit block by checking the input of the user.
Then I started working on capturing the history by appending the dictionaries into the messages list and providing the agent a new list after every call.
I tried running with the model numbered 1 in the available_models list but it was not live at that moment, so if a user tries to use a model which is not available or too occupied, I took care of it using a try/except block in the call function. Now if there is any issue with the agent it will simply request the user to either try again later or use another model.
Then, to keep the chat alive, we have to manage the memory (messages list), so after a certain number of calls we remove the oldest part of the memory and keep the latest ones in the messages along with the system_prompt.
I also added the reset command, which removes everything in the messages and keeps only the system_prompt.