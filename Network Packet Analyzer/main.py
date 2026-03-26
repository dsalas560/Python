# main.py
# The entry point for the Network Packet Analyzer.
# This is the file you run to start the program â€” it handles startup,
# checks that everything is in order, and hands control to capture.py.
#
# Keeping main.py thin and clean is good practice. All the real logic
# lives in the src/ modules. main.py just ties everything together.
#
# To run this program:
#   1. Open VS Code as Administrator (required for packet capture on Windows)
#   2. Open the terminal with Ctrl + `
#   3. Run: python main.py

import sys
# sys.version_info â€” lets us check the Python version at runtime.
# sys.exit()       â€” cleanly exits the program with a status code.
#                    Exit code 0 = success, 1 = error. This is standard
#                    Unix/Windows convention used by shells and CI systems.

import os
# os.path.exists() â€” checks whether a file or folder exists on disk.
# os.makedirs()    â€” creates a folder (and any missing parent folders).
# We use these to make sure the logs/ directory exists before capturing.

# Add the src/ folder to Python's module search path.
# By default Python only looks in the current directory for imports.
# sys.path is the list of directories Python searches when you write "import X".
# Inserting src/ at index 0 means Python checks src/ first before anywhere else.
# This is what allows capture.py to do "from parser import parse_packet" etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# os.path.dirname(__file__) â€” gets the directory containing main.py
# os.path.join(..., "src")  â€” appends "src" to that path in an OS-safe way
#                             (uses backslash on Windows, forward slash on Mac/Linux)

from capture import run
# Now that src/ is on the path, we can import from our own modules.
# run() is the main entry point in capture.py that starts the whole session.


# --- Minimum Python Version Check ---
# f-strings (used throughout this project) require Python 3.6+.
# The "X | Y" type union syntax (e.g. int | None) requires Python 3.10+.
# We enforce 3.10 as the minimum to avoid confusing syntax errors.
MIN_PYTHON = (3, 10)


def check_python_version():
    """
    Checks that the running Python version meets our minimum requirement.
    
    sys.version_info is a named tuple like (3, 11, 2, 'final', 0).
    We compare the first two elements (major, minor) against MIN_PYTHON.
    Tuple comparison in Python is lexicographic â€” (3, 11) > (3, 10) is True.

    Exits the program with an error message if the version is too old.
    """

    if sys.version_info < MIN_PYTHON:
        # sys.version gives the full version string e.g. "3.9.7 (default, ...)"
        print(f"[!] Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.")
        print(f"[!] You are running Python {sys.version}")
        print(f"[!] Please upgrade at https://www.python.org/downloads/")

        # Exit with code 1 to signal an error to the shell
        sys.exit(1)


def check_logs_directory():
    """
    Ensures the logs/ directory exists before the capture session starts.
    
    os.path.exists() returns True if the path exists (file or folder).
    os.makedirs() creates the directory and any missing parents.
    
    We do this at startup so capture sessions can immediately write log
    files without needing to check mid-capture.
    """

    logs_dir = "logs"

    if not os.path.exists(logs_dir):
        # exist_ok=True means no error is raised if the folder already exists.
        # Without exist_ok=True, a race condition could cause a crash if two
        # processes tried to create the folder at the same time.
        os.makedirs(logs_dir, exist_ok=True)
        print(f"[+] Created logs directory at ./{logs_dir}/")


def check_scapy():
    """
    Verifies that Scapy is installed and importable.
    
    We attempt to import scapy inside a try/except block.
    ImportError is raised by Python when a module can't be found â€”
    meaning the user hasn't installed it yet.
    
    Giving a clear error message here is much friendlier than letting
    Python throw a raw ImportError stack trace later.
    """

    try:
        import scapy.all
    except ImportError:
        print("[!] Scapy is not installed.")
        print("[!] Run: pip install scapy")
        sys.exit(1)


def check_rich():
    """
    Verifies that Rich is installed and importable.
    Same pattern as check_scapy() â€” early, friendly error over a raw crash.
    """

    try:
        import rich
    except ImportError:
        print("[!] Rich is not installed.")
        print("[!] Run: pip install rich")
        sys.exit(1)


def print_banner():
    """
    Prints a startup banner to the terminal when the program launches.
    Gives the tool a professional feel and confirms it started correctly.
    """

    banner = r"""
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘         Network Packet Analyzer              â•‘
    â•‘         Built with Python + Scapy            â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    """
    # The r"..." prefix makes this a raw string â€” backslashes are treated
    # as literal characters, not escape sequences. Needed for the box art.
    print(banner)
    print("    [+] Checking environment...\n")


def main():
    """
    Main function â€” runs all startup checks then launches the capture session.
    
    Order matters here:
        1. Banner first so the user sees something immediately
        2. Version check before anything else that might use modern syntax
        3. Dependency checks before we try to import and use them
        4. Directory setup before any file writing could happen
        5. run() last â€” starts the actual capture session
    """

    print_banner()

    # Run all pre-flight checks before starting the capture
    check_python_version()
    check_scapy()
    check_rich()
    check_logs_directory()

    print("    [+] All checks passed. Starting analyzer...\n")

    # Hand control to capture.py to run the full capture session.
    # From here, capture.py manages the threads, display, and shutdown.
    run()


# --- Standard Python Entry Point Guard ---
# This block only runs when main.py is executed directly (python main.py).
# It does NOT run if main.py is imported as a module by another file.
#
# __name__ is a special Python variable:
#   - When you run a file directly: __name__ == "__main__"
#   - When a file is imported:      __name__ == the module's filename
#
# This pattern is standard practice in every Python project.
if __name__ == "__main__":
    main()
