## Local Perplexity clone
There are 3 reasons for this project.
1. I want a local chat interface I control
2. I want to learn some skills
3. I want to brushup on other 

## Requirements
- ollama - Core Ollama API client - enables communication with local Ollama LLM models for chat functionality
- prompt_toolkit - Add keyboard navigation controls
- llama3 - this is the default model the bot looks for
- qwen2.5-coder:32b - only needed if you want to use the swap command
- watchdog - only needed if you want to run file_watcher.  See "AI Assistant" in this doc for more info

## To run
1. In terminal navigate to local_chat_bot/backend/src
2. run `python3 main.py`

## Features
- Default subject / persona
- Set alternate subject / persona
- Store subject related chat in subject log
- Retrieve subject instructions and chat logs
- View chats, all chat or subject specific
- Allow creation of new subject / persona
- Allow user to see and update subject and persona instructions
- Allow user ability to delete chats, subjects, and persona
- Allow user ability to move chats to other subject
- UI update: start prompt / response with "User:\n" and "Assistant:\n"
- Allow swap between modals, llama3 and qwen2.5-coder:32b
- Basic UI using PyWebView

### Upcoming features
- Subjects [screen | panel | accordian | modal]
   - Source docs for specific subjects (CRUD)
   - Source links doc for specific subjects (CRUD)
- Chat history  [screen | panel | accordian | modal]
   - Allow user modify default chat title
      - On save displayed Title = 1st 10 words of chat.
      - Format: (word_word_word)
      - If multiple chats have the same name add -[nn] to the end. Format: (word_word_word-01)
      - add CRUD
- Enhanced UI
- Web search

## Default Personas
- default - a general persona focusing on sort factual responses
- gm - game master for TTRPG
- teacher - basic teacher / mentor 
- writer - basic writing assistant

## Default Subjects
- no_subject - default location for chats
- fantasy_story and scifi_story - these have simple source instructions about a fantasy / scifi story concept.