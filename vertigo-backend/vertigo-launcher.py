import os
import sys
import subprocess
import time
import venv

VENV_DIR = os.path.join(os.getcwd(), ".venv")
PYTHON_EXEC = os.path.join(VENV_DIR, "Scripts", "python.exe") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "python")

# Step 1: Create venv if missing
def create_venv():
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)

# Step 2: Install dependencies
def install_requirements():
    subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "-r", "requirements.txt"])


# Step 4: Run the app inside the virtualenv
def run_app():
    try:
        print("[INFO] Launching app...")
        # Instead of subprocess, run it directly (make sure vertigo.py has if __name__ == "__main__")
        os.execv(PYTHON_EXEC, [PYTHON_EXEC, "vertigo.py"])
    except Exception as e:
        print(f"[ERROR] Failed to launch app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_time = time.time()
    create_venv()
    install_requirements()
    print(f"[INFO] Setup completed in {time.time() - start_time:.2f} seconds")
    run_app()