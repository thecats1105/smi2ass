# Python built in modules
import re
from collections import defaultdict
from operator import itemgetter
from typing import Dict

# PIP installed modules
import chardet
from bs4 import BeautifulSoup as bs
from bs4 import ResultSet

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

        self.path2smi: str  # Path to SMI file
        self.smi_sgml: str
        self.smi_sgml_bs: ResultSet
        # The value that  hold smi lines by each language. The language code
        # is used as key of the dictionary.
        # Each dictionary key is holding list as [lines, time code in ass]
        self.smi_lines: dict[str, list[any]] = defaultdict(list)
        # The value that holds converted lines from SMI subtitle. The language
        # will be used as key of the dictionary.
        # Each key will hold list as [lines of ass formatted subtitle]
        self.ass_lines: dict[str, list[str]] = defaultdict(list)
        # Flag initialization process is complete before converting to ASS
        self.flag_preprocess: bool = False

        # Only initialize the class when SMI file path is provided
        if smi_path != "":
            self.__preprocess(smi_path)

    def __preprocess(self, smi_path: str) -> None:

        self.path2smi = smi_path  # Saving input path

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
        self.smi_sgml_bs = bs(self.smi_sgml, "html.parser").find_all("sync")

        # Get timecode for each lines and septate out subtitle in each language
        self.__time_lan()

        # Preprocess is complete, not it can convert to ass
        self.flag_preprocess = True

    def __convert_whitespace(self) -> None:
        # CRLF, LF or TAB to white space.
        # Some subtitle uses TAB as space character
        whitespace: list[str] = ["\u000D\u000A", "\u000A", "\u000D"]

        # # Special case for "\t" character
        # self.smi_sgml.replace("\t", "    ")

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
        for key, value in tmp_lines.items():
            # Sorting lines by SMI timecode only more then one language
            if len(tmp_lines) != 1:
                tmp_lines[key] = sorted(value, key=itemgetter(2))

            # Appears need to save millisecond timecode for the very last list
            # # # Only copy SMI line and ASS timecode
            # tmp_lines[key] = [tmp[:2] for tmp in value]

        # Copy temperate value to the class values
        self.smi_lines = tmp_lines

    def __tag_conv(self, tags: list[any], conv_rule: str) -> None:
        for tmp_tag in tags:
            if len(tmp_tag.text) != 0:
                tmp_tag.replaceWith(conv_rule % tmp_tag.text)
            else:
                tmp_tag.extract()

    def __core(self, lines2conv: list[list[any]]) -> list[str]:
        # Setting first item to be ASS style header
        tmp_ass_lines: list[str] = [self.ass_header()]

        for i in range(len(lines2conv)):
            # Getting current line of SMI
            tmp_line: bs = lines2conv[i][0]

            # Setting converted timecode
            timcode_1: str = lines2conv[i][1]  # Start of subtitle

            # Setting end time code
            try:
                timecode_2: str = lines2conv[i + 1][1]  # End of subtitles
            except:
                """
                Due to how the SMI subtitle is structure, there isn't
                indication for end time for the line. Thus, adding 1s to the
                last time code, os it cant convert without error
                """
                timecode_2: str = self.__ms2timestamp(lines2conv[i][2] + 1000)

            # Converting next line (br) tags
            for tmp_br in tmp_line.find_all("br"):
                tmp_br.replaceWith("\\n")

            # Convert bold (b) tags
            self.__tag_conv(tmp_line.find_all("b"), "{\\b1}%s{\\b0}")

            # Convert italics (i) tag
            self.__tag_conv(tmp_line.find_all("i"), "{\\i1}%s{\\i0}")

            # Convert underline (u) tag
            self.__tag_conv(tmp_line.find_all("u"), "{\\u1}%s{\\u0}")

            # Convert strikes (s) tag
            self.__tag_conv(tmp_line.find_all("s"), "{\\s1}%s{\\s0}")

            # Convert ruby (rt) tag
            self.__tag_conv(
                tmp_line.find_all("s"),
                "{\\fscx50}{\\fscy50}&nbsp;%s&nbsp;{\\fscx100}{\\fscy100}",
            )

            p_tags = tmp_line.find_all("p")

    def update_file2conv(self, smi_path: str) -> None:
        """Re-initialing class with new SMI file

        Args:
            smi_path (str): SMI file path
        """

        self.__preprocess(smi_path)

    def to_ass(self, smi_path: str = "") -> None:
        # If there is path input then update to new SMI file
        if smi_path != "":
            self.update_file2conv(smi_path)

        # If class was not initialized print error message.
        if not self.flag_preprocess:
            print("Initialization  process is not complete")
            print(
                'Please Initialize class by calling "update_file2conv" method'
            )
        else:
            for key, value in self.smi_lines.items():
                self.ass_lines[key] = self.__core(value)
                # self.ass_lines[key].append(self.ass_header())
                # self.ass_lines[key] += self.__core(value)

    def save(self, output_path: str):
        pass
