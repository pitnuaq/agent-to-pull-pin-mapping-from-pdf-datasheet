import os
import json
import sqlite3
import fitz
import base64
from pathlib import Path
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate as cpt
from langchain_core.messages import HumanMessage
import re
import time
from PIL import Image
import io

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "api"
os.environ["LANGCHAIN_PROJECT"] = "vision_Agent_v1"

db_path = r"C:\Users\Muhammad Syafiq\Desktop\LangChain\ICs_database.db"
COOL_DOWN_TIME = 10

llm = ChatOllama(
    model="gemma4:12b",
    temperature=0.0,
    base_url="http://localhost:11434",
    keep_alive="1h",
    reasoning=True,
    num_ctx=32000
)

def normalize_mpn(mpn: str) -> str:
    """Removes all non-alphanumeric characters and converts to uppercase."""
    return re.sub(r'[^A-Z0-9]', '', str(mpn).upper())

# ==========================================
# MARKDOWN LOADER FUNCTIONS
# ==========================================

def load_markdown_directory(directory_path: Path, target_mpn: str = None, target_package: str = None) -> str:
    """Reads all .md files in alphabetical order and safely injects variables."""
    combined_content = []
    
    if not directory_path.exists():
        print(f"[Warning] Directory not found: {directory_path}")
        return ""

    for filepath in sorted(directory_path.glob("*.md")):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                combined_content.append(content)
        except Exception as e:
            print(f"[Error] Failed to load {filepath.name}: {e}")
            
    full_text = "\n\n".join(combined_content)
    
    # Safely replace placeholders without breaking JSON templates (which use { })
    if target_mpn:
        full_text = full_text.replace("{target_mpn}", target_mpn)
    if target_package:
        full_text = full_text.replace("{target_package}", target_package)
        
    return full_text

def build_system_prompt() -> str:
    """Stitches together tools.md instructions to build the agent's core brain."""
    tools_content = load_markdown_directory(Path(r"C:\Path_of_tools_details"))
    
    return (
        "You are an expert engineering AI and expert Test Engineer.\n\n"
        "=========================================\n"
        "AVAILABLE TOOLS & CONSTRAINTS\n"
        "=========================================\n"
        f"{tools_content}"
    )

# ==========================================
# TOOL DEFINITIONS
# ==========================================

@tool
def read_datasheet(pdf_path: str, target_package: str, target_mpn: str) -> str:
    '''Reads a PDF Datasheet, converts the specific page containing the Pin Assignment 
    layout into an image, and leverages Gemma Vision's multimodal reasoning to output 
    the exact pin mappings directly as a valid JSON string.'''

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return f"Error: Could not find file at {pdf_path}"
    
    print(f"[Tool] PyMuPDF is visually capturing the layout page for: {pdf_file.name}......")

    try:
        doc = fitz.open(str(pdf_file))
        target_page_num = -1

        # 1. Scan text elements to locate the exact visual layout frame
        search_keywords = [
            "PIN ASSIGNMENT", "PIN CONFIGURATION", "PINNING", 
            "PIN FUNCTIONS", "TERMINAL ASSIGNMENTS", "CONNECTION DIAGRAM",
            "TOP VIEW", "PINOUT", "PIN DEFINITIONS", 
            "LOGIC DIAGRAM", "FUNCTIONAL DIAGRAM" 
        ]

        for page_idx in range(len(doc)):
            page_text = doc[page_idx].get_text().upper()
            
            # Skip Table of Contents pages
            if "TABLE OF CONTENTS" in page_text or "CONTENTS" in page_text:
                continue 
                
            if any(keyword in page_text for keyword in search_keywords):
                target_page_num = page_idx
                print(f"[Tool] Pin headers matched on page {page_idx + 1}")
                break
        
        # Fallback to page 2 if no explicit strings are matched in text indices
        if target_page_num == -1 and len(doc) > 1:
            print("[Tool] Pin headers not matched in metadata stream. Defaulting to page 2 image capture...")
            target_page_num = 1

        # 2. Render target page to high-res image
        target_page = doc[target_page_num]
        pix = target_page.get_pixmap(dpi=150) 

        # Load the raw PyMuPDF bytes into PIL
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # Convert to Grayscale
        img = img.convert('L')
            
        # Restrict to a safer, higher-resolution bounding box using LANCZOS
        img.thumbnail((1280, 1280), Image.Resampling.LANCZOS) 
        
        # Save to a memory buffer as a compressed JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85) 
        img_bytes = buffer.getvalue()
        
        # Encode out to Base64 stream format
        b64_image = base64.b64encode(img_bytes).decode('utf-8')
        doc.close()

    except Exception as e:
        return f"PyMuPDF Vision Capture Failure: Failed to render visual layout page due to: {str(e)}"

    print(f"[Tool] Frame rendering successful. Dispatching multimodal payload to Gemma Vision...")
    print(f"[Debug] Sending payload size: {len(b64_image)} characters. Waiting for Ollama...")

    # Dynamically load the vision logic from the skills folder
    skills_dir = Path(r"C:\Path_skills_md_file")
    
    vision_prompt = load_markdown_directory(
        skills_dir, 
        target_mpn=target_mpn, 
        target_package=target_package
    )

    # Construct standard LangChain Multimodal structure
    message = HumanMessage(
        content=[
            {"type": "text", "text": vision_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64_image}"}
            }
        ]
    )

    # Execute direct vision logic loop pass through multimodal model
    response = llm.invoke([message])
    return response.content

