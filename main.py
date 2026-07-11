# import base64
# import json
# import os

# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# from agent.executor import Executor
# from agent.llm_client import LLMClient
# from agent.planner import Planner
# from agent.utils import ensure_dir

# # -------------------------------------------------------
# # Load Environment Variables
# # -------------------------------------------------------

# load_dotenv()

# # -------------------------------------------------------
# # FastAPI
# # -------------------------------------------------------

# app = FastAPI(
#     title="Autonomous AI Agent",
#     version="1.0.0",
#     description="Autonomous Planning Agent using Groq"
# )

# # -------------------------------------------------------

# class AgentRequest(BaseModel):
#     request: str

# # -------------------------------------------------------

# ensure_dir("demo_outputs")

# # -------------------------------------------------------
# # Initialize LLM
# # -------------------------------------------------------

# try:

#     llm = LLMClient(
#         model="llama-3.3-70b-versatile",
#         fallback_to_mock=False
#     )

# except Exception as e:

#     raise RuntimeError(
#         f"Failed to initialize LLM.\n{e}"
#     )

# planner = Planner(llm)
# executor = Executor(llm)

# # -------------------------------------------------------

# @app.get("/")
# async def root():

#     return {

#         "status": "running",

#         "message": "Autonomous AI Agent is ready."

#     }

# # -------------------------------------------------------

# @app.post("/agent")
# async def run_agent(req: AgentRequest):

#     user_request = req.request.strip()

#     # ----------------------------------------------
#     # Request Validation
#     # ----------------------------------------------

#     if not user_request:

#         raise HTTPException(
#             status_code=400,
#             detail="Request cannot be empty."
#         )

#     if len(user_request) < 10:

#         raise HTTPException(
#             status_code=400,
#             detail="Request is too short."
#         )

#     print("\n")
#     print("=" * 70)
#     print("USER REQUEST")
#     print("=" * 70)
#     print(user_request)

#     # ----------------------------------------------
#     # Planning
#     # ----------------------------------------------

#     try:

#         plan = planner.create_plan(user_request)

#         print("\n")
#         print("=" * 70)
#         print("GENERATED EXECUTION PLAN")
#         print("=" * 70)

#         print(json.dumps(
#             plan,
#             indent=4
#         ))

#     except Exception as e:

#         raise HTTPException(

#             status_code=500,

#             detail=f"Planner Error:\n{str(e)}"

#         )

#     # ----------------------------------------------
#     # Execute Plan
#     # ----------------------------------------------

#     try:

#         result = executor.execute_plan(

#             plan,

#             user_request

#         )

#     except Exception as e:

#         raise HTTPException(

#             status_code=500,

#             detail=f"Executor Error:\n{str(e)}"

#         )

#     # ----------------------------------------------
#     # Read DOCX
#     # ----------------------------------------------

#     doc_path = result.get("docx_path")

#     doc_base64 = None

#     if doc_path and os.path.exists(doc_path):

#         with open(doc_path, "rb") as f:

#             doc_base64 = base64.b64encode(

#                 f.read()

#             ).decode("utf-8")

#     # ----------------------------------------------

#     response = {

#         "status": "success",

#         "request": user_request,

#         "document_type": plan.get(
#             "document_type"
#         ),

#         "assumptions": plan.get(
#             "assumptions",
#             []
#         ),

#         "tasks": plan.get(
#             "tasks",
#             []
#         ),

#         "execution_plan": plan.get(
#             "plan",
#             []
#         ),

#         "execution_log": result.get(
#             "execution_log",
#             []
#         ),

#         "reflection": result.get(
#             "reflection",
#             {}
#         ),

#         "docx_path": doc_path,

#         "docx_base64": doc_base64

#     }

#     print("\n")
#     print("=" * 70)
#     print("AGENT COMPLETED SUCCESSFULLY")
#     print("=" * 70)

#     return response

import base64
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.executor import Executor
from agent.llm_client import LLMClient
from agent.planner import Planner
from agent.utils import ensure_dir

# -------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------

load_dotenv()

# -------------------------------------------------------

app = FastAPI(
    title="Autonomous AI Agent",
    version="1.0",
    description="Autonomous Planning Agent using Groq"
)

# -------------------------------------------------------

class AgentRequest(BaseModel):
    request: str

# -------------------------------------------------------

ensure_dir("demo_outputs")

llm = LLMClient()
planner = Planner(llm)
executor = Executor(llm)

# -------------------------------------------------------

@app.get("/")
async def home():

    return {
        "status": "running",
        "message": "Autonomous AI Agent is ready."
    }

# -------------------------------------------------------

@app.post("/agent")
async def run_agent(req: AgentRequest):

    user_request = req.request.strip()

    if not user_request:
        raise HTTPException(
            status_code=400,
            detail="Request cannot be empty."
        )

    if len(user_request) < 10:
        raise HTTPException(
            status_code=400,
            detail="Request is too short."
        )

    print("\n" + "=" * 70)
    print("USER REQUEST")
    print("=" * 70)
    print(user_request)

    # ---------------- Planner ----------------

    plan = planner.create_plan(user_request)

    print("\n" + "=" * 70)
    print("GENERATED PLAN")
    print("=" * 70)
    print(json.dumps(plan, indent=4))

    # ---------------- Executor ----------------

    result = executor.execute_plan(
        plan,
        user_request
    )

    # ---------------- DOCX ----------------

    doc_path = result["docx_path"]

    doc_base64 = None

    if os.path.exists(doc_path):

        with open(doc_path, "rb") as f:

            doc_base64 = base64.b64encode(
                f.read()
            ).decode()

    print("\n" + "=" * 70)
    print("EXECUTION FINISHED")
    print("=" * 70)

    return {

        "status": "success",

        "request": user_request,

        "document_type": plan["document_type"],

        "assumptions": plan["assumptions"],

        "tasks": plan["tasks"],

        "execution_plan": plan["plan"],

        "execution_log": result["execution_log"],

        "reflection": result["reflection"],

        "docx_path": doc_path,

        "docx_base64": doc_base64

    }