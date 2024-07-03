# Python builtin modules
import json

# PIP installed modules
import webcolors

class AssStyle():
    def __init__(self, setting_path: str = './setting/') -> None:
        """Reads setting JSON file form local drive and compose into ASS
        header blcok. Also, reads language code and color code setting from
        JSON file from local drive that can convert SMI to ASS style code.

        Args:
            setting_path (str, optional): Path to where JSON files are located. 
            Defaults to './setting/'.
        """

        # Save input path
        self.root_path: str = setting_path

        # Reading language code
        self.lan_code: dict[str, str] = load_setting(
            'lan_code.json', self.root_path)

        # Reading ass style information
        self.ass_style: dict[str, any] = load_setting(
            'ass_styles.json', self.root_path)

        # Prepare even block of the ass header
        self.ass_event: str = "[Events]\nFormat: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text"

    def __compse_info(self) -> str:
        """Composing "Script Info" block of ASS header in string

        Returns:
            str: Composed "Script Info" block of subtitle
        """

        # Shallow copy to protect original data
        tmp_dict: dict[str, any] = self.ass_style["ScriptInfo"]

        # Adding heading of info section
        tmp_info: str = str(tmp_dict["Head"]) + '\n'

        # Adding message the info section
        if isinstance(tmp_dict["msg"], list):
            for tmp in tmp_dict["msg"]:
                tmp_info += tmp + '\n'
        else:
            tmp_info += tmp_dict["msg"] + "\n"

        # Instead of delecting used keys, just skip it
        for tmp in tmp_dict.keys():
            if (tmp != "Head") and (tmp != "msg"):
                tmp_info += f"{tmp}: {tmp_dict[tmp]}\n"

        return tmp_info  # Back to home!! LOL

    def __compose_styles(self) -> str:
        """Compose "Styles" block of AAS header in string

        Returns:
            str: Composed "Styles" block
        """

        # Shallow copy to protect original data
        tmp_dict: dict[str, any] = self.ass_style["style"]
        tmp_head: str = tmp_dict["Head"]
        tmp_format: str = "Format: "
        tmp_style: str = "Style: "

        # Instead of delecting used keys, just skip it
        for tmp in tmp_dict.keys():
            if tmp != "Head":
                tmp_format += f'{tmp}, '
                tmp_style += f'{tmp_dict[tmp]},'

        return f'{tmp_head}\n{tmp_format}\n{tmp_style}\n'

    def get_lang_code(self, tmp_lang_code: str) -> str:
        """Convert SMI language code to ASS language code

        Args:
            tmp_lang_code (str): SMI language code in all upper case

        Returns:
            str: Maching ASS language code. in case when language code is not 
            exist, it will return "und" as unknown
        """

        try:
            return self.lan_code[tmp_lang_code]
        except:
            print('Language code \"%s\" is not found, please add language code to \"%s\"' % (tmp_lang_code, 'lan_code.json'))
            return self.lan_code["UNKNOWNCC"]

    def color2hex(self, str_color: str) -> str:
        return webcolors.name_to_hex(str_color)

    def update_title(self, title: str) -> None:
        """Update title value in the Script Info block

        Args:
            title (str): Video fiel that what to add to Sctipt Info block
        """

        self.ass_style["ScriptInfo"]["Title"] = title

    def update_res(self, res_x: int, res_y: int) -> None:
        """To update resoluation information of the video. It is default to
        FullHD (1980 x 1080) resulution in the json file

        Args:
            res_x (int): Horizontal size of the screen
            res_y (int): Vertical size of the screen
        """

        self.ass_style["ScriptInfo"]["PlayResX"] = res_x
        self.ass_style["ScriptInfo"]["PlayResY"] = res_y

    def update_font_name(self, name: str) -> None:
        """Updating font of subtitle

        Args:
            name (str): Name of the Font
        """

        self.ass_style["style"]["Fontname"] = name

    def update_font_size(self, size: int | float) -> None:
        """Updating font size of subtitle

        Args:
            size (int | float): Size of font
        """

        self.ass_style["style"]["Fontsize"] = size

    def compose_ass_header(self) -> str:
        return self.__compse_info() + '\n' + self.__compose_styles() + \
            '\n' + self.ass_event


def load_setting(fs_name: str, fs_path: str) -> dict[str, any]:
    """Reading json file from file

    Args:
        fs_name (str): JSON file name
        fs_path (str): Path to JSON file

    Returns:
        dict[str, any]: Parsed JSON data from file 
    """

    # Setting full path of JSON file to open
    file2open: str = fs_path + fs_name
    with open(file2open, 'r') as f:
        return json.load(f)


# Some test codes that used during development
if __name__ == '__main__':
    # Testing code for "compose_ass_style"
    tmp = AssStyle()
    with open('./tmp_out.ass', 'w') as f:
        f.write(tmp.compose_ass_header())

    tmp.update_font_name("This is Test")
    tmp.update_font_size(100)
    tmp.update_title("Test title")
    tmp.update_res(12358, 1586897)
    with open('./tmp_out2.ass', 'w') as f:
        f.write(tmp.compose_ass_header())
