import subprocess
import sys
import os

def build():
    """
    Runs PyInstaller to build the executable.
    """
    pyinstaller_command = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--name', 'ModernDiff',
        '--onefile',
        '--windowed',
        '--clean',
        'src/main_app.py'
    ]

    print(f"Running command: {' '.join(pyinstaller_command)}")

    try:
        subprocess.run(pyinstaller_command, check=True)
        print("\nBuild successful!")
        print(f"Executable created in '{os.path.abspath('dist')}'")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\nBuild failed: PyInstaller not found. Make sure it is installed.")
        sys.exit(1)

if __name__ == "__main__":
    build()
