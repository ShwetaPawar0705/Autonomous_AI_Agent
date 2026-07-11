

from agent.prompts import TASK_EXTRACTION_PROMPT
from agent.utils import safe_parse_json


class Planner:

    def __init__(self, llm):
        self.llm = llm

    def create_plan(self, user_request: str):

        prompt = TASK_EXTRACTION_PROMPT.format(
            user_request=user_request
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an Autonomous Planning Agent.\n"
                    "Your job is ONLY to create an execution plan.\n"
                    "Do NOT write the final document.\n"
                    "Return ONLY valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        try:

            response = self.llm.chat(
                messages=messages,
                temperature=0,
                max_tokens=1800,
                force_json=True,
            )

            raw = response.get("content", "").strip()

            print("\n========== PLANNER OUTPUT ==========")
            print(raw)
            print("====================================\n")

            plan = safe_parse_json(raw)

            self._validate(plan)

            return plan

        except Exception as e:

            print(f"\nPlanner failed : {e}")

            return self._fallback_plan(user_request)

    ########################################################

    def _validate(self, plan):

        if not isinstance(plan, dict):
            raise ValueError("Planner output must be JSON.")

        required = [
            "document_type",
            "assumptions",
            "tasks",
            "plan"
        ]

        for item in required:

            if item not in plan:
                raise ValueError(f"Missing field: {item}")

        if not isinstance(plan["plan"], list):
            raise ValueError("plan must be a list.")

        if len(plan["plan"]) == 0:
            raise ValueError("Plan cannot be empty.")

        for step in plan["plan"]:

            for key in [
                "step",
                "name",
                "tool",
                "prompt"
            ]:

                if key not in step:
                    raise ValueError(
                        f"Missing '{key}' in plan."
                    )

        return True

    ########################################################

    def _fallback_plan(self, user_request):

        """
        Used only if planner fails.

        Creates a dynamic document plan instead of
        generic 'write document' tasks.
        """

        return {

            "document_type": "Business Document",

            "assumptions": [

                "Missing information was completed using reasonable business assumptions."

            ],

            "tasks": [

                "Analyze Request",

                "Identify Document Structure",

                "Generate Executive Summary",

                "Generate Objectives",

                "Generate Main Content",

                "Generate Timeline",

                "Generate Risks",

                "Generate Conclusion",

                "Review Document",

                "Generate DOCX"

            ],

            "plan": [

                {
                    "step": 1,
                    "name": "Executive Summary",
                    "tool": "LLM",
                    "prompt":
                        "Write an executive summary describing the purpose of the document."
                },

                {
                    "step": 2,
                    "name": "Objectives",
                    "tool": "LLM",
                    "prompt":
                        "Write clear project objectives using bullet points."
                },

                {
                    "step": 3,
                    "name": "Project Scope",
                    "tool": "LLM",
                    "prompt":
                        "Describe the project scope including inclusions and exclusions."
                },

                {
                    "step": 4,
                    "name": "Proposed Solution",
                    "tool": "LLM",
                    "prompt":
                        "Explain the proposed solution in detail."
                },

                {
                    "step": 5,
                    "name": "System Architecture",
                    "tool": "LLM",
                    "prompt":
                        "Describe the overall system architecture with components and data flow."
                },

                {
                    "step": 6,
                    "name": "Implementation Timeline",
                    "tool": "LLM",
                    "prompt":
                        "Create a realistic implementation timeline."
                },

                {
                    "step": 7,
                    "name": "Budget Estimate",
                    "tool": "LLM",
                    "prompt":
                        "Provide an estimated budget with major cost categories."
                },

                {
                    "step": 8,
                    "name": "Risk Assessment",
                    "tool": "LLM",
                    "prompt":
                        "Identify risks and mitigation strategies."
                },

                {
                    "step": 9,
                    "name": "Expected Business Impact",
                    "tool": "LLM",
                    "prompt":
                        "Describe the expected business value and measurable outcomes."
                },

                {
                    "step": 10,
                    "name": "Conclusion",
                    "tool": "LLM",
                    "prompt":
                        "Write a professional conclusion with next steps."
                },

                {
                    "step": 11,
                    "name": "Generate DOCX",
                    "tool": "DOCX",
                    "prompt":
                        "Generate the final Microsoft Word document."
                }

            ]

        }