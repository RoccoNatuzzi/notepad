import subprocess
import sys
import os
import customtkinter

def build():
    """
    Runs PyInstaller to build the executable, ensuring customtkinter data
    files are included.
    """
    # Get the path to the customtkinter library
    ctk_path = os.path.dirname(customtkinter.__file__)

    # The --add-data flag format is 'source:destination'
    # We want to copy the customtkinter directory into the root of the executable
    add_data_flag = f"--add-data={ctk_path}:customtkinter"

    pyinstaller_command = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--name', 'DiffNote',
        '--onefile',
        '--windowed',
        '--clean',
        add_data_flag,
        '--add-data=theme.json:.',
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
