# project_name
Descript project


## Installation & Setup
1. Clone the repository
```bash
# Clone this repository with git
git clone project_link

# Open the directory in terminal
cd Funday-Games-Example/
```

2. Create Virtual Environment & activate
```bash
uv venv

source .venv/bin/activate
```

3. Install requirements
```bash
# For Users
uv sync --no-dev --link-mode=copy

# For Devs
uv sync --link-mode=copy
```

4. Run the program
```bash
uv run funday_bundle
```


# Tools for the project

**Generating a requirements file**
```bash
uv pip compile pyproject.toml -o requirements.txt
```

**Install Program as development**
```bash
uv pip install -e .
```

**add new requirements in pyproject**
```bash
uv add <package_name>
```

**Building Program (demo not tested yet!)**
```bash
uv run pyinstaller --onefile --noconsole --windowed --collect-all pynput --icon "icon.ico" --name "funday_bundle" src/funday_bundle/main.py
```