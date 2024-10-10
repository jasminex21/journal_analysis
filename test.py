from pypdf import PdfReader
from dateutil.parser import parse

def is_date(string, fuzzy=False):

    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """

    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

reader = PdfReader("/home/jasmine/PROJECTS/journal_analysis/data/Journal.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text(extraction_mode="layout")

print(number_of_pages)
print(page)
print(text)