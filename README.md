# 🔐 Passwords Authentication Lab

## 🚀 Getting Started 

### 1. Clone (Download) the project:
```bash
git clone git@github.com:omer-lebel/password-auth-lab.git
cd password-auth-lab
```
### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
python main.py
```

---

## 📦 Adding New Dependencies

### 1. Add to `requirements.in`
Edit your `requirements.in` file and add the new package:
```
requests
libs # new dependency
```

### 2. Recompile
This will regenerate the `requirements.txt` file:
```bash
pip-compile --upgrade requirements.in
```

### 3. Update Your Environment
```bash
pip install -r requirements.txt
```

> **⚠️ Note: To downgrade modules:**
> 1. Deactivate env if needed: `deactivate`
> 2. Delete old env: `rm -rf .venv`
> 3. Create new env: `python -m venv .venv`
> 4. Activate it: `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
> 5. Install pip-tools: `pip install pip-tools`
> 6. Edit `requirements.in` as needed (pin versions like `libs==1.2.3`)
> 7. Run step 2 and 3 (Recompile & reinstall)
---

## ⚙️ Git Cheat Sheet - basic workflow

### 1️⃣ Verify you are on the main branch
```bash
git branch 
```

### 2️⃣ Pull Changes to make sure you are updated
```bash
git pull
```

### 3️⃣ Create and move to a new branch
```bash
git checkout -b <branch-name>
```

### 4️⃣ Make Your Changes
Edit files in your project like normal.

### 5️⃣ Stage Your Changes 
Tell git which files to track:
```bash
git add <file-name>
```

### 6️⃣ Commit Your Changes (local save)
Save your changes to your local `.git` repository.
Do this frequently.
```bash
git commit -m "description msg"
```

### 7️⃣ Push Your Changes to remote
Do this at more significant checkpoints — after several commits or when you complete a piece of work.
```bash
git push
```