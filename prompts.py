# System Prompt
# SYSTEM_PROMPT = (
#     "You are a document analysis system. "
#     "Perform PAGE-LEVEL document parsing only. "
#     "Do not infer cross-page information."
# )

# System Prompt
SYSTEM_PROMPT = """ You are an AI assistant specialized in converting PDF images to Markdown format. Please follow these instructions for the conversion:

    1. Text Processing:
    - Accurately recognize all text content in the PDF image without guessing or inferring.
    - Convert the recognized text into Markdown format.
    - Maintain the original document structure, including headings, paragraphs, lists, etc.

    2. Mathematical Formula Processing:
    - Convert all mathematical formulas to LaTeX format.
    - Enclose inline formulas with \( \). For example: This is an inline formula \( E = mc^2 \)
    - Enclose block formulas with \\[ \\]. For example: \[ \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \]

    3. Table Processing:
    - Convert tables to HTML format.
    - Wrap the entire table with <table> and </table>.

    4. Figure Handling:
    - Ignore figures content in the PDF image. Do not attempt to describe or convert images.

    5. Output Format:
    - Ensure the output Markdown document has a clear structure with appropriate line breaks between elements.
    - For complex layouts, try to maintain the original document's structure and format as closely as possible.

    Please strictly follow these guidelines to ensure accuracy and consistency in the conversion. Your task is to accurately convert the content of the PDF image into Markdown format without adding any extra explanations or comments.
"""


def get_naive_prompt(page_id, width, height):
    return f"""
Parsing this document follow the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations

"""

def get_cot_prompt(page_id, width, height):
    return f"""
Parsing this document step-by-step following the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations

"""

def get_pearl_prompt(page_id, width, height):
    return f"""
Parsing this document following these steps and rules.

Steps:
1. Plan: read the document and output a sequence of steps to parse it.
2. Execute: execute each plan step internally.
3. Aggregate: integrates all information from each step to produce the final output.


Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations

"""


def get_react_prompt(page_id, width, height):
    return f"""
Parsing this document following these steps and rules:

Steps with ReAct framework (loop until done):
Thought: What should I analyze on the page?
Action: Analyze following the previous thought.
Observation: What did I learn from the analysis?

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations
"""

def get_sr_prompt(page_id, width, height):
    return f"""
Parsing this document following these steps and rules.

Steps:
1. Try to parse all text content from the page first, for the structured text like table, formula, try to denote them in your natural language first.
2. Analyze the page and identify each layout block.
3. For each block, determine its type, text content, and bounding box.
4. Integrate all text content to the information from each layout block properly.
5. From the integration, construct the final output following the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations
"""

def get_sr_woa_prompt(page_id, width, height):
    return f"""
Parsing this document following these steps and rules.

Steps:
1. Retrieve all text content from the page first and construct the final output following the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations
"""

def get_sr_wos_prompt(page_id, width, height):
    return f"""
Parsing this document following these steps and rules.

Steps:
1. Analyze the text content and and identify each layout block.
2. For each block, determine its type, text content, and bounding box.
3. Construct the final output following the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- No markdown, no explanations
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


# Mapping modes to functions for easy access
PROMPT_MAP = {
    "naive": get_naive_prompt,
    "cot": get_cot_prompt,
    "react": get_react_prompt,
    "pearl": get_pearl_prompt,
    "sr": get_sr_prompt,
    "sr_woa": get_sr_woa_prompt,
    "sr_wos": get_sr_wos_prompt,
}



# old one
'''
JSON schema:
{{
  "page_id": "{page_id}",
  "page_size": {{"width": {width}, "height": {height}}},
  "language": "<ISO-639-1>",
  "blocks": [
    {{
      "type": "title | text_block | figure | figure_caption | figure_footnote | table | table_caption | table_footnote | equation_isolated | equation_caption | header | footer | page_number | page_footnote | abandon | code_txt | code_txt_caption | reference | text_span | equation_ignore | equation_inline | footnote_mark",
      "text": "...",
      "bbox": [x_min, y_min, x_max, y_max]
    }}
  ]
}}

JSON schema:
{{
  "layout_dets": [       // List of page elements
    {{
      "category_type": "<one of: title | text_block | figure | figure_caption | figure_footnote | table | table_caption | table_footnote | equation_isolated | equation_caption | header | footer | page_number | page_footnote | abandon | code_txt | code_txt_caption | reference | text_span | equation_ignore | equation_inline | footnote_mark>",
      "poly": [x1, y1, x2, y2, x3, y3, x4, y4], 
      "ignore": false,    // Whether to ignore during evaluation
      "order": 0,         // Reading order
      "anno_id": 0,       // Special annotation ID, unique for each layout box
      "text": "...",      // Optional field, Text OCR results are written here
      "latex": "$...$",   // Optional field, LaTeX for formulas is written here, MUST enclose in $...$
      "html": "...",      // Optional field, HTML for tables is written here, MUST in valid HTML format
      "attribute": {{"xxx": "xxx"}},
      "line_with_spans": [
        {{
          "category_type": "text_span | equation_inline | equation_ignore | footnote_mark",
          "poly": [...],
          "ignore": false,
          "text": "...",
          "latex": "$...$"
        }}
      ],
      "merge_list": []
    }}
  ],
  "page_info": {{
    "page_no": "{page_id}",
    "height": "{height}",
    "width": "{width}",
    "image_path": "xx/xx.png",
    "page_attribute": {{"xxx": "xxx"}}
  }},
  "extra": {{
    "relation": []
  }}
}}
Rules for filling fields based on category type:

1. title, text_block, header, footer, page_number, page_footnote, equation_caption, equation_ignore, table_caption, table_footnote , figure_caption, figure_footnote, reference, code_txt, code_txt_caption, abandon: fill "text", leave "latex" and "html" empty.
2. equation_isolated, equation_inline: fill "latex", leave "text" and "html" empty. Need to enclose the equation text in "$ ... $".
3. table: fill "latex" and/or "html", leave "text" empty. 
4. figure: fill "text", leave "latex" and "html" empty.
5. text_span, footnote_mark: nested inside "line_with_spans".
6. "order" starts from 0 and increases sequentially for each block. This is for reading order.
6. Always provide "poly", "order", "anno_id".
7. Use "merge_list" for multi-line blocks.

Return valid JSON only, without extra text.
'''