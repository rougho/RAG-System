import subprocess
import sys

def install_requirements():
    try:
        import pip
    except ImportError:
        print("pip is not installed. Please install pip and try again.")
        sys.exit(1)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