@tool
def save_pinout_to_db(part_number: str, pin_assignments: any) -> str:
    '''Saves the entire extracted pinout configuration as a clean, standardized JSON array 
    blob directly into a single column inside the 'master_components' table.'''

    print(f"[Tool] Agent is attempting to save hybrid JSON data for {part_number} to SQLite database ({db_path}).....")
    
    if isinstance(pin_assignments, str):
        try:
            parsed_pins = json.loads(pin_assignments)
        except Exception:
            try:
                cleaned_str = pin_assignments.strip().strip("`").replace("json\n", "")
                parsed_pins = json.loads(cleaned_str)
            except Exception as parse_err:
                return f"Schema Error: pin_assignments string couldn't be parsed as valid JSON: {str(parse_err)}"
    else:
        parsed_pins = pin_assignments

    if not isinstance(parsed_pins, list):
        return f"Schema Error: Expected pin_assignments data layout to result in a list format, but received {type(parsed_pins)}"

    cleaned_pins_list = []
    for pin_info in parsed_pins:
        if not isinstance(pin_info, dict):
            continue
        
        p_num = pin_info.get('pin_number') or pin_info.get('pin')
        p_name = pin_info.get('pin_name') or pin_info.get('name') or pin_info.get('pin_function')
        p_func = pin_info.get('description') or pin_info.get('pin_function') or ""
        
        if p_num is not None and p_name is not None:
            cleaned_pins_list.append({
                "pin_number": str(p_num),
                "pin_name": str(p_name),
                "pin_function": str(p_func)
            })

    json_blob = json.dumps(cleaned_pins_list, indent=2)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE master_components 
            SET pin_assignments = ?
            WHERE REPLACE(REPLACE(REPLACE(UPPER(mpn), ',', ''), '-', ''), ' ', '') = ?;
        ''', (json_blob, normalize_mpn(part_number)))
            
        conn.commit()
        conn.close()
        return f"Success: Cleanly saved formatted JSON array mapping ({len(cleaned_pins_list)} pins) inside 'master_components' for {part_number}."
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Database Pipeline Error: {str(e)}"
    
# ==========================================
# AGENT SETUP & EXECUTION
# ==========================================

def custome_agent(model, tools, system_prompt: str, debug: bool = False):
    if debug:
        print("[DEBUG] Initializing Agent with tools:", [t.name for t in tools])

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )

if __name__ == '__main__':
    tools = [read_datasheet, save_pinout_to_db]

    # Dynamically load system instructions instead of hardcoding
    system_prompt = build_system_prompt()

    agent = custome_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        debug=True
    )

    pdf_folder = Path(r"C:\Users\Muhammad Syafiq\Desktop\LangChain\ICs Logic Gate Datasheet")

    for pdf_file in pdf_folder.glob("*.pdf"):
        pdf_filename = str(pdf_file)
        target_mpn = pdf_file.stem.upper()
        
        target_package = "Unknown Package"
        already_processed = False
        
        # --- DB CONTEXT LAYER ---
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT mpn, specs, pin_assignments FROM master_components;")
            all_rows = cursor.fetchall() 
            conn.close()

            normalized_file_mpn = normalize_mpn(target_mpn)
            row = None
            
            for db_mpn, specs, pins in all_rows:
                if normalize_mpn(db_mpn) == normalized_file_mpn:
                    row = (specs, pins)
                    break
            
            if row:
                specs_json_str, pin_data = row
                
                if specs_json_str:
                    try:
                        specs_dict = json.loads(specs_json_str)
                        supplier_pkg = specs_dict.get("Supplier Device Package", "")
                        case_pkg = specs_dict.get("Package / Case", "")
                        target_package = f"{supplier_pkg} | {case_pkg}".strip(" | ")
                    except Exception:
                        pass
                
                if pin_data and pin_data.strip() != "" and pin_data.strip() != "[]":
                    already_processed = True
            else:
                print(f"[Warning] MPN '{target_mpn}' was not found in the master_components table. Skipping file.")
                continue
                
        except Exception as e:
            print(f"[Warning] Database pre-check error: {str(e)}")

        print(f"\n{'#'*80}")
        print(f"Checking Cache Status for: {target_mpn}")
        print(f"Combined Target Package Profile from DB: {target_package}")
        print(f"{'#'*80}")

        if already_processed:
            print(f"--> [SKIP] Pin assignment data already exists for {target_mpn}. Skipping LLM process.\n")
            continue

        print(f"\nStarting agent mission for: {pdf_file.name}")

        user_message = (
            f"Extract the pinout for {pdf_filename}. "
            f"Crucially, only extract the pin assignment matching the package profile variations: '{target_package}' "
            f"and matching the part number/MPN: '{target_mpn}'. "
            f"Save the results to the DB."
        )

        result = agent.invoke({"messages": [("user", user_message)]})

        print("\n" + "="*50)
        print(f"STEP BY STEP PROCESS FOR {pdf_file.name}:")
        print("="*50)

        for msg in result["messages"]:
            print(f"\n--- {msg.__class__.__name__} ---")
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"DECISION: Calling Tools -> {msg.tool_calls}")
            if msg.content:
                content_preview = msg.content[:800] + "\n....[CONTENT TRUNCATED FOR READIBILITY]...." if len(msg.content) > 800 else msg.content
                print(f"CONTENT: {content_preview}")

        print("\n" + "="*70)
        print(f"========== FINAL REPORT FOR {pdf_file.name} ==========")
        print("="*70)
        print(result["messages"][-1].content)

        print(f"Cooling down and flushing VRAM for {COOL_DOWN_TIME} seconds...")
        time.sleep(COOL_DOWN_TIME)
