# qa-practice-swaglabs
This repo is a used for teaching and demoing basic test automation using Selenium, and Python 3 as the binding Language.
For this demo we are using Swag Labs as our test website.

# Set-up and installation
The first step is to create your individual lightweight virtual environment. Some computers like Macs often have
pre-installed Python interpreters but as a good practice you need to have your own lightweight environment that can be
used by your project/s. You can also have multiple virtual environments for different purposes,
that you can assign to different projects.

**What is a virtual environment? A virtual environment is (amongst other things):**

- Used to contain a specific Python interpreter and software libraries and binaries which are needed to support
a project (library or application). These are by default isolated from software in other virtual environments 
and Python interpreters and libraries installed in the operating system.
- Contained in a directory, conventionally named .venv or venv in the project directory, or under a container directory
for lots of virtual environments, such as ~/.virtualenvs.
- Not checked into the source control systems such as Git.
- Considered as disposable – it should be simple to delete and recreate it from scratch. You don’t place any project code in the environment.
- Not considered as movable or copyable – you just recreate the same environment in the target location.

**Virtual Environment Setup for macOS (Python & Testing Tools):**
1. Check if Homebrew is installed. Run in Terminal: brew --version
If not installed, run: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install the latest Python interpreter. Run: brew install python
3. Verify the Python version. Run: python3 --version
4. Confirm the Python installation path. Run: which python3
Expected output: /opt/homebrew/bin/python3
5. Navigate to your project directory. Run: mkdir my_project && cd my_project
6. Create a virtual environment. Run: python3 -m venv [desired venv name]
7. Activate the virtual environment. Run: source venv/bin/activate
8. Upgrade pip (recommended). Run: pip install --upgrade pip
9. Install Selenium. Run: pip install selenium
10. Install Pytest. Run: pip install pytest
11. (Optional) Install extra Pytest plugins. Run: pip install pytest-base-url pytest-html
12. Verify installed packages. Run: pip list
Confirm selenium, pytest, pytest-base-url, and pytest-html are listed.

**Python Virtual Environment Setup for Windows:**
⚠️ Assumes Python is installed via python.org or Microsoft Store. If not, download and install Python first.
📌 Step-by-Step (for Command Prompt or PowerShell)
1. Check Python version
python --version

2. Check pip version
pip --version

3. (Optional) Upgrade pip
python -m pip install --upgrade pip

4. Create your project folder and navigate into it
mkdir my_project
cd my_project

5. Create virtual environment (replace "venv" with your folder name if needed)
python -m venv venv

6. Activate the virtual environment
venv\Scripts\activate

7. Confirm you're in the virtual environment
where python
python --version

8. Install Selenium
pip install selenium

9. Install PyTest
pip install pytest

10. (Optional) Install PyTest plugins
pip install pytest-base-url pytest-html

11. Verify installed packages
pip list

**Clone GitHub Repo & Set Up Python Virtual Environment (macOS/Linux)**
1. Get the GitHub repo URL (replace with your actual URL)
Example: https://github.com/yourusername/your-repo-name.git

2. Navigate to the folder where you want to clone the project
cd ~/Projects

3. Clone the repository
git clone https://github.com/yourusername/your-repo-name.git

4. Navigate into the cloned repo
cd your-repo-name

5. (Optional) Create a virtual environment if you haven't yet
python3 -m venv venv

6. Activate the virtual environment
source venv/bin/activate

7. Verify installed packages
pip list

8. Generate requirements.txt
pip freeze > requirements.txt

9. Open your IDE (e.g., PyCharm) and set interpreter to use: ./venv/bin/python

**Clone GitHub Repo & Set Up Python Virtual Environment (Windows CMD)**
1. Get the GitHub repo URL (replace with your actual URL)
Example: https://github.com/yourusername/your-repo-name.git

2. Navigate to the folder where you want to clone the project
cd %USERPROFILE%\Documents

3. Clone the repository
git clone https://github.com/yourusername/your-repo-name.git

4. Navigate into the cloned repo
cd your-repo-name

5. (Optional) Create a virtual environment if not yet created
python -m venv [desired venv name]

6. Activate the virtual environment
venv\Scripts\activate

7. Verify installed packages
pip list

8. Generate requirements.txt
pip freeze > requirements.txt

9. Open your IDE (e.g., PyCharm) and set the interpreter to: venv\Scripts\python.exe

## Standalone Demo
The file test_standalone_demo.py contains a basic standalone file containing a few tests that use some of the common basic
Selenium methods. It also has comments that explain the steps used. This will make you familiarized and get started with automating tests.


