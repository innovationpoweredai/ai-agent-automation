# AI Agent Automation (Experimental)
This project is intentionally incomplete. If you enjoy understanding systems by reconstructing missing logic, this repo is an invitation.
## Overview

This repository contains an **experimental AI-assisted automation agent** designed to execute user-defined tasks on a computer using a **closed-loop perception–action cycle**.

The system follows a simple but powerful idea:

> **Prompt → Plan → Execute → Observe (Screenshot) → Decide → Repeat**

The agent offloads reasoning and interpretation to external AI APIs while keeping execution local, resulting in **low system load** and a modular architecture.

---

## Key Concepts

* AI-assisted task decomposition
* Step-by-step execution (atomic actions)
* Screenshot-based feedback after every action
* Local automation with external reasoning
* Multi-agent control (experimental UI included)

---

## ⚠️ Important Note (Read This)

This repository represents a **preserved snapshot of an experimental system**.

Some components, glue logic, or context may be **missing or incomplete**.

This is **intentional**.

The project is published in this state to:

* Preserve the core ideas
* Encourage **reverse engineering**
* Allow contributors to explore, extend, or reinterpret the system

If you enjoy understanding systems by reading code and reconstructing intent,
**this project is for you**.

---

## How It Works (High Level)

1. A user provides a high-level prompt.
2. The agent breaks the prompt into executable steps using AI assistance.
3. Each step is executed locally (mouse, keyboard, filesystem, etc.).
4. After each step, a screenshot is captured.
5. The screenshot is analyzed to determine the next action.
6. The loop continues until completion or a safety limit is reached.

---

## Project Status

* 🧪 Experimental
* 🧩 Partially incomplete by design
* 🛠 Open to interpretation and extension
* ❗ Not guaranteed to be actively maintained

---

## Contributing

Contributions are welcome.

You are encouraged to:

* Reverse engineer missing pieces
* Improve robustness and safety
* Refactor or redesign components
* Add documentation or diagrams
* Experiment freely

Please keep pull requests focused and small.

---

## Disclaimer

This project is for **educational and experimental purposes only**.
It should not be used for sensitive, destructive, or unsupervised automation.

---

## Author

**Preyan Mondal**
Independent builder and experimenter.

Built as an exploration of what is possible when **AI tools are combined with basic system understanding and disciplined experimentation**.

---

## Final Note

This repository is not a tutorial.
It is not a product.

It is **evidence**.

---

## License

MIT License






User Prompt
   ↓
Local Flask Server (Windows)
   ↓
AI Reasoning (API)
   ↓
Local Execution (pyautogui, subprocess)
   ↓
Screenshot
   ↓
Next Step
