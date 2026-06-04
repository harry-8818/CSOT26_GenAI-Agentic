# Learnings from Build 1 :
I first tried to understand the strcuture of the model how we call different models from openrouter using API key.
The chat.completions will take the input given by user and they generate a response object which contains the whole piece of information regarding the answer to tha prompt and the backend(token usage).
I also tried adding a system role that forces the bot to return the response in only one sentence.

## Contents in Response object:
It contains the unique ID generated during every call,type od data returned, model used.

### response.choices:
This contains the one or more generated results.
finish_reason tells us why the generation stopped
if it is equal to "stop" that means it has naturally finished its thought
or if it is equal to "length" that means it ran out of room
It also contains the final response to the query specified by role="assistant"

### response.usage:
This conatins the info regarding the tokens used for the query, backend and tokens used for writing the response and finally stores the total tokens used in each call.
It keeps on subtarcting the total tokens from the remaining token budget.