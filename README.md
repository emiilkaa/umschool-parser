# Umschool Parser
This parser can save direct links to the lessons' videos, homework and extra materials of the course (the course must already be purchased).

Installation
---
The parser itself doesn't require installation, but it needs some dependencies to work. You have to install:

1. Python 3.6 or above;
2. [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) — the program directory (`C:\Program Files\wkhtmltopdf\bin` by default) must be in the PATH ([Windows](https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/), [Linux](https://linuxize.com/post/how-to-add-directory-to-path-in-linux/));
3. Some Python packages required for the parser to work. You can see the list of these packages in the `requirements.txt` file. You can install them using the `pip install -r requirements.txt` command in Terminal or Command Prompt (running Terminal or Command Prompt in the same directory as the `requirements.txt` file).

Usage
---
After the installation of all the dependencies, you can use the parser.

Just run the `main.py` file, enter your username (or email) and password to enter the Umschool website, and also enter the link to the course (like this: `https://umschool.net/course/989/lessons/`) — after program execution there'll be the course's directory with all the materials.