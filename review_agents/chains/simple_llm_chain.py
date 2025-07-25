import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import Runnable

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "review_prompts.json")

# Todo: Use Vault
USE_PORTKEY = os.getenv("USE_PORTKEY", "false").lower() == "true"
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SimpleLLMChainExecutor:
    def __init__(self):
        self.prompts = self._load_prompts()
        self.llm = ChatOpenAI(
            temperature=0.3,
            model="gpt-4",
            openai_api_key=PORTKEY_API_KEY if USE_PORTKEY else OPENAI_API_KEY,
            base_url="https://api.portkey.ai/v1/proxy/openai" if USE_PORTKEY else None,
        )

    def _load_prompts(self) -> dict:
        with open(PROMPT_FILE, "r") as f:
            return json.load(f)

    def build_chain(self, factor: str) -> Runnable:
        # Prompts can be loaded from a database in future.
        prompt_text = self.prompts.get(factor)
        if not prompt_text:
            raise ValueError(f"No prompt found for factor: {factor}")
        prompt = PromptTemplate(input_variables=["code"], template=prompt_text)
        return prompt | self.llm
