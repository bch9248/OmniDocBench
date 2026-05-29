# System Prompt
# SYSTEM_PROMPT = (
#     "You are a document analysis system. "
#     "Perform PAGE-LEVEL document parsing only. "
#     "Do not infer cross-page information."
# )

# System Prompt
# SYSTEM_PROMPT = """ You are an AI assistant specialized in converting PDF images to JSON format. Please follow these instructions for the conversion:

#     1. Text Processing:
#     - Accurately recognize all text content in the PDF image without guessing or inferring.
#     - Convert the recognized text into JSON format.
#     - Maintain the original document structure, including headings, paragraphs, lists, etc.

#     2. Mathematical Formula Processing:
#     - Convert all mathematical formulas to LaTeX format.
#     - Enclose inline formulas with \( \). For example: This is an inline formula \( E = mc^2 \)
#     - Enclose block formulas with \\[ \\]. For example: \[ \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \]

#     3. Table Processing:
#     - Convert tables to HTML format.
#     - Wrap the entire table with <table> and </table>.

#     4. Figure Handling:
#     - Ignore figures content in the PDF image. Do not attempt to describe or convert images.

#     5. SPICE Diagrams:
#     - Detect and extract electrical schematics or circuit diagrams.
#     - Convert these into a functional, text-based SPICE netlist.
#     - Format: Use a standard component-node-value sequence (e.g., R1 1 2 10k).
#     - Container: Wrap the entire netlist strictly with ```spice and ```.
#     - Ground: Always designate the circuit common/ground as node 0.

#     6. Output Format:
#     - Ensure the output JSON document has a clear structure in appropriate schema, following the natural reading order of the document.
#     - For complex layouts, try to maintain the original document's structure and format as closely as possible.

#     Please strictly follow these guidelines to ensure accuracy and consistency in the conversion. Your task is to accurately convert the content of the PDF image into JSON format without adding any extra explanations or comments.
# """

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

    5. SPICE Diagrams:
    - Detect and extract electrical schematics or circuit diagrams.
    - Convert these into a functional, text-based SPICE netlist.
    - Format: Use a standard component-node-value sequence (e.g., R1 P3V3DS 1 10k).
    - The Net name is in black font, the Component name is in blue or green font.
    - Write the node in identical black font Net names as in the diagram if provided, otherwise use 1 ,2, 3, etc.
    - Make sure to include all components and net names exactly as shown in the diagram.
    - Container: Wrap the entire netlist strictly with ```spice and ```.
    - Ground: Always designate the circuit common/ground as node 0.
    
    6. Output Format:
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
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments

"""

def get_gpt5_prompt(page_id, width, height):
    return f"""
Parsing this document follow the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments

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
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments

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
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments

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
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments
"""

def get_sr_prompt(page_id, width, height, queries=None):
    query_section = ""
    if queries:
        query_section = "Below are the circuit diagram queries that expect to be answered on this page:\n## Circuit Connection Queries\n\n"
        for i, query in enumerate(queries, 1):
            query_section += f"{i}. **Query**: {query.get('query', '')}\n"
            query_section += f"   **Connection Script**: {query.get('script', '')}\n"
            query_section += "\n"
        query_section += "\n"
    
    return f"""{query_section}Parsing this document following these steps and rules.

Steps:
1. Base on those queries, imagine what formulation of circuit diagrams you expect to see on the page. How are they related to the queries?
2. Analyze the page and identify each layout block.
3. For each block, determine its type, text content, and bounding box.
4. Make a cross-verification between imagination and the information from each layout block properly.
5. Construct the final output following the rules.

Rules:
- Output ONLY the element in the document in md format , do not output the queries or your imagination
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments
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
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments
"""

def get_sr_wos_prompt(page_id, width, height):
    return f"""
Parsing this document following these steps and rules.

Steps:
1. Analyze the page and identify each layout block.
2. For each block, determine its type, text content, and bounding box.
3. Construct the final output following the rules.

Rules:
- Output ONLY the element in the document in md format 
- Treat this as a single independent page
- Follow the reading order of the document
- Detect layout blocks and their bounding boxes
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code
- For spice diagrams, output the netlist format, Must enclose in ```spice and ```.
- No explanations, no comments
"""

def get_golden_prompt(page_id, width, height, sr_hint=None):
    hint_section = ""
    if sr_hint:
        hint_section = f"""
IMPORTANT: Reading Order Reference
Below is a markdown representation of this page that shows the correct reading order.
Use this as a HINT to determine the proper sequence of layout blocks:

