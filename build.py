import os
import shutil
import subprocess
import sys

def build_executable():
    print("Building Unicorn Math Adventures executable...")
    
    # Create build and dist directories if they don't exist
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    
    # Get PyInstaller path
    python_scripts = os.path.join(os.path.dirname(sys.executable), "Scripts")
    user_scripts = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python312", "Scripts")
    
    # Try both system and user Scripts directories
    if os.path.exists(os.path.join(python_scripts, "pyinstaller.exe")):
        pyinstaller = os.path.join(python_scripts, "pyinstaller.exe")
    elif os.path.exists(os.path.join(user_scripts, "pyinstaller.exe")):
        pyinstaller = os.path.join(user_scripts, "pyinstaller.exe")
    else:
        raise FileNotFoundError("Could not find pyinstaller.exe")

    # Create clean dist directory
    try:
        if os.path.exists("dist"):
            shutil.rmtree("dist")
    except PermissionError:
        print("Please close any running instances of the game before building.")
        sys.exit(1)
    os.makedirs("dist")
    
    # PyInstaller command with bundled assets
    cmd = [
        pyinstaller,
        "--name=Unicorn Math Adventures",
        "--onefile",   # Create a single executable
        "--windowed",  # No console window
        "--icon=assets/images/unicorn.png",  # App icon
        "--add-data=assets/images/*.png;assets/images",  # Bundle images
        "--add-data=assets/sounds/*.mp3;assets/sounds",  # Bundle sounds
        "src/unicorn_math_adventures.py"
    ]
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    # Create README with UTF-8 encoding
    with open(os.path.join("dist", "README.txt"), "w", encoding="utf-8") as f:
        f.write("Unicorn Math Adventures\n")
        f.write("======================\n\n")
        f.write("A fun and educational math game featuring unicorns, rainbows, and magical word problems!\n\n")
        f.write("How to Play:\n")
        f.write("1. Double-click 'Unicorn Math Adventures.exe'\n")
        f.write("2. Choose your level or start with Level 1 (Addition & Subtraction)\n")
        f.write("3. Solve math problems to earn points and collect rainbow rewards\n")
        f.write("4. Get 10 correct answers in a row to level up\n")
        f.write("5. Try to beat your high score in 5 minutes!\n\n")
        f.write("Controls:\n")
        f.write("- Use number keys to enter answers\n")
        f.write("- Use space and forward slash for fractions (e.g., '1 1/3')\n")
        f.write("- Press Enter to submit your answer\n")
        f.write("- Press Backspace to correct mistakes\n\n")
        f.write("Important:\n")
        f.write("- High scores are saved automatically in your Documents folder\n")
        f.write("- The game can be moved anywhere on your computer\n\n")
        f.write("Enjoy learning math with unicorns!\n")
    
    print("Build complete! Game package is in the dist folder.")

if __name__ == "__main__":
    build_executable()
