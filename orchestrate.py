import os
import sys
import subprocess
import time
import re
import logging
import warnings
import shutil
import asyncio

# Suppress System Warnings (Python 3.9 EOL, etc.)
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Configure Global Logging
logging.basicConfig(
    filename='logs_main.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("[ORCHESTRATOR] --- NEW SESSION STARTED ---")
logger = logging.getLogger()

def print_banner():
    # Use standard ANSI escape to clear scrollback as well as current view
    if os.name == 'posix':
        sys.stdout.write("\033[H\033[2J\033[3J")
    else:
        os.system('cls')
    
    print("\033[1;94m")
    print(r"""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠃⠹⠄⠀⠸⣿⣿⣧⠀⠀⠘⠙⠛⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⡏⠁⠀⠀⠀⠀⠀⠀⠐⣿⣿⠷⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⣅⡄⠸⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⣽⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⣸⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠙⠗⠋⣿⣇⣹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣗⣀⢠⣀⣠⣤⣤⡀⠐⠀⢹⣿⠀⠔⠠⣄⣤⣤⣠⣄⣀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣿⣿⡄⠀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠈⣿⣿⠃⠀⢿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠒⢌⠉⠻⠿⠿⠟⠋⠀⢀⣽⣿⣄⠀⠈⠙⠻⠿⠟⠋⠛⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠑⢄⠀⠀⠀⠀⢰⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣄⠀⠀⠈⠑⠉⠓⢆⠸⠿⢻⣿⠻⠿⠀⠀⠀⠀⠀⢀⣠⠀⣀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠁⢹⠢⡀⠀⠀⠀⠈⠓⢢⠸⡏⠀⠀⠀⠀⠀⠀⠀⠀⢸⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣴⡈⢑⠢⢄⡀⠀⠀⢹⣿⣄⠀⢀⣀⣀⣸⢹⡟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠳⣮⡀⠄⠀⢱⡦⢼⣿⡬⣯⡍⠀⠀⣉⢙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣿⣿⣿⣰⡄⣸⣷⣾⣿⣿⣿⠀⣤⣸⣿⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣏⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    """)
    print("\033[0m")
    print("\033[1;97m   TRACXN GHOST RECON \033[0m\033[90m| \033[91mDead Domain Scraper Engine\033[0m")
    print("\033[90m   " + "─" * 54 + "\033[0m")
    print("\033[3;37m   \"Death Walks Among You! Reviving Dead Domains...\"\033[0m")
    print(f"\n\033[90m   [{time.strftime('%H:%M:%S')}] System Online. Logs: logs_main.log\033[0m\n")

# Make sure the current directory is in path for imports
sys.path.append(os.getcwd())

try:
    from services.google_sheet import GoogleSheetClient
except ImportError:
    print("[ORCHESTRATOR] Missing parent dependencies. Attempting to install using uv...")
    subprocess.run(["uv", "pip", "install", "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2", "gspread"], check=False)
    try:
        from services.google_sheet import GoogleSheetClient
    except ImportError:
        print("[CRITICAL] Could not import GoogleSheetClient. Please run 'pip install google-api-python-client google-auth' in your base environment.")
        sys.exit(1)

def find_latest_python():
    """Finds the highest version of python3 available on the system."""
    search_dirs = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]
    candidates = []
    for d in search_dirs:
        if not os.path.exists(d): continue
        try:
            for f in os.listdir(d):
                if re.match(r"^python3\.\d+$", f):
                    candidates.append(os.path.join(d, f))
        except Exception: pass
    
    if not candidates:
        return sys.executable
    
    def ver_key(p):
        parts = re.findall(r"\d+", p)
        return [int(x) for x in parts] if parts else [0]
        
    candidates.sort(key=ver_key, reverse=True)
    return candidates[0]

def get_python_executable(force=False):
    """
    Exclusively uses 'uv' for environment management in the root directory.
    Handles venv creation, python versioning, and dependency synchronization atomically.
    """
    venv_path = os.path.join(os.getcwd(), ".venv")
    unix_path = os.path.join(venv_path, "bin", "python")
    win_path = os.path.join(venv_path, "Scripts", "python.exe")
    venv_exe = unix_path if os.name != "nt" else win_path
    
    if not shutil.which("uv"):
        print("\n\033[91m[CRITICAL] 'uv' not found!\033[0m")
        print("This engine now requires 'uv' for high-performance environment management.")
        print("Install it via: \033[96mcurl -LsSf https://astral.sh/uv/install.sh | sh\033[0m\n")
        sys.exit(1)

    if force and os.path.exists(venv_path):
        print(f"[ORCHESTRATOR] Purging environment (Atomic)...")
        if os.name != "nt":
            trash_path = venv_path + ".trash"
            try:
                if os.path.exists(trash_path):
                    subprocess.run(["rm", "-rf", trash_path], check=False)
                os.rename(venv_path, trash_path)
                subprocess.Popen(["rm", "-rf", trash_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                subprocess.run(["rm", "-rf", venv_path], check=False)
        else:
            subprocess.run(["rmdir", "/s", "/q", venv_path], shell=True, check=False)

    is_broken = os.path.exists(venv_path) and not os.path.exists(os.path.join(venv_path, "pyvenv.cfg"))
    if not os.path.exists(venv_path) or is_broken or force:
        if is_broken: print(f"[ORCHESTRATOR] Detected broken environment. Recreating...")
        
        if os.path.exists(venv_path):
            if os.name != "nt": subprocess.run(["rm", "-rf", venv_path], check=False)
            else: subprocess.run(["rmdir", "/s", "/q", venv_path], shell=True, check=False)
            
        print(f"[ORCHESTRATOR] Creating environment via uv...")
        subprocess.run(["uv", "venv"], cwd=os.getcwd(), check=True)

    print(f"[ORCHESTRATOR] Installing dependencies via uv...")
    try:
        req_path = os.path.join(os.getcwd(), "requirements.txt")
        if os.path.exists(req_path):
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], cwd=os.getcwd(), check=True)
        else:
            subprocess.run(["uv", "pip", "install", "."], cwd=os.getcwd(), check=True)
        
        print(f"[ORCHESTRATOR] Verifying Playwright binaries...")
        subprocess.run(["uv", "run", "playwright", "install"], cwd=os.getcwd(), check=True)
        
        return venv_exe
    except subprocess.CalledProcessError as e:
        print(f"\n\033[91m[CRITICAL] uv sync failed: {e}\033[0m")
        sys.exit(1)

