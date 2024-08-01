# Built in modules
import argparse

# Custom made modules
from smi2ass import Smi2Ass


def cmd_arg() -> dict[str, dict[str, any]]:
    args: dict[str, dict[str, any]] = {
        "smi_file": {"flag": False, "data": []},
        "output_path": {"flag": False, "data": ""},
        "title": {"flag": False, "data": ""},
        "font": {"flag": False, "data": ""},
        "font_size": {"flag": False, "data": ""},
        "resolution": {"flag": False, "data": ["", ""]},
    }

    return args


def main() -> None:
    arg: dict[str, dict[str, any]] = cmd_arg()
    print("Hello")


if __name__ == "__main__":
    main()
