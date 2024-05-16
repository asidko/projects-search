import os
import curses
import sys
import subprocess
import heapq

# Configuration variables
DEFAULT_DEPTH = 2
DEFAULT_ROOT = os.path.expanduser('~/projects')
HISTORY_FILE = os.path.expanduser('~/.projects_history')

def find_git_projects(base_dir, depth):
    """Find all git projects up to a specified depth."""
    git_projects = []
    for root, dirs, _ in os.walk(base_dir):
        if '.git' in dirs:
            git_projects.append(root)
        # Limit the depth of the search
        current_depth = root[len(base_dir):].count(os.sep)
        if current_depth >= depth:
            del dirs[:]
    return git_projects

def fuzzy_match(query, string):
    """Check if the query is a fuzzy match for the string."""
    query = query.lower()
    string = string.lower()
    it = iter(string)
    return all(char in it for char in query)

def search_projects(projects, query):
    """Search projects by full path or project folder name."""
    if '/' in query:
        return [project for project in projects if fuzzy_match(query, project)]
    else:
        return [project for project in projects if fuzzy_match(query, os.path.basename(project))]

def get_last_modified_projects(projects, num_projects=3):
    """Get the last modified projects."""
    project_mod_times = [(os.path.getmtime(proj), proj) for proj in projects]
    last_modified_projects = heapq.nlargest(num_projects, project_mod_times)
    return [proj for _, proj in last_modified_projects]

def get_last_opened_projects(history_file, num_projects=3):
    """Get the last opened projects from the history file, avoiding duplicates."""
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            lines = file.read().splitlines()
        unique_lines = list(dict.fromkeys(lines))
        return unique_lines[-num_projects:]
    return []

def save_to_history(history_file, project_path):
    """Save the project path to the history file, avoiding duplicates."""
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            lines = file.read().splitlines()
        if project_path in lines:
            return
    with open(history_file, 'a') as file:
        file.write(project_path + '\n')

def display_projects(stdscr, label, projects, start_line, highlight=None):
    """Display projects in the terminal with optional highlight."""
    stdscr.addstr(start_line, 0, label)
    for idx, project in enumerate(projects, start=start_line + 1):
        prefix = '*' if project == highlight else ' '
        stdscr.addstr(idx, 0, f"{prefix} {os.path.basename(project)}")

def update_screen(stdscr, query, last_modified, last_opened, matches, selected_project, highlighted_project):
    """Update the screen with the current state."""
    stdscr.clear()
    display_projects(stdscr, "Last updated projects:", last_modified, 1, highlighted_project)
    display_projects(stdscr, "Last opened projects:", last_opened, 5, highlighted_project)
    stdscr.addstr(9, 0, "Start typing to search for git projects (Ctrl+C to exit):")
    stdscr.addstr(10, 0, "Query: " + query)

    if matches:
        for idx, match in enumerate(matches):
            prefix = '*' if match == selected_project else ' '
            stdscr.addstr(12 + idx, 0, f"{prefix} {os.path.basename(match)}")

    stdscr.refresh()

def handle_input(key, query, matches, tab_index, recent_projects, git_projects):
    """Handle user input and update the search state."""
    selected_project = None
    highlighted_project = None

    if key in (curses.KEY_BACKSPACE, 127):
        query = query[:-1]
    elif key == 9:  # Tab key
        if recent_projects:
            tab_index = (tab_index + 1) % len(recent_projects)
            highlighted_project = recent_projects[tab_index]
            query = os.path.basename(highlighted_project)
    elif key == 10 and curses.keyname(key) == b'^M':  # Shift+Enter
        query = ""
    else:
        query += chr(key)
        tab_index = 0
        highlighted_project = None

    if len(query) >= 2:
        matches = search_projects(git_projects, query)
        if matches:
            selected_project = matches[0]

    return query, matches, tab_index, selected_project, highlighted_project

def interactive_search(stdscr, git_projects, last_modified, last_opened, command):
    """Main function for the interactive search interface."""
    query = ""
    matches = []
    tab_index = 0
    selected_project = None
    highlighted_project = None
    recent_projects = last_opened + last_modified

    while True:
        update_screen(stdscr, query, last_modified, last_opened, matches, selected_project, highlighted_project)
        key = stdscr.getch()

        if key in (curses.KEY_EXIT, 3, 27):  # Ctrl+C or Esc to exit
            break
        elif key == 10:  # Enter key
            if selected_project:
                execute_command(selected_project, command)
                save_to_history(HISTORY_FILE, selected_project)
                return

        query, matches, tab_index, selected_project, highlighted_project = handle_input(
            key, query, matches, tab_index, recent_projects, git_projects
        )

def execute_command(selected_project, command):
    """Execute the specified command with the selected project."""
    if command:
        final_command = [part.replace('%F', selected_project) for part in command]
        subprocess.run(final_command)
    else:
        print(selected_project)

def main(stdscr, command):
    """Main entry point for the application."""
    git_projects = find_git_projects(DEFAULT_ROOT, DEFAULT_DEPTH)
    last_modified_projects = get_last_modified_projects(git_projects)
    last_opened_projects = get_last_opened_projects(HISTORY_FILE)
    interactive_search(stdscr, git_projects, last_modified_projects, last_opened_projects, command)

if __name__ == "__main__":
    command = sys.argv[1].split() if len(sys.argv) > 1 else None
    curses.wrapper(main, command)