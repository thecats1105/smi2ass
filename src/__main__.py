# Built in modules
import argparse

# Custom made modules
from smi2ass import Smi2Ass


def cmd_arg() -> dict[str, dict[str, any]]:
    # Predefined values where command arguments are going to save
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
    # Test codes
    arg: dict[str, dict[str, any]] = cmd_arg()
<<<<<<< HEAD
    Smi2Ass("./test_smis/Angel Beats! 01.smi").to_ass().save("./convt_test")
    Smi2Ass("./test_smis/Angel Beats! 02.smi.smi").to_ass().save(
        "./convt_test"
    )
    Smi2Ass("./test_smis/Bakemonogatari-01.smi").to_ass().save("./convt_test")
    Smi2Ass("./test_smis/Durarara!! - 01.smi").to_ass().save("./convt_test")
    Smi2Ass("./test_smis/Durarara!! - 02.smi").to_ass().save("./convt_test")
    Smi2Ass("./test_smis/Psycho-Pass - S01E15.smi").to_ass().save(
        "./convt_test"
    )
    Smi2Ass("./test_smis/경계의 저편 BD 01화.smi").to_ass().save(
        "./convt_test"
    )
    Smi2Ass("./test_smis/경계의 저편 BD 02화.smi").to_ass().save(
        "./convt_test"
    )
=======
    print("Hello")
>>>>>>> parent of e5f6eb7 (Removing testing code from ass_setting)


if __name__ == "__main__":
    main()
