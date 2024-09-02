import os
import subprocess
import sys
from pathlib import Path
import shutil
import subprocess

# Global variable, flag to check if the build script is running under windows
IS_WIN: bool = os.name == "nt"


def is_venv() -> bool:
    """Check if the script is running inside a virtual environment

    Returns:
        bool: True if it running inside of the virtual environment
    """
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def activate_venv(venv_path) -> None:
    """Activate the virtual environment

    Args:
        venv_path (str): The path of virtual environment.

    Raises:
        FileNotFoundError: Activation Script is not found.
    """

    # Root of virtual environment
    activate_script = Path(venv_path)

    if IS_WIN:
        activate_script = activate_script.joinpath(
            "Scripts", "activate_this.py"
        )
    else:
        activate_script = activate_script.joinpath("bin", "activate_this.py")

    if not activate_script.exists():
        raise FileNotFoundError(
            f"Activation script not found at {activate_script}"
        )

    with open(activate_script) as f:
        exec(f.read(), dict(__file__=activate_script))


def build_with_nuitka(script_name, output_dir, output_name) -> None:
    """Build the specified Python script using Nuitka

    Args:
        script_name (str): The name of the Python script to compile.
        output_dir (str): The directory to place the compiled executable.
        output_name (str): The name of compiled executable.
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
        "--jobs=8",
        f"--output-dir={output_dir}",
        f"--output-filename={output_name}",
        script_name,
    ]

    try:
        subprocess.run(command, check=True)
        print(f"\nSuccessfully built {output_name} with Nuitka.\n")
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to build {output_name}. Error: {e}\n")
        exit(2)


def copy_setting_dir(output_dir) -> None:
    """Copying directory that holding json files for ass header

    Args:
        output_dir (str): The output directory where excitable file
    """

    settings_dir = Path(f"{output_dir}/setting")
    if settings_dir.exists():
        shutil.rmtree(settings_dir)

    shutil.copytree(Path("./setting"), settings_dir)


def test_build_prog(out_dir, output_name) -> None:
    test_smis_dir = "./test_smis"

    test_command: list[str] = [
        f"{out_dir}/{output_name}" + (".exe" if IS_WIN else ""),
        f"{test_smis_dir}/Angel Beats! 01.smi",
        f"{test_smis_dir}/Angel Beats! 02.smi",
        f"{test_smis_dir}/Bakemonogatari-01.smi",
        f"{test_smis_dir}/Durarara!! - 01.smi",
        f"{test_smis_dir}/Durarara!! - 02.smi",
        f"{test_smis_dir}/Psycho-Pass - S01E15.smi",
        f"{test_smis_dir}/경계의 저편 BD 01화.smi",
        f"{test_smis_dir}/경계의 저편 BD 02화.smi",
    ]

    try:
        subprocess.run(test_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run built program. Error {e}")
        exit(2)


def main() -> None:
    # Ensure we are running in a virtual environment
    if not is_venv():
        venv_path = ".venv"  # Path to your virtual environment
        print(
            f"\nNot running inside a virtual environment. Activating {venv_path}...\n"
        )
        activate_venv(venv_path)

    script_name: str = "./src/__main__.py"
    output_dir: str = "./build"
    output_name: str = "smi2ass"

    # Let's build the program
    build_with_nuitka(script_name, output_dir, output_name)

    # Let's copy json files for the ass header
    copy_setting_dir(output_dir)

    # Let's test the program that was built
    test_build_prog(output_dir, output_name)


if __name__ == "__main__":
    main()