Interactive Git Project Search Tool
===================================

Overview:
---------
A command-line tool to search and execute commands on git projects in a specified directory.

Features:
---------
- Real-time fuzzy search
- Navigate recent projects with Tab
- Execute custom commands on selected projects
- Maintains a history of opened projects

Installation:
-------------
1. Download the script:
    wget https://github.com/asidko/projects-search/raw/main/search.py

Usage:
------
Run the script with an optional command argument:
    python search.py 'command %F'

Examples:
---------
1. Open project in Visual Studio Code:
    python search.py 'code %F'

2. Open project in IntelliJ IDEA:
    python search.py 'idea %F'

Interactive Navigation:
-----------------------
- Type to search
- Tab: Cycle through recent projects
- Enter: Execute command or print project path
- Shift+Enter: Clear query
- Esc: Exit

Configuration:
--------------
- Default search depth: 2
- Default root directory: ~/projects
- History file: ~/.projects_history

Contributing:
-------------
Contributions are welcome! Submit a Pull Request.

License:
--------
MIT License