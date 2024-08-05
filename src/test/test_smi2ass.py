"""
Test code that used during development stage.
"""

from smi2ass import Smi2Ass


def main() -> None:
    tmp_smi: Smi2Ass = Smi2Ass("./test_smis/Psycho-Pass - S01E15.smi")

    print("writing test file 1")
    tmp_lines = tmp_smi.smi_lines[list(tmp_smi.smi_lines.keys())[0]]
    with open("test1.txt", "w", encoding="utf-8") as f:
        f.writelines([str(tmp[0]) + "\n\n" for tmp in tmp_lines])

    tmp_smi.to_ass()
    tmp_smi.save()

    print("writing test file 2")
    tmp_smi.update_file2conv("./test_smis/Bakemonogatari-01.smi")
    tmp_lines = tmp_smi.smi_lines[list(tmp_smi.smi_lines.keys())[0]]
    with open("test2.txt", "w", encoding="utf-8") as f:
        f.writelines([str(tmp[0]) + "\n\n" for tmp in tmp_lines])

    tmp_smi.to_ass()
    tmp_smi.save()

    print("writing test file 3")
    tmp_smi.update_file2conv("./test_smis/경계의 저편 BD 01화.smi")
    tmp_lines = tmp_smi.smi_lines[list(tmp_smi.smi_lines.keys())[0]]
    with open("test3.txt", "w", encoding="utf-8") as f:
        f.writelines([str(tmp[0]) + "\n\n" for tmp in tmp_lines])

    tmp_smi.to_ass()
    tmp_smi.save("./converted")


if __name__ == "__main__":
    main()
