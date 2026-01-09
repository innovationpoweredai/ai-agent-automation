# main.py

import os
import base64
import json
import time
from datetime import datetime
import requests
import asyncio
import sys
import re 

# Import the tool functions defined in tools.py
from tools import take_screenshot, type_text, click, hotkey, open_application, create_folder, write_file, read_file, current_datetime, delay, click_predefined_location

# --- Define agent-specific file paths ---
# These will now be dynamically set based on the agent_id
PROMPT_FILE = ""
AGENT_LOG_FILE = ""
AGENT_STATUS_FILE = ""

# --- Custom Stop Tool Function ---
def stop_agent() -> str:
    """
    Signals the agent to gracefully stop its execution, indicating task completion.
    This writes 'finished' to the status file and can be used by the LLM.
    """
    print("\n[AGENT STOP] LLM requested agent to stop. Task considered complete.")
    # Use the write_file function from tools.py to ensure the status file is correctly updated.
    write_file(AGENT_STATUS_FILE, "finished") 
    return "✅ Agent received stop signal. Task completed."

# --- IMPORTANT: Configure your LLM API call ---
API_KEY = os.getenv("GEMINI_API_KEY", "") # <-- REPLACE THIS PLACEHOLDER WITH YOUR ACTUAL API KEY!

# --- Initial API Key Check ---
if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("ERROR: API_KEY is not configured in main.py. Please replace 'YOUR_GEMINI_API_KEY_HERE' with your actual Gemini API key from aistudio.google.com.")
    sys.exit(1)