def run_engine(sheet_id, extra_args=None):
    print(f"\n[ORCHESTRATOR] Starting Engine...")
    
    python_exe = get_python_executable()
    print(f"[ORCHESTRATOR] Using Python: {python_exe}")
    
    env = os.environ.copy()
    venv_dir = os.path.abspath(os.path.join(os.getcwd(), ".venv"))
    
    if os.path.exists(venv_dir):
        env["VIRTUAL_ENV"] = venv_dir
        bin_dir = os.path.join(venv_dir, "bin") if os.name != "nt" else os.path.join(venv_dir, "Scripts")
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
        print(f"[ORCHESTRATOR] Venv Activated: {venv_dir}")
    
    cmd = [python_exe, "ghost.py", "--sheet-id", sheet_id]
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        logging.info(f"[ORCHESTRATOR] Executing Shell: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, cwd=os.getcwd(), env=env)
        process.wait()
        
        exit_code = process.returncode
        if exit_code < 0:
            import signal
            sig_name = signal.Signals(-exit_code).name
            logging.error(f"[ORCHESTRATOR] Engine KILLED by signal {sig_name} (Code {exit_code})")
        else:
            logging.info(f"[ORCHESTRATOR] Engine finished with exit code {exit_code}")
    except KeyboardInterrupt:
        print("\n[ORCHESTRATOR] Interrupted by user. Cleaning up...")
        process.terminate()
        sys.exit(1)
    return process.returncode

def extract_id(sheet_input):
    if "spreadsheets/d/" in sheet_input:
        match = re.search(r"spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_input)
        return match.group(1) if match else sheet_input
    return sheet_input

def setup_environments():
    print("\n\033[97m[GHOST] INITIALIZING ENVIRONMENTS\033[0m")
    print(f"\033[90m-------------------------------\033[0m")
    get_python_executable(force=True)
    print("\n\033[92m[SUCCESS] Environment is ready.\033[0m")

def show_diagnostics(sheet_id):
    print(f"\n\033[97m[GHOST] SYSTEM DIAGNOSTICS\033[0m")
    print(f"\033[90m-------------------------\033[0m")
    print(f"Target Sheet: {sheet_id}")
    try:
        from utils.hardware import HardwareOptimizer
        conc, specs = HardwareOptimizer.calculate_concurrency()
        print(f"Detected RAM:  {specs['total_ram_gb']}GB")
        print(f"CPU Cores:     {specs['cpu_cores']}")
        print(f"Max Concur:    {conc}")
    except:
        print("Hardware data unavailable.")

async def main():
    DEFAULT_SHEET = "1WvqHhXQcFSOuGnDW87J2Elv29uMEMAWiTknB4BWzlD4"
    sheet_id = DEFAULT_SHEET

    while True:
        print_banner()
        print("\033[90m   --- ORCHESTRATED RUNS ---\033[0m")
        print("\033[1;96m   [0] UNIFIED RECON       \033[90m(Integrated Single-Pass | HIGH FIDELITY)\033[0m")
        print("\033[1;96m   [1] UNIFIED WEB SEARCH  \033[90m(Google Serper + LinkedIn Fallback Only)\033[0m")
        
        print("\n\033[90m   --- UTILITIES ---\033[0m")
        print("\033[97m   [2] DIAGNOSTICS         \033[90m(System & Hardware Check)\033[0m")
        print("\033[97m   [3] SETUP ENVIRONMENT   \033[90m(Reinstall dependencies)\033[0m")
        print("\033[91m   [4] EXIT HUB            \033[90m(Close engine)\033[0m")
        
        choice = input(f"\n\033[96m   [GHOST] Select Strategy >> \033[0m").strip()

        if choice in ['0', '1']:
            dtype_choice = input(f"\n\033[96m   [GHOST] Select Output Format [1] Text Only (Faster) [2] HTML >> \033[0m").strip()
            data_type = "html" if dtype_choice == '2' else "text"

        if choice == '0':
            run_engine(sheet_id, ["--data-type", data_type])
            break
        elif choice == '1':
            run_engine(sheet_id, ["--mode", "search_only", "--data-type", data_type])
            break
        elif choice == '2':
            show_diagnostics(sheet_id)
            input("\n\033[90mPress Enter to return to menu...\033[0m")
        elif choice == '3':
            setup_environments()
            input("\n\033[90mEnvironment setup complete. Press Enter to return to menu...\033[0m")
        elif choice == '4':
            print("\n\033[90m[ORCHESTRATOR] Shutting down Ghost Recon Hub...\033[0m")
            sys.exit(0)
        else:
            print("\033[91m   Invalid Selection. Try again.\033[0m")
            time.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
    print("\n[ORCHESTRATOR] Full Pipeline execution completed successfully.")
