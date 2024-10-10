import pandas as pd

from pypdf import PdfReader
from dateutil.parser import parse
from datetime import datetime

class NaturalLanguageProccessor: 

    def __init__(self, path, to_add_path):

        """
        Constructor
        
        Args: 

            path: 
                The path to the CSV file containing preexisting entries; to be
                read in as a dataframe, and new entries will be appended

            to_add_path: 
                The path to the PDF file containing entries that are not yet
                contained in the entries df; their text must be extracted via
                extract_text
        """
        
        self.entries = pd.read_csv(path)
        self.reader = PdfReader(to_add_path)
        self.pages = self.reader.pages
        self.new_entries = {}

    def _is_date(string, fuzzy=False):

        """ Determines whether a given string can be interpreted as a date. """

        try: 

            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            
            return False

    def extract_text(self): 
        
        last_possible_date = ""

        for page in self.pages:

            # extraction_mode=layout to preserve the layout in the original PDF
            text = page.extract_text(extraction_mode="layout")
            ls = text.split("\n")

            # if the first row in the page is a date...
            possible_date = ", ".join(ls[0].split(", ")[1:]).replace(" ", "")

            if self._is_date(possible_date):

                last_possible_date = possible_date
                self.new_entries[possible_date] = "\n".join(ls[1:]).replace("\n", " ").lstrip()

            else: 

                self.new_entries[last_possible_date] += text.replace("\n", " ")

    def get_latest_date(self): 
        
        """ Returns the date (datetime.date obj.) of the most recent entry """

        latest_entry = self.pages[0].extract_text(extraction_mode="layout")
        ls = latest_entry.split("\n")
        latest_date = ", ".join(ls[0].split(", ")[1:]).replace(" ", "")

        return datetime.strptime(latest_date, "%B%d,%Y").date()


