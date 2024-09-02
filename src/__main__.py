# Built in modules
import argparse
from pathlib import Path

# Custom made modules
from smi2ass import smi2ass


def cmd_arg():
    parser = argparse.ArgumentParser(
        prog="smi2ass",
        description="Converting SAMI (SMI) into Advanced SubStation Alpha (ASS) subtitle",
    )

    parser.add_argument(
        "file_name",
        metavar="F",
        type=str,
        nargs="+",
        help="SMI file name to  be processed",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        type=str,
        default=str(Path().cwd().joinpath("out")),
        help="The output folder where file will be saved",
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="Tile of the video file for subtitle header",
    )

    parser.add_argument(
        "-f", "--font_size", type=float, help="Font size of subtitle"
    )

    parser.add_argument(
        "-res_x",
        "--resolution_x",
        type=int,
        help="Horizontal resolution of the video",
    )

    parser.add_argument(
        "-res_y",
        "--resolution_y",
        type=int,
        help="Vertical resolution of the video",
    )

    return parser.parse_args()


def main() -> None:
    obj_smi2ass = smi2ass()
    args: argparse.Namespace = cmd_arg()

    for tmp_file_name in args.file_name:
        obj_smi2ass.to_ass(tmp_file_name).save(args.output_dir)


if __name__ == "__main__":
    main()