# import os
# import time
# from typing import List, Dict, Any, Optional

# try:
#     from groq import Groq
# except Exception:
#     Groq = None


# class LLMClient:
#     def __init__(
#         self,
#         model: str = "llama-3.3-70b-versatile",
#         max_retries: int = 2,
#         timeout: float = 60.0,
#         fallback_to_mock: bool = False,
#     ):
#         self.model = model
#         self.max_retries = max_retries
#         self.timeout = timeout
#         self.fallback_to_mock = fallback_to_mock

#         api_key = os.environ.get("GROQ_API_KEY")
#         self.use_mock = False

#         if Groq is None:
#             if fallback_to_mock:
#                 self.use_mock = True
#                 self.client = None
#             else:
#                 raise RuntimeError("groq package is not installed. Run: pip install groq")
#         elif not api_key:
#             if fallback_to_mock:
#                 self.use_mock = True
#                 self.client = None
#             else:
#                 raise RuntimeError("Set GROQ_API_KEY in your environment.")
#         else:
#             self.client = Groq(api_key=api_key, timeout=timeout)

#     def chat(
#         self,
#         messages: List[Dict[str, str]],
#         max_retries: Optional[int] = None,
#         temperature: float = 0.2,
#         max_tokens: int = 1200,
#         force_json: bool = False,
#     ) -> Dict[str, Any]:
#         if self.use_mock:
#             return {"content": self._mock_response(messages, force_json=force_json)}

#         retries = self.max_retries if max_retries is None else max_retries
#         attempt = 0

#         while True:
#             try:
#                 kwargs = {
#                     "model": self.model,
#                     "messages": messages,
#                     "temperature": temperature,
#                     "max_tokens": max_tokens,
#                 }
#                 if force_json:
#                     kwargs["response_format"] = {"type": "json_object"}

#                 resp = self.client.chat.completions.create(**kwargs)
#                 return {"content": resp.choices[0].message.content}

#             except Exception as e:
#                 attempt += 1
#                 if attempt > retries:
#                     raise RuntimeError(f"Groq chat failed after retries: {e}") from e
#                 time.sleep(1.5 * attempt)

#     def _mock_response(self, messages: List[Dict[str, str]], force_json: bool = False) -> str:
#         text = "\n".join(m.get("content", "") for m in messages).lower()

#         if force_json or ("strict json" in text and "plan" in text):
#             return """{
#   "document_type": "Business Document",
#   "assumptions": ["Missing details were filled with reasonable defaults."],
#   "tasks": [
#     "Understand request",
#     "Create outline",
#     "Write document sections",
#     "Generate Word file",
#     "Run self-check"
#   ],
#   "plan": [
#     {
#       "step": 1,
#       "name": "Understand request",
#       "tool": "LLM",
#       "prompt": "Summarize the user request and identify the document type."
#     },
#     {
#       "step": 2,
#       "name": "Create outline",
#       "tool": "LLM",
#       "prompt": "Create a clear outline with headings and subheadings."
#     },
#     {
#       "step": 3,
#       "name": "Write document sections",
#       "tool": "LLM",
#       "prompt": "Write the full business document content using the outline."
#     },
#     {
#       "step": 4,
#       "name": "Generate Word file",
#       "tool": "docx",
#       "prompt": "Build the final Word document."
#     }
#   ]
# }"""

#         if "summarize the user request" in text:
#             return "The user wants a business document describing the requested project in a structured and professional format."

#         if "create a clear outline" in text or "outline" in text:
#             return """1. Introduction
# 2. Objectives
# 3. Scope
# 4. Timeline
# 5. Cost Estimate
# 6. Conclusion"""

#         if "write the full business document content" in text or "write the document content" in text:
#             return """Introduction

# This document outlines the proposed project in a clear and structured format.

# Objectives

# - Define the project goals.
# - Explain the expected value.
# - Provide a simple execution direction.

# Timeline

# - Week 1: Planning and requirements.
# - Week 2: Design and review.
# - Week 3: Development and testing.
# - Week 4: Final delivery.

# Cost Estimate

# - Planning: Low
# - Development: Medium
# - Testing and delivery: Medium

# Conclusion

# This proposal provides a practical starting point for implementation."""

#         if "review" in text or "suggested_changes" in text:
#             return '{"ok": true}'

#         return "Mock Groq response: generated content for this section."

import os
import time
from typing import List, Dict, Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMClient:

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        max_retries: int = 3,
        timeout: float = 60,
    ):

        self.model = model
        self.max_retries = max_retries

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not found. Please check your .env file."
            )

        self.client = Groq(
            api_key=api_key,
            timeout=timeout,
        )

        print("=" * 60)
        print("Groq Client Initialized")
        print(f"Model : {self.model}")
        print("=" * 60)

    ##############################################################

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
        force_json: bool = False,
    ) -> Dict[str, Any]:

        for attempt in range(self.max_retries):

            try:

                kwargs = {

                    "model": self.model,

                    "messages": messages,

                    "temperature": temperature,

                    "max_tokens": max_tokens,

                }

                if force_json:

                    kwargs["response_format"] = {
                        "type": "json_object"
                    }

                response = self.client.chat.completions.create(
                    **kwargs
                )

                return {

                    "content":
                        response.choices[0].message.content

                }

            except Exception as e:

                print(
                    f"Groq Retry {attempt+1}/{self.max_retries}"
                )

                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Groq API Error: {e}"
                    )

                time.sleep(2)

    ##############################################################

    def generate_section(self, prompt):

        return self.chat(

            [

                {

                    "role": "user",

                    "content": prompt

                }

            ],

            temperature=0.2,

            max_tokens=1200

        )["content"]

    ##############################################################

    def generate_json(self, prompt):

        return self.chat(

            [

                {

                    "role": "user",

                    "content": prompt

                }

            ],

            temperature=0,

            max_tokens=1800,

            force_json=True

        )["content"]