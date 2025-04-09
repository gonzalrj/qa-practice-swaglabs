# qa-practice-swaglabs
This repo is a used for teaching and demoing basic Selenium automation using Swag Labs website.

# Set-up and installation
The first step is to create your individual lightweight virtual environment. Some computers like Macs often have pre-installed Python interpreters but as a good practice you need to have your own lightweight environment that can be used by your project/s. You can also have multiple virtual environments for different purposes, that you can assign to different projects.

A virtual environment is (amongst other things):

- Used to contain a specific Python interpreter and software libraries and binaries which are needed to support a project (library or application). These are by default isolated from software in other virtual environments and Python interpreters and libraries installed in the operating system.
- Contained in a directory, conventionally named .venv or venv in the project directory, or under a container directory for lots of virtual environments, such as ~/.virtualenvs.
- Not checked into source control systems such as Git.
- Considered as disposable – it should be simple to delete and recreate it from scratch. You don’t place any project code in the environment.
- Not considered as movable or copyable – you just recreate the same environment in the target location.

Virtual Environment set-up for MacOS:
1. Check if Homebrew is installed in your machine. Via terminal run brew --version. If Homebrew is not yet installed, you can run /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install the latest Python interpreter by running brew install python.
3. Verify the Python version by running python3 --version. It should show the latest Python version.
4. Confirm your the path installed by running which python3. Expected output /opt/homebrew/bin/python3.
5. Move to the directory you want to create your virtual environment and run python3 -m venv venv-path-name.
6. Activate your environment by running source venv-path-name/bin/activate to start installing project dependencies.
7. Install Selenium by running pip install selenium.
8. Install PyTest by running pip install pytest.
9. Repeat the same steps for 2 optional packages: pytest-base-url and pytest-html.
10. Verify all installations by running pip list. Make sure both packages are shown from the list.

Cloning repository to local machine.
1. Get the GitHub repo URL.
2. Via Terminal, navigate to the folder you want to save a copy of your project locally.
3. Clone the repo by running git clone https://github.com/yourusername/your-repo-name.git (your GitHub repo URL).
4. Via Terminal, activate your venv by running source venv-path-name/bin/activate
5. Verify that your desired dependencies are captured by running pip list
6. Once confirmed, create a requirements.txt file from it by executing pip freeze > requirements.txt
7. The project can now be opened in your preferred IDE, in my case it is PyCharm. Make sure to use the created virtual environment for this project.


