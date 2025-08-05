import os
import json
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from pydantic import SecretStr
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import Runnable
# from langchain.output_parsers.openai_tools import JsonOutputToolsParser


from review_agents.output_schemas.pr_review_output_schema import REVIEW_OUTPUT_SCHEMA

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "review_prompts.json")

# Todo: Use Vault
# USE_PORTKEY = os.getenv("USE_PORTKEY", "false").lower() == "true"
# PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SimpleLLMChainExecutor:
    def __init__(self):
        self.prompts = self._load_prompts()
        self.llm = ChatOpenAI(
            temperature=0.3,
            model="gpt-4o",
            openai_api_key=OPENAI_API_KEY, # Todo: Use Portkey if needed.
            base_url=None, # Todo: Use Portkey if needed. "https://api.portkey.ai/v1/proxy/openai"
        )
        # self.parser = JsonOutputToolsParser(schema=REVIEW_OUTPUT_SCHEMA)

    def _load_prompts(self) -> dict:
        with open(PROMPT_FILE, "r") as f:
            raw_prompts =  json.load(f)

        simple_prompts = {}
        for factor, prompt_variants in raw_prompts.items():
            simple_prompts[factor] = prompt_variants.get("simple")
        return simple_prompts

    def build_chain(self, factor: str) -> Runnable:
        # Prompts can be loaded from a database in future.
        prompt_text = self.prompts.get(factor)
        if not prompt_text:
            raise ValueError(f"No prompt found for factor: {factor}")
        prompt = PromptTemplate(input_variables=["code"], template=prompt_text)
        return prompt | self.llm.with_structured_output(REVIEW_OUTPUT_SCHEMA)
