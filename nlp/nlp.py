import pandas as pd

from pypdf import PdfReader
from dateutil.parser import parse
# from datetime import datetime

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
        self.entries["date"] = pd.to_datetime(self.entries["date"])

        self.reader = PdfReader(to_add_path)
        self.pages = self.reader.pages
        self.new_entries = {}

    def _is_date(self, string, fuzzy=False):

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
            print(possible_date)

            if self._is_date(possible_date):

                last_possible_date = possible_date
                self.new_entries[possible_date] = "\n".join(ls[1:]).replace("\n", " ").lstrip()

            else: 

                self.new_entries[last_possible_date] += text.replace("\n", " ")

        self.new_entries = pd.DataFrame({
            "date": list(self.new_entries.keys()), 
            "entry": list(self.new_entries.values())
        })

        # convert date to pandas datetime
        self.new_entries["date"] = pd.to_datetime(self.new_entries["date"], format="%B%d,%Y")

        print(f"{len(self.new_entries)} new entries processed")

    def save_all_entries(self): 

        self.extract_text()
        last_date = self.new_entries["date"].iloc[0].date()
        all_entries = pd.concat([self.entries, self.new_entries])
        all_entries = all_entries.sort_values(by='date').reset_index()
        all_entries.to_csv(f"/home/jasmine/PROJECTS/journal_analysis/data/{last_date}_ENTRIES.csv", index=False)
        print(f"Entries updated in /home/jasmine/PROJECTS/journal_analysis/data/{last_date}_ENTRIES.csv")

if __name__ == "__main__":

    nlp = NaturalLanguageProccessor(path="/home/jasmine/PROJECTS/journal_analysis/data/OCT10.csv", 
                                    to_add_path="/home/jasmine/Downloads/Journal.pdf")
    nlp.save_all_entries()