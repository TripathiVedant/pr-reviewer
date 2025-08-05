import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import Runnable
from pydantic import SecretStr

# from langchain.output_parsers.openai_tools import JsonOutputToolsParser


from review_agents.output_schemas.pr_review_output_schema import REVIEW_OUTPUT_SCHEMA

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "review_prompts.json")

# Todo: Use Vault
# USE_PORTKEY = os.getenv("USE_PORTKEY", "false").lower() == "true"
# PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MAX_COMPLETION_TOKENS = 2000  # Todo: have ability to breakup into 2 or to fallback to llm having more context window.
MAX_PROMPT_TOKENS = 13000     # conservative margin if total limit is 16k

class ComplicatedLLMChainExecutor:
    def __init__(self):
        self.prompts = self._load_prompts()
        self.llm = ChatOpenAI(
            temperature=0.3,
            model="gpt-4o",
            openai_api_key=OPENAI_API_KEY
        )

    def _load_prompts(self) -> dict:
        with open(PROMPT_FILE, "r") as f:
            raw_prompts = json.load(f)

        # Extract only the "complex" prompts
        complex_prompts = {}
        for factor, prompt_variants in raw_prompts.items():
            complex_prompts[factor] = prompt_variants.get("complex")
        return complex_prompts

    def build_chain(self, factor: str) -> Runnable:
        prompt_text = self.prompts.get(factor)
        if not prompt_text:
            raise ValueError(f"No prompt found for factor: {factor}")
        prompt = PromptTemplate(
            input_variables=["function", "context", "diff_summary"],
            template=prompt_text
        )
        return prompt | self.llm.with_structured_output(REVIEW_OUTPUT_SCHEMA)

    async def run_chain(self, factor: str, function_data: Dict[str, str]) -> Dict[str, Any]:
        chain = self.build_chain(factor)
        return await chain.ainvoke(function_data)

    def summarize_diff(self) -> Runnable:
        """Uses an LLM to generate a concise summary of the code diff."""
        prompt_text = self.prompts.get("summarize")
        prompt_template = PromptTemplate(
            input_variables=["diff"],
            template=prompt_text
        )

        return prompt_template | self.llm
