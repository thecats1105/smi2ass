# Python built in modules
import re
from collections import defaultdict
from operator import itemgetter
from typing import Dict

# PIP installed modules
import chardet
from bs4 import BeautifulSoup, ResultSet

# Custom modules
from ass_settings import AssStyle


class Smi2Ass(AssStyle):
    def __init__(self, smi_path: str = "", **kwargs) -> None:
        """Class constructor, this class only initializes when SMI file path
        is given as input variable

        Args:
            smi_path (str, optional): Smi file path. Defaults to "".
        """

        # Initializing parent class
        super().__init__(**kwargs)

        self.smi_sgml: str
        self.smi_sgml_bs: ResultSet
        # Prepare the value hold smi lines by each language. The langue code
        # is used as key of the dictionary.
        # Each dictionary key is holding list as
        # [index, lines, time code]
        self.smi_lines: dict[str, list[any]] = defaultdict(list)
        # self.ass_lines: list[str]
        self.ass_lines: str

        # Only initialize the class when SMI file path is provided
        if smi_path != "":
            self.__preprocess(smi_path)

    def __preprocess(self, smi_path: str) -> None:
        # Check if file is accessible. If it is not, program will raise error.
        try:
            # Identify encoding of the file
            with open(smi_path, "rb") as f:
                f_encoding: str | None = chardet.detect(f.read())["encoding"]
            # Reading SMI file
            with open(
                smi_path, "r", encoding=f_encoding, errors="replace"
            ) as f:
                self.smi_sgml = f.read()
        except IOError as e:
            raise IOError(f"Failed to open the file {smi_path}: {e}")

        # Preprocess raw string before parse SMI lines
        self.__convert_whitespace()
        self.__convert_ss()
        self.__add_sync_tag()

        # Parse SMI with BeautifulSoup with HTML parser
        self.smi_sgml_bs = BeautifulSoup(
            self.smi_sgml, "html.parser"
        ).find_all("sync")

        self.__time_lan()

    def __convert_whitespace(self) -> None:
        # CRLF, LF or TAB to white space.
        # Some subtitle uses TAB as space character
        # whitespace = [u'\u000D\u000A', u'\u000A', u'\u000D', '\t']
        whitespace: list[str] = ["\u000D\u000A", "\u000A", "\u000D"]

        for temp in whitespace:
            self.smi_sgml.replace(temp, " ")

    def __convert_ss(self) -> None:
        # Convert special characters

        # Defining special characters in unicode
        char_ss: list[str] = [
            "\u00A0",
            "\u180E",
            "\u2000",
            "\u2001",
            "\u2002",
            "\u2003",
            "\u2004",
            "\u2005",
            "\u2006",
            "\u2007",
            "\u2008",
            "\u2009",
            "\u200A",
            "\u200B",
            "\u202F",
            "\u205F",
            "\u3000",
        ]
        # Replace special space characters so that Beautifulsoup
        # can't remove them
        for tmp_ss in char_ss:
            self.smi_sgml.replace(
                tmp_ss, f"smi2ass_unicode({str(ord(tmp_ss))})"
            )

        # Replace space around a tag with "&nbsp;", so that they are not
        # stripped when we replace a tag.
        self.smi_sgml = re.sub(r"> +<", ">smi2ass_unicode(32)<", self.smi_sgml)
        self.smi_sgml = re.sub(r"> +", ">smi2ass_unicode(32)", self.smi_sgml)
        self.smi_sgml = re.sub(r" +<", "smi2ass_unicode(32)<", self.smi_sgml)
        # but not <rt>
        self.smi_sgml = re.sub(
            r"< *[Rr][Tt] *>(smi2ass_unicode\([0-9]+\))+",
            "<rt>",
            self.smi_sgml,
        )
        self.smi_sgml = re.sub(
            r"(smi2ass_unicode\([0-9]+\))+</ *[Rr][Tt] *>",
            "</rt>",
            self.smi_sgml,
        )

    def __add_sync_tag(self) -> None:
        # Close the <sync> tags to avoid tag recursion

        # Remove </sync>
        self.smi_sgml = re.sub(r"</ *[Ss][Yy][Nn][Cc] *>", "", self.smi_sgml)
        # Add </sync> right before <sync>
        self.smi_sgml = re.sub(
            r"< *[Ss][Yy][Nn][Cc] +", "</sync><sync ", self.smi_sgml
        )

    def __ms2timestamp(self, ms: int) -> str:
        """Converting millisecond to h:mm:ss.ff time format

        Args:
            ms (int): Time in millisecond

        Returns:
            str: Converted time stamp
        """

        hours = int(ms / 3600000)
        ms -= hours * 3600000
        minutes = int(ms / 60000)
        ms -= minutes * 60000
        seconds = int(ms / 1000)
        ms -= seconds * 1000
        ms = round(ms / 10)
        return "%01d:%02d:%02d.%02d" % (hours, minutes, seconds, ms)

    def __time_lan(self) -> None:
        tmp_lines: dict[str, list[any]] = defaultdict(list)
        time_code: int  # Prepare valuable to hold time in ms.

        # Set for timecode and separate out each language
        for lines in self.smi_sgml_bs:
            # for index, lines in enumerate(self.smi_sgml_bs):
            # Get timecode from <SYNC Start= > tag
            # If case when there is error, the time_code is set to "-1"
            try:
                # original code uses regular expression to get timecode. Based
                # on some sample SMIs, it seems not need to use regular
                # expression
                # time_code = int(re.sub(r'\..*$', '', lines['start']))
                time_code = int(lines["start"])
                if time_code < 0:
                    time_code = -1
                    print(f"Negative time code: {lines}")
            except:
                time_code = -1
                print(f"Failed to extract time code: {lines}")

            # Language separation is depends on p class tag (<P Class= >)
            # Get language name from <P Class= > tag
            try:
                lang_tag: list[str] = lines.find("p")["class"]
            except:  # Bad case: <SYNC Start=7630><P>
                # If no p class, it will set to unknown language
                lang_tag = ["UNKNOWNCC"]
                print(f"Failed to extract language class: {lines}")
                print('Language has been set to "UNKNOWNCC"')

            # The key of the dictionary is language code in ass.
            # temporarily hols smi line data in to tmp_lines, and data
            # structure is [smi lines, ass time code, time in ms]
            if time_code > 0:
                ass_lang_code: str = self.get_lang_code(lang_tag[0].upper())
                tmp_lines[ass_lang_code].append(
                    [lines, self.__ms2timestamp(time_code), time_code]
                )

        # Sort the dictionary by the length of the list associated with
        # each key
        tmp_lines = dict(
            sorted(tmp_lines.items(), key=lambda item: len(item[1]))
        )

        """
        check whether proper multiple language subtitle
        if one language is less than 10% of the other language,
        it is likely that misuse of class name
        so combine or get rid of them
        """
        # Prepare list to hold language code and present of language compare
        # with largest language.
        # line_count structure: [lan code: str, percent: float]
        line_count: list[any] = []
        # First key from the dictionary, which has largest lines.
        tmp_key: str = list(tmp_lines.keys())[0]
        for tmp_lang in tmp_lines.keys():
            tmp_len: int = len(tmp_lines[tmp_lang])
            line_count.append(
                [tmp_lang, tmp_len, tmp_len / len(tmp_lines[tmp_key])]
            )

        """
        If there s a language with less than 10%, only two language exist than 
        combine them.
        I general, the main language has largest number of files. Thus, for
        this case, it is merging largest number of language.
        """
        # If there is only one language is detected, skip the merging process
        if len(line_count) != 1:
            for tmp in line_count:
                tmp_key: str = tmp[0]
                # If language is less then or equal to 10%, merge to largest
                if tmp[2] <= 0.1:
                    tmp_lines[line_count[0]] += tmp_lines[tmp_key]
                    del tmp_lines[tmp_key]

            # Sort each language lines based on SMI timecode in millisecond
            for key, value in tmp_lines:
                # Sorting lines by SMI timecode
                tmp_lines[key] = sorted(value, key=itemgetter(2))

                # Only copy SMI line and ASS timecode
                tmp_lines[key] = [tmp[:2] for tmp in tmp_lines[key]]

        # Copy temperate value to the class values
        self.smi_lines = tmp_lines

    def __core(self, lines) -> None:
        for i in range(len(lines)):
            tmp_line = lines[i][1]

            # Current time code
            ass_time_1: str = lines[i][2]
            # Next time code, if it is last item, then add 1s from current
            ass_time_2: str = (
                self.__ms2timestamp(int(lines["start"]) + 1000)
                if i == len(lines) - 1
                else lines[i + 1][2]
            )

            p_tags = tmp_line.find_all("p")

    def update_file2conv(self, smi_path: str) -> None:
        """Re-initialing class with new SMI file

        Args:
            smi_path (str): SMI file path
        """

        self.__preprocess(smi_path)

    def to_ass(self, smi_path: str = ""):
        pass

    def save(self, output_path: str):
        pass


if __name__ == "__main__":
    # Custom made modules
    from ass_settings import AssStyle

    tmp_smi: Smi2Ass = Smi2Ass("./test_smis/Psycho-Pass - S01E15.smi")
    # tmp_smi.to_ass("./test_smis/Psycho-Pass - S01E15.smi")

    print("Hello")

    tmp_lines = tmp_smi.smi_sgml_bs
    print(tmp_lines)
    tmp_lines = tmp_smi.smi_lines
    print(tmp_lines)
