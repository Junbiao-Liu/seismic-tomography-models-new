#!/usr/bin/env python3
"""
Run all Python scripts with one click
"""
import subprocess
import sys
from pathlib import Path

def ensure_directories_exist():
    """Ensure required directories exist"""
    project_root = Path(__file__).parent.absolute()
    
    # Define required directories
    required_dirs = [
        project_root / "orig_nc",
        project_root / "processing_nc"
    ]
    
    # Create directories if they don't exist
    for directory in required_dirs:
        directory.mkdir(exist_ok=True)
        print(f"✓ Ensured directory exists: {directory}")

def run_all_scripts():
    """Run all Python scripts in python_src directory"""
    project_root = Path(__file__).parent.absolute()
    python_src_dir = project_root / "python_src"
    
    # Ensure required directories exist
    ensure_directories_exist()
    
    if not python_src_dir.exists():
        print(f"Error: {python_src_dir} directory does not exist")
        return
    
    # Get all .py files
    py_files = list(python_src_dir.glob("*.py"))
    
    # Exclude this script itself
    py_files = [f for f in py_files if f.name != "run_all.py"]
    
    if not py_files:
        print("No Python scripts found")
        return
    
    print(f"Found {len(py_files)} Python scripts:")
    for i, py_file in enumerate(py_files, 1):
        print(f"{i}. {py_file.name}")
    
    # Run all scripts in order
    for py_file in py_files:
        print(f"\n🚀 Running: {py_file.name}")
        print("-" * 50)
        
        try:
            # Run script with correct working directory
            result = subprocess.run([sys.executable, str(py_file)], 
                                  cwd=str(python_src_dir),  # Set working directory to python_src
                                  capture_output=False,     # Show output in real-time
                                  text=True)
            
            if result.returncode == 0:
                print(f"✅ {py_file.name} completed successfully")
            else:
                print(f"❌ {py_file.name} failed")
                
        except Exception as e:
            print(f"❌ Error running {py_file.name}: {e}")

if __name__ == "__main__":
    run_all_scripts()