# --- LLM Interaction Function ---
async def call_llm_with_vision(prompt: str, image_base64: str) -> str:
    print(f"\n[LLM Call] Sending prompt to LLM...")
    contents = [{"role": "user", "parts": [{"text": prompt}, {"inlineData": {"mimeType": "image/png", "data": image_base64}}]}]
    payload = {"contents": contents}
    # --- Using gemini-1.5-pro for enhanced reasoning ---
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}" 
    try:
        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload)
        response.raise_for_status()
        result = response.json()
        # print(f"[LLM Debug] Full API Response JSON: {json.dumps(result, indent=2)}") # Uncomment for full debug
        if result.get("candidates") and result["candidates"] and len(result["candidates"]) > 0 and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts") and len(result["candidates"][0]["content"]["parts"]) > 0:
            llm_response = result["candidates"][0]["content"]["parts"][0]["text"].strip() 
            
            # Extracting the tool call, assuming it's the last line or clearly identifiable
            tool_call_start_markers = (
                "open_application(", "type_text(", "hotkey(", "click(",
                "take_screenshot(", "write_file(", "read_file(", "stop_agent(", "delay(",
                "click_predefined_location(" 
            )
            
            found_tool_call = None
            # Iterate lines in reverse to find the last tool call, or parse for a specific format
            lines = llm_response.split('\n')
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line.startswith(tool_call_start_markers):
                    found_tool_call = stripped_line
                    break
            
            if found_tool_call:
                print(f"[LLM Response - Cleaned Tool Call]:\n{found_tool_call}")
                return found_tool_call
            else:
                print(f"[LLM Response - Warning: No explicit tool call found, returning original response]:\n{llm_response}")
                return llm_response

        elif result.get("promptFeedback"):
            safety_ratings = result["promptFeedback"].get("safetyRatings", [])
            block_reason = result["promptFeedback"].get("blockReason", "Unknown")
            print(f"[LLM Safety Block] Prompt or image blocked due to: {block_reason}")
            for rating in safety_ratings:
                print(f"  Category: {rating.get('category', 'N/A')}, Probability: {rating.get('probability', 'N/A')}")
            return f"ERROR: LLM input blocked by safety filters. Reason: {block_reason}. Check logs for details."
        else:
            print("[LLM Error]: Unexpected response structure or no content (no candidates and no promptFeedback).")
            return "ERROR: LLM returned no valid content or identifiable error."
    except requests.exceptions.RequestException as e:
        print(f"[LLM Error]: Network or API request failed: {e}")
        return f"ERROR: API call failed: {e}"
    except json.JSONDecodeError as e:
        print(f"[LLM Error]: Failed to decode JSON response: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
        return f"ERROR: Invalid JSON response: {e}"
    except Exception as e:
        print(f"[LLM Error]: An unexpected error occurred during API call: {e}")
        return f"ERROR: An unexpected error occurred during API call: {e}"

# --- Tool Execution Logic (UNSAFE for production - for prototype demonstration only) ---
def execute_tool_call(tool_call_string: str) -> str:
    print(f"[Tool Usage] Executing tool: {tool_call_string}") # Clearer tool usage indication
    try:
        allowed_tools = {
            "create_folder": create_folder, "write_file": write_file, "read_file": read_file,
            "open_application": open_application, "click": click, "type_text": type_text,
            "hotkey": hotkey, "take_screenshot": take_screenshot, "current_datetime": current_datetime,
            "time": time, "stop_agent": stop_agent, "delay": delay, 
            "click_predefined_location": click_predefined_location, 
        }
        result = eval(tool_call_string, {"__builtins__": None}, allowed_tools)
        return f"[Tool Success] {result}"
    except NameError:
        return f"[Tool Error] Unknown tool function: '{tool_call_string}'. Function not found or not in allowed tools."
    except SyntaxError:
        return f"[Tool Error] Invalid Python syntax in tool call: '{tool_call_string}'."
    except Exception as e:
        print(f"[Tool Error] Failed to execute tool '{tool_call_string}': {e}")
        return f"[Tool Error] Failed to execute tool '{tool_call_string}': {e}"

# --- Main AI Agent Loop ---
async def run_agent_prototype(target_prompt: str, agent_id: str):
    global PROMPT_FILE, AGENT_LOG_FILE, AGENT_STATUS_FILE 

    # Set agent-specific file paths
    PROMPT_FILE = os.path.join(os.path.dirname(__file__), f"prompt_{agent_id}.txt")
    AGENT_LOG_FILE = os.path.join(os.path.dirname(__file__), f"agent_log_{agent_id}.txt")
    AGENT_STATUS_FILE = os.path.join(os.path.dirname(__file__), f"agent_status_{agent_id}.txt")

    original_stdout = sys.stdout
    try:
        with open(AGENT_LOG_FILE, "w", encoding="utf-8") as f:
            sys.stdout = f 
            write_file(AGENT_STATUS_FILE, "running")
            print(f"--- Starting AI Agent Prototype ({agent_id}) ---")
            print(f"Overall Goal: {target_prompt}")

            # Ensure necessary base directories exist (agent-specific and common)
            agent_screenshots_dir = os.path.join(os.path.dirname(__file__), f"agent_screenshots_{agent_id}")
            print(create_folder(agent_screenshots_dir))
            
            # Common F: paths
            notes_dir = os.path.join(AGENT_DIR, "notes")
            print(create_folder(notes_dir))
            data_dir = os.path.join(AGENT_DIR, "data")
            print(create_folder(data_dir))
            project_reports_dir = os.path.join(data_dir, "project_reports")
            print(create_folder(project_reports_dir))
            documents_dir = os.path.join(AGENT_DIR, "documents")
            print(create_folder(documents_dir))
            logs_dir = os.path.join(AGENT_DIR, "logs")
            print(create_folder(logs_dir))
            web_content_dir = os.path.join(AGENT_DIR, "web_content")
            print(create_folder(web_content_dir))
            reports_dir = os.path.join(AGENT_DIR, "reports")
            print(create_folder(reports_dir))
            results_dir = os.path.join(AGENT_DIR, "results")
            print(create_folder(results_dir))
            facts_dir = os.path.join(AGENT_DIR, "facts")
            print(create_folder(facts_dir))
            screenshots_multi_tab_dir = os.path.join(AGENT_DIR, "screenshots_multi_tab")
            print(create_folder(screenshots_multi_tab_dir))
            config_dir = os.path.join(AGENT_DIR, "config")
            print(create_folder(config_dir))

            full_overall_goal = target_prompt 
            
            # Get available known locations dynamically for the prompt
            from tools import KNOWN_LOCATIONS 
            known_locations_list = ", ".join([f"'{name}'" for name in KNOWN_LOCATIONS.keys()])
            
            llm_prompt_template = (
                f"Overall Goal: {full_overall_goal}\n"
                "Previous Actions and Results:\n{action_history_json}\n\n"
                "Examine the current screenshot. Based on the Overall Goal and past actions, "
                "determine the *single, most efficient next action* to progress. "
                "Your response MUST be ONLY a valid Python function call string from the available tools. "
                "Do NOT include any surrounding text, explanations, or markdown. "
                "For example: open_application(\"notepad.exe\") or click(123, 456).\n" 
                "\nValid Tool Call Examples:\n"
                r"open_application(r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')" "\n"
                r"type_text('example.com')" "\n"
                r"hotkey('enter')" "\n"
                r"hotkey('ctrl+a')" "\n"
                r"hotkey('ctrl+c')" "\n"
                r"hotkey('ctrl+v')" "\n"
                r"hotkey('ctrl+t')" "\n"
                r"hotkey('ctrl+tab')" "\n"
                r"hotkey('alt', 'f4')" "\n"
                r"click(500, 300)" "\n"
                r"click_predefined_location('whatsapp_chat_1')" "\n" 
                f"take_screenshot(r'{agent_screenshots_dir}\\specific_screenshot.png')" "\n"
                r"delay(5) # Example: Pause for 5 seconds." "\n"
                r"stop_agent() # IMPORTANT: Call this when the Overall Goal is FULLY and SAFELY achieved." "\n" 
                f"\n--- AVAILABLE PREDEFINED LOCATIONS ---"
                f"\nUse click_predefined_location('LOCATION_NAME') for precise clicks. Available names: {known_locations_list}\n" 
                "\n--- APPLICATION LAUNCH EXAMPLES ---"
                r"open_application(r'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe')" "\n"
                r"open_application(r'C:\\Windows\\System32\\notepad.exe')" "\n"
                r"open_application(r'C:\\Windows\\System32\\calc.exe')" "\n"
                r"open_application(r'C:\\Users\\<YourUser>\\AppData\\Local\\Microsoft\\WindowsApps\\WhatsApp.exe') # REPLACE <YourUser> with your actual Windows username. Verify this path first!" "\n"
                r"open_application(r'C:\\Program Files\\DeepSeekAI\\DeepSeekAI.exe') # Verify this path for DeepSeek AI first!" "\n"
                r"open_application(r'C:\\Program Files\\AnotherApp\\AnotherApp.exe') # Add any other apps here after verifying their exact paths." "\n"
                
                "\n\n--- CRITICAL INSTRUCTIONS FOR SEQUENCING ---"
                "\n1. If you just typed text into an address bar or search bar, you MUST follow it with hotkey('enter') to submit. Do NOT click randomly after typing into a text field if the goal is to submit that text."
                "\n2. After pressing 'enter' (e.g., after navigating to a URL or submitting a search query), you MUST wait a moment for the new page to load. Then, the *next and most critical action* should be to take the requested screenshot *of the loaded page or search results* if the goal involves it."
                "\n3. Focus on completing each major step of the Overall Goal in sequence. Do not skip or add irrelevant actions. Break down complex tasks into smaller, logical tool calls."
                "\n4. **CRITICAL: When the Overall Goal is FULLY AND SUCCESSFULLY COMPLETED, your absolute final action MUST be `stop_agent()`. Do NOT issue any other commands after `stop_agent()`.**" 
                "\n5. Pay attention to the exact details requested in the Overall Goal. Use raw strings (e.g., r'C:\\path\\file.txt') for all paths and ensure double backslashes for all Windows paths within strings if you need to *type* a path, but REMEMBER: You are NOT allowed to save files unless explicitly instructed otherwise."
                "\n6. If a previous action resulted in an error, analyze the error message and the current screenshot to determine the appropriate corrective action. If an action fails and you are stuck, try to restart the problematic part of the task."
                "\n7. When performing copy/paste or selecting all, ensure the correct application (e.g., browser or Notepad) is in focus."
                "\n8. To open a web browser, use `open_application(r'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe')` if the task involves web navigation. Do NOT open a browser if it is not required by the overall goal."
                "\n9. **DIRECT URL NAVIGATION:** If the Overall Goal provides a complete URL (starting with 'http://' or 'https://'), you MUST type that full URL directly into the browser's address bar using `type_text('FULL_URL_HERE')` and then immediately press Enter using `hotkey('enter')`. Do NOT try to navigate to a search engine first or click any search results if a direct URL is given."
                "\n10. **GENERAL WEBSITE NAVIGATION (Named Sites):** If the Overall Goal requests navigating to a named website (e.g., 'Instagram', 'Facebook', 'YouTube', 'Wikipedia') without providing a full URL, you MUST first ensure a web browser is open. Then, type the standard domain name (e.g., 'instagram.com', 'facebook.com', 'youtube.com', 'wikipedia.org') into the browser's address bar using `type_text('DOMAIN_NAME_HERE.com')` and immediately press Enter using `hotkey('enter')`. This ensures reliable navigation to common sites."
                "\n11. **TYPING IN INPUT FIELDS (Reliable Method):** When typing into *any* input field (search box, message box, address bar, etc.): **First, you MUST click the input field using `click(x,y)` or `click_predefined_location('NAME')` to give it focus.** Then use `type_text('Your message here')`. After typing, if the text is meant to be submitted (e.g., search query, form submission, message send), you MUST follow with `hotkey('enter')`. If the input field is *not* focused after clicking, try using `hotkey('tab')` one or more times to cycle through interactive elements until the input field is highlighted/focused. As a last resort for web browser address bars, use `hotkey('ctrl', 'l')` to focus the address bar, then `type_text('Your URL or search query')`. Always follow `type_text` with `hotkey('enter')` if it's meant to submit a query or send a message. **After typing, consider adding a small delay like `delay(0.5)` if the text doesn't appear immediately.**" 
                "\n12. **IMPORTANT:** You are NOT allowed to use `write_file()` or `hotkey('ctrl+s')` unless the Overall Goal explicitly asks you to save a file. If the task does not mention saving, avoid any save-related actions and proceed to the next step or `stop_agent()` once the main goal is achieved."
                "\n13. **DELAYING ACTIONS:** If you need to wait for an application to fully load, a process to complete, or for a specific period before the next action, use `delay(seconds)`. For example, `delay(3)` will pause for 3 seconds. Use appropriate delay times (e.g., 2-5 seconds) when opening new applications or navigating to new web pages."
                "\n14. **RELIABLE CLICKS (New):** For critical, frequently used click locations, prioritize `click_predefined_location('LOCATION_NAME')` over `click(x,y)` if a suitable `LOCATION_NAME` is available in the `--- AVAILABLE PREDEFINED LOCATIONS ---` list. This is more robust." 
                "\n15. **TEXT VISIBILITY TROUBLESHOOTING:** If text you have typed appears transparent or doesn't show up, it means the input field did not fully register the input. The solution is usually to ensure you **first click the input field (or use `hotkey('tab')` to focus it) then `type_text()`, and then add a `delay(0.5)` or `delay(1)` immediately after `type_text()`** to allow the application to render the input. Review the screenshot after typing to confirm visibility." 
                "\n16. **AI REASONING FORMAT:** Your response should include the following sections before the final tool call, mimicking a step-by-step reasoning process:"
                "\nShort term goal: [Describe the immediate goal for this step]"
                "\nWhat I see: [Describe relevant observations from the screenshot/context]"
                "\nReflection: [Explain your reasoning for the chosen action]"
                "\nAction: [The single tool call]"
            )

            action_history = []
            
            print("\n--- CONFIRMATION: Initializing Agent for LLM Guidance ---")
            
            for i in range(1, 40): # Max 39 LLM-guided iterations
                print(f"\n--- Agent LLM Guided Iteration {i} (Overall Action {i+1}) ---")
                current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Screenshot paths now include agent_id
                screenshot_path = os.path.join(agent_screenshots_dir, f"intermediate_screen_{agent_id}_{current_timestamp}.png") 

                print(f"[Perception] Taking screenshot: {screenshot_path}")
                if i == 1:
                    time.sleep(2) 
                screenshot_result = take_screenshot(screenshot_path)
                print(screenshot_result)

                if "✅" not in screenshot_result:
                    print("Failed to take screenshot. Exiting agent loop as perception failed.")
                    break

                # Check if stop signal received from status file
                status_content = read_file(AGENT_STATUS_FILE)
                if "finished" in status_content:
                    print(f"\n[AGENT SIGNAL] Received 'finished' signal from {AGENT_STATUS_FILE}. Stopping agent loop.")
                    break # Break the main loop and gracefully exit

                try:
                    with open(screenshot_path, "rb") as f:
                        image_bytes = f.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                except Exception as e:
                    print(f"Error encoding screenshot to base64: {e}. Exiting agent loop.")
                    break

                llm_prompt_to_send = llm_prompt_template.format(action_history_json=json.dumps(action_history, indent=2))
                
                # Print the AI's reasoning sections
                print("\n[Reasoning] LLM Input (excerpt, including reasoning format instructions):\n")
                prompt_lines = llm_prompt_to_send.splitlines()
                # Find the start of the reasoning format instructions to print them
                reasoning_start_index = -1
                for idx, line in enumerate(prompt_lines):
                    if "AI REASONING FORMAT:" in line:
                        reasoning_start_index = idx
                        break
                
                if reasoning_start_index != -1:
                    print("\n".join(prompt_lines[reasoning_start_index:]))
                else:
                    # Fallback if the marker isn't found (shouldn't happen with the new template)
                    print("\n".join(prompt_lines[-20:])) # Print last 20 lines as a fallback excerpt
                print("\n--- LLM Input End ---\n")


                llm_response_full = await call_llm_with_vision(llm_prompt_to_send, image_base64)

                # Parse the LLM's full response to extract reasoning and the final action
                reasoning_sections = {}
                current_section = None
                tool_call = ""
                
                for line in llm_response_full.split('\n'):
                    line = line.strip()
                    if line.startswith("Short term goal:"):
                        current_section = "Short term goal"
                        reasoning_sections[current_section] = line.replace("Short term goal:", "").strip()
                    elif line.startswith("What I see:"):
                        current_section = "What I see"
                        reasoning_sections[current_section] = line.replace("What I see:", "").strip()
                    elif line.startswith("Reflection:"):
                        current_section = "Reflection"
                        reasoning_sections[current_section] = line.replace("Reflection:", "").strip()
                    elif line.startswith("Action:"):
                        current_section = "Action"
                        tool_call = line.replace("Action:", "").strip()
                    elif current_section and not tool_call: # If we are in a reasoning section and haven't found the tool call yet
                        reasoning_sections[current_section] += " " + line.strip() # Append to current section
                
                # Print the extracted reasoning to the log
                print(f"\n[AI Reasoning Output]:")
                print(f"Short term goal: {reasoning_sections.get('Short term goal', 'N/A')}")
                print(f"What I see: {reasoning_sections.get('What I see', 'N/A')}")
                print(f"Reflection: {reasoning_sections.get('Reflection', 'N/A')}")
                print(f"Action: {tool_call}") # Print the extracted tool call here
                
                if not tool_call:
                    print(f"[Agent] LLM returned an error or invalid response (no valid tool call found): {llm_response_full}")
                    print("Exiting agent loop due to LLM response error.")
                    break
                
                if "stop_agent()" in tool_call:
                    print("\n[AGENT SIGNAL] LLM called 'stop_agent()'. Stopping agent loop early.")
                    tool_execution_result = execute_tool_call(tool_call)
                    print(tool_execution_result)
                    action_history.append({"tool_call": tool_call, "result": tool_execution_result, "timestamp": current_datetime()})
                    break # Break the main loop and gracefully exit

                time.sleep(1.5) 
                tool_execution_result = execute_tool_call(tool_call)
                print(tool_execution_result)
                action_history.append({"tool_call": tool_call, "result": tool_execution_result, "timestamp": current_datetime()})
                time.sleep(2)

            print("\n--- AI Agent Prototype Finished ---")
            current_status = read_file(AGENT_STATUS_FILE)
            if "running" in current_status:
                 write_file(AGENT_STATUS_FILE, "finished") 
            
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Agent loop encountered an unhandled exception: {e}")
        write_file(AGENT_STATUS_FILE, f"error: {e}")
    finally:
        sys.stdout = original_stdout

if __name__ == "__main__":
    # The agent_id will be passed as a command-line argument
    if len(sys.argv) > 1:
        agent_id_from_arg = sys.argv[1]
    else:
        # Default to 'default' if no agent_id is provided (for direct testing)
        agent_id_from_arg = "default"

    # Set global paths for this agent's run
    PROMPT_FILE = os.path.join(os.path.dirname(__file__), f"prompt_{agent_id_from_arg}.txt")
    AGENT_LOG_FILE = os.path.join(os.path.dirname(__file__), f"agent_log_{agent_id_from_arg}.txt")
    AGENT_STATUS_FILE = os.path.join(os.path.dirname(__file__), f"agent_status_{agent_id_from_arg}.txt")

    if os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                initial_prompt_from_file = f.read()
            print(f"Running agent '{agent_id_from_arg}' with prompt from {PROMPT_FILE}")
            asyncio.run(run_agent_prototype(initial_prompt_from_file, agent_id_from_arg))
        except Exception as e:
            print(f"Error reading prompt from file for agent '{agent_id_from_arg}': {e}. Exiting.")
            write_file(AGENT_STATUS_FILE, f"error: Could not read prompt file: {e}")
            sys.exit(1)
    else:
        default_prompt = (
            "Open Notepad. Type 'Hello World!' into Notepad. Close Notepad. Stop the agent."
        )
        print(f"No prompt file found for agent '{agent_id_from_arg}'. Using default prompt for direct run.")
        asyncio.run(run_agent_prototype(default_prompt, agent_id_from_arg))

