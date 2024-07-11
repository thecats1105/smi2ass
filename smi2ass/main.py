# Python build in pakage
import sys
from operator import itemgetter
# Importing html pakage based on python version
if sys.version_info.major == 3:
    if sys.version_info.minor < 7:
        from html.parser import HTMLParser
    else:
        import html
else:
    sys.exit('Python < 3 is unsupported...')

# PIP installed mouldes
import chardet

