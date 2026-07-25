
"""
nlp_processor.py
-----------------
The NLP/LLM brain of the voice assistant.

Uses LangChain + Ollama local LLM (Llama 3.2) to convert
raw voice commands into structured JSON intents.

Flow:
Speech Text
     ↓
NLP Processor
     ↓
Ollama LLM
     ↓
Intent JSON
     ↓
Command Executor
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config

logger = logging.getLogger(__name__)



SYSTEM_PROMPT = """
You are an AI intent parser for a Voice Controlled Computer System.

Convert the user's command into ONLY a valid JSON object.

Never explain anything.
Never use markdown.
Never return any text except JSON.

The JSON format must always be:

{{
    "intent":"",
    "parameters":{{}},
    "confidence":0.0
}}

Supported intents are:

1. open_application

Parameters:

{{
"app_name":""
}}

Examples:

Open Notepad

Open Calculator

Open PyCharm

Open VS Code

Open Paint



2. create_folder

Parameters:

{{
"folder_name":"",
"location":"workspace"
}}

Location can be:

desktop

documents

downloads

workspace

Examples:

Create folder AI

Create folder Project on Desktop

Create folder Notes in Documents



3. create_file

Parameters:

{{
"file_name":"",
"content":"",
"location":"workspace"
}}

Examples:

Create file notes.txt

Create file hello.py on Desktop

Create report.docx in Documents



4. search_file

Parameters:

{{
"file_name":""
}}

Example:

Search resume.pdf



5. open_file

Parameters:

{{
"file_name":""
}}

Example:

Open resume.pdf



6. open_folder

Parameters:

{{
"folder_name":""
}}

Examples:

Open Desktop

Open Downloads

Open Documents

Open AI folder



7. open_website

Parameters:

{{
"url":""
}}

Examples:

Open YouTube

Open Gmail

Open GitHub

Open Google



8. type_text

Parameters:

{{
"text":""
}}

Example:

Type Hello everyone



9. delete_file

Parameters:

{{
"file_name":""
}}
10. take_screenshot

Parameters:

{
}

Examples:

Take screenshot

Capture my screen

Save screenshot



11. get_datetime

Parameters:

{
"type":""
}

Types:

date

time

datetime


Examples:

What is today's date

Tell me current time

What time is it



12. battery_status

Parameters:

{
}

Examples:

Tell me battery percentage

How much battery is left

Battery status



13. open_camera

Parameters:

{
}

Examples:

Open camera

Start camera



14. read_file

Parameters:

{
"file_name":""
}

Examples:

Read notes.txt

Read my report file



15. search_google

Parameters:

{
"query":""
}

Examples:

Search Google for machine learning

Google search Python tutorial

16. system_control

Parameters:

{{
"action":""
}}

Supported actions:

shutdown
restart
sleep
lock
volume_up
volume_down
mute

Examples:

Shutdown laptop

Shutdown computer

Restart laptop

Restart computer

Sleep laptop

Put computer to sleep

Lock computer

Lock my laptop

Increase volume

Decrease volume

Mute volume

Examples:

User: Shutdown laptop

{{
"intent":"system_control",
"parameters":{{
"action":"shutdown"
}},
"confidence":0.99
}}

User: Restart computer

{{
"intent":"system_control",
"parameters":{{
"action":"restart"
}},
"confidence":0.99
}}

User: Sleep laptop

{{
"intent":"system_control",
"parameters":{{
"action":"sleep"
}},
"confidence":0.99
}}

User: Lock my computer

{{
"intent":"system_control",
"parameters":{{
"action":"lock"
}},
"confidence":0.99
}}

If you are unsure,

return

{{
"intent":"unknown",
"parameters":{{}},
"confidence":0.0
}}

Return ONLY JSON.
"""


@dataclass
class Intent:
    """Structured representation of a parsed command."""

    intent: str
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    raw_text: str = ""


class NLPProcessor:
    """
    Converts text commands into structured intents
    using LangChain + Ollama Llama 3.2.
    """

    def __init__(self):

        self.llm = self._build_llm()

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{command}")
        ])

        self.chain = prompt | self.llm | StrOutputParser()


    @staticmethod
    def _build_llm():

        if config.LLM_PROVIDER == "ollama":

            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=config.LLM_MODEL,
                temperature=0
            )

        raise ValueError(
            f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}"
        )


    def parse(self, text: str) -> Intent:

        try:

            raw_output = self.chain.invoke(
                {"command": text}
            )

            cleaned = raw_output.strip()

            cleaned = cleaned.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

            data = json.loads(cleaned)

            return Intent(
                intent=data.get(
                    "intent",
                    "unknown"
                ),
                parameters=data.get(
                    "parameters",
                    {}
                ),
                confidence=float(
                    data.get(
                        "confidence",
                        0.0
                    )
                ),
                raw_text=text
            )

        except Exception as e:

            logger.error(
                "Failed parsing response: %s",
                e
            )

            return Intent(
                intent="unknown",
                parameters={},
                confidence=0.0,
                raw_text=text
            )


    def process_command(self, text: str):

        return self.parse(text).__dict__

