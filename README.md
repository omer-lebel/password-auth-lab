# 🔐 Passwords Authentication Lab
todo add short explanation

## 🚀 Getting Started
### Clone (Download) the project:
```bash
git clone git@github.com:omer-lebel/password-auth-lab.git
```
### Setup Environment:
```bash
cd password-auth-lab
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
## Running
###  1. Turn on the server
edit the `config.json` as you wish ...
todo add here or somewhere explain about the config file 
```bash
cd password-auth-lab
python -m server.main --config=<path_to_config.json> --output=<outputdir>
```
* `--config` - Path to config JSON file (default: config.json)
* `--output` -  Output directory for database, logs, and config copy
###  2. Register the clients
```bash
python register/main.py
```

###  3. Run the attacker
```bash
cd attacker
python main.py --attack=<attack type>
```
* `--attacke` - the attack type:
  * `spray` - for spraying attack over all the users in `users.json`
  * `brute_force` - for brute force attack over the users in `some file`
  * `both`
Both of the attack using the dictionary password, and do up to 100,000 login 
###  4. Analyze with log analyzer
```bash
cd log_analayzer
python main.py --input=<attemp.jsonl>
```
* `--input` - path to **attempt.jsonl** file
* **output pdf** - will be generated in the same dir as the input file