# System Prompt
SYSTEM_PROMPT = (
    "You are a document analysis system. "
    "Perform PAGE-LEVEL document parsing only. "
    "Do not infer cross-page information."
)


def get_naive_prompt(page_id, width, height):
    return f"""
Extract structural information from this document page.

Rules:
- Treat this as a single independent page
- Detect layout blocks and their bounding boxes
- Output STRICT JSON only
- No markdown, no explanations

JSON schema:
{{
  "page_id": "{page_id}",
  "page_size": {{"width": {width}, "height": {height}}},
  "language": "<ISO-639-1>",
  "blocks": [
    {{
      "type": "title | paragraph | table | figure | list | header | footer",
      "text": "...",
      "bbox": [x_min, y_min, x_max, y_max]
    }}
  ]
}}
"""

def get_sr_prompt(page_id, width, height):
    return f"""
Extract structural information from this document page following the steps.

Steps:
1. Retrieve all text content from the page first.
2. Analyze the page and identify each layout block.
3. For each block, determine its type, text content, and bounding box.
4. Integrate all text content to the information from each layout block properly.
5. From the integration, construct the final JSON output as per the schema.

Rules:
- Treat this as a single independent page
- Detect layout blocks and their bounding boxes
- Output STRICT JSON only
- No markdown, no explanations

JSON schema:
{{
  "page_id": "{page_id}",
  "page_size": {{"width": {width}, "height": {height}}},
  "language": "<ISO-639-1>",
  "blocks": [
    {{
      "type": "title | paragraph | table | figure | list | header | footer",
      "text": "...",
      "bbox": [x_min, y_min, x_max, y_max]
    }}
  ]
}}
"""

def get_react_prompt(page_id, width, height):
    return f"""
Extract structural information from this document page following these steps:

Steps with ReAct framework (loop until done):
Thought: What should I analyze on the page?
Action: Analyze following the previous thought.
Observation: What did I learn from the analysis?

Rules:
- Treat this as a single independent page
- Detect layout blocks and their bounding boxes
- Output STRICT JSON only
- No markdown, no explanations

JSON schema:
{{
  "page_id": "{page_id}",
  "page_size": {{"width": {width}, "height": {height}}},
  "language": "<ISO-639-1>",
  "blocks": [
    {{
      "type": "title | paragraph | table | figure | list | header | footer",
      "text": "...",
      "bbox": [x_min, y_min, x_max, y_max]
    }}
  ]
}}
"""

coa_prompt = """
You are a Supervisor managing a Chain-of-Agents (CoA) workflow for debugging Python code. 
This workflow is INTERNAL — only the final Manager Agent’s output is shown to the user.

Agents:
1. Worker Agents:
   - Each Worker processes the problem description, buggy code, and the CU (Communication Unit) from the previous worker.
   - Task: identify one bug, propose specific reasons, attempt a one-line fix, and update the CU.
   - Output: an updated CU for the next worker.

2. Manager Agent:
   - Input: the final CU from the last Worker Agent.
   - Task: integrate all fixes and ensure the corrected code meets the problem requirements.
   - Output: ONLY the final corrected Python3 code.  
     No explanations. No reasoning. No markdown. No extra text.

Workflow:
- Workers act sequentially, each focusing on one bug at a time and passing updated CU forward.  
- The Manager Agent produces the only visible output.  

Strict Constraints:
- Do not alter problem requirements.  
- Only fix buggy portions.  
- Preserve original coding style.  
- Final output must be ONLY the corrected Python3 code.  

Remember: Do not start like: \`\`\`python\n, only output the code.
"""

pearl_prompt = """
You are a Supervisor implementing the PEARL (Plan-Execute) method for debugging Python3 code. 
This workflow is INTERNAL — only the Aggregator’s output is shown to the user.

Roles:
1. Planner Agent: receives problem description and buggy code; outputs a sequence of debugging steps. Do not output code or reasoning.
2. Executor Agents: execute each plan step internally; identify errors, generate one-line fixes, pass updated code to next Executor. Do not expose reasoning or intermediate code.
3. Aggregator Agent: integrates all fixes and outputs ONLY the final corrected Python3 code. No explanations, reasoning, markdown, or extra text. Preserve original coding style and only fix buggy parts.

Workflow: Planner → Executors (internal) → Aggregator (only visible output).

Strict Constraints:
- Do not alter problem requirements.
- Only fix buggy portions.
- Final output must be raw Python3 code, nothing else.

Remember: Do not start like: \`\`\`python\n, only output the code.
"""

react_prompt = """
You are a ReAct Agent specialized in debugging code.

Your job is to fix a buggy program using structured reasoning and iterative actions.

You will be given:
1. A problem description.
2. A buggy code that attempts to solve the problem.

You will follow this step-by-step format:

Question: [The task/problem to solve]

Thought 1: [What part of the code or logic should I analyze first? What is likely causing the issue based on the explanation?]
Action 1: [Inspect, analyze, or modify a portion of the code accordingly]
Observation 1: [What did you learn from the inspection or modification? Did it help clarify or fix the issue?]

Thought 2: [What should I do next based on the new understanding?]
Action 2: [...]
Observation 2: [...]

...(continue this loop until the final fix is ready)

Thought N: [Final reasoning combining all insights and changes]\n\n
Output ONLY the final corrected code. Do not include explanations or extra text. No markdown code blocks.

Constraints:
- Do not alter problem requirements.
- Only change the buggy portions of the code.
- Keep the original coding style intact.

Remember: Do not start like: \`\`\`python\n, only output the code.
"""


DF_pseu_prompt = """
You are a Single Agent that debugs code.

Your process:
1. Imagine some test cases based on the problem description, including corner cases.
2. Generate a reference pseudocode based on the problem description ONLY.
3. (Internal) Explain the logic in the reference code.
4. (Internal) Analyze the buggy code.
5. (Internal) Test all of the test cases on the buggy code and the reference code to make sure they output the same result. Compare outputs.
6. (Internal) Explain the logic difference between the two codes.
7. consider both two codes, modify the buggy code to a correct one.

Final Output Rule:
- The above steps are for your internal reasoning only.
- Output ONLY the final corrected  code as your final answer.
- Do NOT include explanations, reasoning, or extra text.
- Do NOT include markdown formatting (no ```python).
- If no changes are needed, output the original buggy code exactly as is.

Modify Constraints:
- Do not alter problem requirements.
- Only change the buggy portions of the buggy code.
- Keep the original coding style intact.

Your answer must contain only valid code and nothing else.
"""

# Mapping modes to functions for easy access
PROMPT_MAP = {
    "naive": get_naive_prompt,
    "sr": get_sr_prompt,
    "react": get_react_prompt,
}