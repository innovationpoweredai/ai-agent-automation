#app.py
import os
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Define the base directory for the agent files
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Endpoint to serve the main HTML page ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Endpoint to set the prompt for a specific agent ---
@app.route('/set_prompt/<agent_id>', methods=['POST'])
def set_prompt(agent_id):
    prompt = request.form['prompt']
    prompt_file_path = os.path.join(AGENT_DIR, f"prompt_{agent_id}.txt")
    try:
        with open(prompt_file_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        return jsonify({"status": "success", "message": f"Prompt for Agent {agent_id} set successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to set prompt for Agent {agent_id}: {e}"})

# --- Endpoint to start a specific agent ---
@app.route('/start_agent/<agent_id>', methods=['POST'])
def start_agent(agent_id):
    agent_status_file = os.path.join(AGENT_DIR, f"agent_status_{agent_id}.txt")
    try:
        # Check if an agent process is already running for this ID
        # (A more robust solution would use PIDs or a dedicated process manager)
        if os.path.exists(agent_status_file) and read_agent_status(agent_id) == "running":
            return jsonify({"status": "error", "message": f"Agent {agent_id} is already running."})

        # Clear previous logs and status for a fresh start
        log_file_path = os.path.join(AGENT_DIR, f"agent_log_{agent_id}.txt")
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        if os.path.exists(agent_status_file):
            os.remove(agent_status_file)
        
        # Start main.py as a separate subprocess, passing the agent_id
        # Use 'start' to run it in a new window/process without blocking Flask
        subprocess.Popen(['python', 'main.py', agent_id], cwd=AGENT_DIR, shell=True)
        
        # Give it a moment to start and write status
        # time.sleep(1) # Removed as main.py has its own sleep at start
        
        return jsonify({"status": "success", "message": f"Agent {agent_id} started."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to start Agent {agent_id}: {e}"})

# --- Helper function to read agent status ---
def read_agent_status(agent_id):
    status_file = os.path.join(AGENT_DIR, f"agent_status_{agent_id}.txt")
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception:
            return "error reading status"
    return "stopped" # Default status if file doesn't exist

# --- Endpoint to get a specific agent's status ---
@app.route('/get_status/<agent_id>')
def get_status(agent_id):
    status = read_agent_status(agent_id)
    return jsonify({"status": status})

# --- Endpoint to get a specific agent's logs ---
@app.route('/get_logs/<agent_id>')
def get_logs(agent_id):
    log_file_path = os.path.join(AGENT_DIR, f"agent_log_{agent_id}.txt")
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                logs = f.read()
            return jsonify({"logs": logs})
        except Exception as e:
            return jsonify({"logs": f"Error reading logs: {e}"})
    return jsonify({"logs": "No agent logs yet."})

# --- Endpoint to stop a specific agent ---
@app.route('/stop_agent/<agent_id>', methods=['POST'])
def stop_agent(agent_id):
    # The 'stop_agent' command is handled by the agent itself through the LLM prompt.
    # For now, this just updates the status file to 'stopping' to signal.
    # A robust solution would involve sending a kill signal to the subprocess or using a shared state.
    status_file = os.path.join(AGENT_DIR, f"agent_status_{agent_id}.txt")
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write("stopping")
        return jsonify({"status": "success", "message": f"Stop signal sent to Agent {agent_id}."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to send stop signal to Agent {agent_id}: {e}"})


if __name__ == '__main__':
    # Ensure agent_screenshots directory exists for both agents or general default
    os.makedirs(os.path.join(AGENT_DIR, 'agent_screenshots_default'), exist_ok=True)
    os.makedirs(os.path.join(AGENT_DIR, 'agent_screenshots_agent1'), exist_ok=True)
    os.makedirs(os.path.join(AGENT_DIR, 'agent_screenshots_agent2'), exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0')