--- START READING ORDER HINT ---
{sr_hint}
--- END READING ORDER HINT ---

"""
    
    prompt = f"""
Parsing this document following these steps and rules.

Steps:
1. Analyze the page and identify each layout block.
2. For each block, determine its type, text content, and bounding box.
3. Detect if the text in each block is rotated or not. There are only two possible angles, 0 and 270 degrees. Identify the angle for each block.
4. If the text is rotated (270 degrees), identify the real text content accordingly to reflect the rotation.
5. Integrate all text content to the information from each layout block properly.
6. Use the reading order hint provided to properly order the blocks.
7. From the integration, construct the final output following the rules.

{hint_section}Rules:
- Output ONLY the element in the document in json schema format 
- Treat this as a single independent page
- Follow the reading order of the document (use the hint above to determine correct order)
- Detect layout blocks and their bounding boxes
- Category type is <one of: title | text_block | figure | figure_caption | figure_footnote | table | table_caption | table_footnote | equation_isolated | equation_caption | header | footer | page_number | page_footnote | abandon | code_txt | code_txt_caption | reference | text_span | equation_ignore | equation_inline | circuit_diagram | circuit_footnote | circuit_caption | footnote_mark>
- For tables, output the content in valid HTML format
- For formulas, output the LaTeX code, MUST enclose in $...$
- For spice diagrams, output the netlist format
- No markdown, no explanations


json schema example:
"""
    
    json_example = f"""{{
  "page_info": {{ "page_attribute": {{"xxx": "xxx"}}, "page_no": {page_id}, "height": {height}, "width": {width}, "image_path": "page_{page_id}.png" }},
  "layout_dets": [
      {{
          "category_type": "text_block",
          "poly": [100.0, 100.0, 1100.0, 100.0, 1100.0, 300.0, 100.0, 300.0],
          "ignore": false, "order": 0, "anno_id": 0,
          "text": "THIS DRAWING AND SPECIFICATIONS, HEREIN, ARE THE PROPERTY OF INVENTEC CORPORATION..."
      }},
      {{
          "category_type": "title",
          "poly": [300.0, 500.0, 900.0, 500.0, 900.0, 650.0, 300.0, 650.0],
          "ignore": false, "order": 1, "anno_id": 1,
          "text": "MACHU1416 TLD"
      }},
      {{
          "category_type": "circuit_diagram",
          "poly": [500.0, 700.0, 700.0, 700.0, 700.0, 750.0, 500.0, 750.0],
          "ignore": false, "order": 2, "anno_id": 2,
          "spice": "```spice\\nR8905 301k_1%_2 PV_SYS PV_SYS_RC 0.5M\\nR8906 49.9k_1%_2 PV_SYS_RC OUT 0.5M\\nC8907 100pF_50V_2 PV_SYS 0\\nC8908 49.9k_1%_2 OUT 0.5M\\nC8909 0.22uF_6.3V_2 OUT 0\\nRB855 75_5%_2 CPU_PROC_HOST IN 0.5M\\nRB854 75_5%_4 2 3\\nQ68054 1.2MHZ 3 0 G Q68054_D PANJIT_2N7002KW_3P OFF Vgs=-4.5V 6015B0167001_003\\n```"
      }},
      {{
          "category_type": "equation_isolated",
          "poly": [50.0, 50.0, 1150.0, 50.0, 1150.0, 1400.0, 50.0, 1400.0],
          "ignore": false, "order": 3, "anno_id": 3,
          "latex": "$RSET\\\\ (K\\\\ \\\\mathrm{{OHM}}) = 0.0012T^{{2}} - 0.9308T + 96.147$"
      }},
      {{
          "category_type": "table",
          "poly": [500.0, 1500.0, 700.0, 1500.0, 700.0, 1550.0, 500.0, 1550.0],
          "ignore": false, "order": 4, "anno_id": 4,
          "html": "<table><thead><tr><th>MARKING</th><th>DESCRIPTION</th></tr></thead><tbody><tr><td>M</td><td>MOTHER BOARD</td></tr><tr><td>U</td><td>DAUGHTER BOARD</td></tr><tr><td>F</td><td>14 INCH MOTHER BOARD</td></tr><tr><td>S</td><td>16 INCH MOTHER BOARD</td></tr></tbody></table>"
      }}
  ],
  "extra": {{ "relation": [] }}
}}"""
    
    return prompt + json_example

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
    # "golden": get_golden_prompt,
    # "gpt5": get_gpt5_prompt,

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