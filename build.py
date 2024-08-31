import os
import subprocess
import sys
from pathlib import Path
import shutil


def is_venv() -> bool:
    """
    Check if the script is running inside a virtual environment.
    """
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def activate_venv(venv_path) -> None:
    """
    Activate the virtual environment.

    :param venv_path: Path to the virtual environment.
    """
    activate_script = os.path.join(venv_path, "Scripts", "Activate.ps1")
    if not os.path.exists(activate_script):
        raise FileNotFoundError(
            f"Activation script not found at {activate_script}"
        )

    with open(activate_script) as f:
        exec(f.read(), dict(__file__=activate_script))


def build_with_nuitka(script_name, output_dir, ouput_name) -> None:
    """
    Build the specified Python script using Nuitka.

    :param script_name: The name of the Python script to compile.
    :param output_dir: The directory to place the compiled executable.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = [
        sys.executable,  # Use the current Python executable
        "-m",
        "nuitka",
        "--follow-imports",
        "--standalone",
        "--onefile",
        "--remove-output",
        f"--output-dir={output_dir}",
        f"--output-filename={ouput_name}",
        script_name,
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully built {script_name} with Nuitka.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build {script_name}. Error: {e}")


def main() -> None:
    # Ensure we are running in a virtual environment
    if not is_venv():
        venv_path = "venv"  # Path to your virtual environment
        print(
            f"Not running inside a virtual environment. Activating {venv_path}..."
        )
        activate_venv(venv_path)

    script_name: str = "./src/__main__.py"
    output_dir: str = "./build"
    ouput_name: str = "smi2ass"
    build_with_nuitka(script_name, output_dir, ouput_name)

    # Check if setting file exist, if it is delete them
    if Path(f"{output_dir}/setting").exists():
        Path(f"{output_dir}/setting").unlink()

    # Copy setting folder into build folder
    shutil.copytree(Path("./setting"), Path(f"{output_dir}/setting"))


if __name__ == "__main__":
    main()
