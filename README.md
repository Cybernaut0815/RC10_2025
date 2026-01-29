# **RC 10 teaching repo**



---
### University College London | 2025 | Tutor: Christoph Geiger

The the skill module repo for programming basics on procedural algorithms and AI usage for automated modular building generation.


## **Setup: Creating a Virtual Environment in Visual Studio Code**
---

### Step 1: Open the Project in VS Code
1. Open Visual Studio Code
2. Go to **File** → **Open Folder** and select this project folder

### Step 2: Open the Terminal
- Press `` Ctrl + ` `` (backtick) or go to **Terminal** → **New Terminal**
- This opens a terminal at the bottom of VS Code

### Step 3: Create the Virtual Environment
In the terminal, run:
```bash
python -m venv venv
```
This creates a folder called `venv` in your project directory.

### Step 4: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You'll know it's activated when you see `(venv)` at the beginning of your terminal prompt.

### Step 5: Install Dependencies
With the virtual environment activated, install the required packages:
```bash
pip install -r requirements.txt
```

### Step 6: Select the Python Interpreter in VS Code
1. Press `` Ctrl + Shift + P `` to open the command palette
2. Type "Python: Select Interpreter"
3. Choose the interpreter that shows `.\venv\Scripts\python.exe` (or `./venv/bin/python` on macOS/Linux)

### Tips:
- **Always activate the venv** before running Python scripts or installing packages
- VS Code will remember your interpreter choice for this workspace
- The `venv` folder is already in `.gitignore`, so it won't be committed to git


## **Lesson 1: Basics for python in Rhino**
---

- Theory: Basic introduction into Deep Learning and Machine Learning
- Setting up the environment and installing software
- Basic data types
- Loops and arrays
- Implementation of an array based random-walk

## **Lesson 2: Working with data structures and voxels - Arrays, Fields, Tensors**
---

- Theory: Pixels, Voxels, Arrays and Tensors
- More in depth introduction to using multidimensional arrays
- Game of live
- Basic Wave Function Collapse algorithm

## **Lesson 3: LLM & MCP interaction with architectural voxel data - connectivity graphs & analytics**
---

continue here...

- Theory: Basics in LLMs usage and graph data
- Connectivity graphs
- Basic analytics
- RAG (retrieval augmented Generation) on a large dataset


## **Lesson 4: Training a basic diffusion model**
---

- MCP connection with a dataset and to Voxels in Rhino   [Not implemented]
- Theory: basics in diffusion models 
- Setting up the dataset  [Needs update]
- Creating a neural network  [Needs update]
- Training the model  [Needs update]
- Showing a result in Rhino  [Needs update]