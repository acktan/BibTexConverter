import re
from typing import Optional


class ApaConverter():
    """Convert APA citation type to BibTeX"""
    def __init__(self) -> None:
        """Initialize module"""
        self.bibtex_type_list = {
                            'article': 'article, periodical, journal, magazine',
                            'book': 'book, publications,  publication',
                            'booklet': 'book, no publisher',
                            'conference': 'conference, paper',
                            'inbook': 'section, chapter, book',
                            'incollection': 'article, collection',
                            'inproceedings': 'conference, paper',
                            'manual': 'technical, manual',
                            'masterthesis': 'Masters, thesis',
                            'phdthesis': 'PhD, thesis',
                            'proceedings': 'conference, proceedings',
                            'techreport': 'technical, report, government, white paper',
                            'unpublished': 'not published'
                            }
        self.location = False

    def extract_bibtex_type(self, input_text: str) -> str:
        """ Extract the bibtex type of the citation based on information in the citation

        Args:
            input_text = the entire citation
        Returns:
            BibTeX type
        """
        for bibtype, description in self.bibtex_type_list.items():
            for phrase in description.split(','):
                if phrase in input_text.lower():
                    return "@" + bibtype
        return "@misc"

    def convert(self, input_text: str, bibtex_type: Optional[str] = None) -> str:
        """Run all functions to convert citation to bibtex

        Args:
            input_text = the entire citation
            bibtex_type = bibtex_type of citation if known
        Returns:
            converted_citation
        """

        if bibtex_type is None:
            bibtex_type = self.extract_bibtex_type(input_text)
        elif bibtex_type not in self.bibtex_type_list:
            raise NameError('This BibTeX type does not exist')


        author = self.get_authors(input_text)
        title = self.get_title(input_text)
        year = self.get_year(input_text)

        bibtex_name = ''.join([author.split(', ', maxsplit=1)[0].lower(), year])
        full_bibtex = f"""{bibtex_type}{{{bibtex_name}, \n author = {{{author}}}, \n title = {{{title}}}, \n year = {year}, \n """

        if bibtex_type == '@book':
            publisher = self.get_publishers(input_text)
            full_bibtex += f'publisher = {{{publisher}}}, \n '
            if self.location:
                full_bibtex += f'location = {{{self.location}}}, \n '

        if bibtex_type == '@article':
            try:
                journal, second = self.get_journal(input_text)
                if '-' in second:
                    second = ApaConverter.remove_non_numeric_chars(second)
                    full_bibtex += f'journal = {{{journal}}}, \n pages = {{{second}}}, \n '
                else:
                    full_bibtex += f'journal = {{{journal}}}, \n volume = {{{second}}}, \n '
            except ValueError:
                try:
                    journal, second, third = self.get_journal(input_text)
                    if '(' in second:
                        contains_page = second.split('(')
                        volume = contains_page[0]
                        number = contains_page[1].replace(')', '')
                        third = third.replace('p ', '')
                        full_bibtex += f'journal = {{{journal}}}, \n volume = {{{volume}}}, \n number = {{{number}}}, \n pages = {{{third}}}, \n'
                    else:
                        full_bibtex += f'journal = {{{journal}}}, \n volume = {{{second}}}, \n pages = {{{third}}}, \n'
                except ValueError:
                    journal = self.get_journal(input_text)
                    full_bibtex += f'journal = {{{journal}}}, \n'

        # close out parentheses on BibTeX
        full_bibtex += '}'
        return full_bibtex


    def get_title(self, input_text: str) -> Optional[str]:
        """Get title from apa citation

        Args:
            input_text = the entire citation
        Returns:
            title of text
        """
        title = input_text.split(').')[1].split('. ')[0].strip()
        if title:
            return title
        return None

    def get_year(self, input_text) -> Optional[str]:
        """Get first instance of 4 numbers within parentheses in citation

        Args:
            input_text = the entire citation
        Returns:
            year
        """
        pattern = r'\((.*?)\)'
        match = re.search(pattern, input_text)
        if match:
            content_within_parentheses = match.group(1)
            pattern_numbers = r'\d{4}'
            match_numbers = re.search(pattern_numbers, content_within_parentheses)
            if match_numbers:
                consecutive_numbers = match_numbers.group()
                return consecutive_numbers
        return None

    def get_authors(self, input_text: str) -> str:
        """Extract author names in proper BibTeX format

        Args:
            input_text = the entire citation
        Returns:
            author names in BibTeX format
        """
        string = ApaConverter.split_by_period(input_text)[0]
        authors = []
    
        string = string.split(' (', 1)[0]
        author_names = string.split('.,')
        num_authors = len(author_names)

        for i, author in enumerate(author_names):
            author = author.strip().replace('& ', '')
            if not author.endswith('.') and (num_authors > 1 or i > 0):
                author += '.'
            authors.append(author)

        return ' and '.join(authors)

    def get_publishers(self, input_text: str) -> str:
        """Extract publishers

        Args:
            input_text = the entire citation
        Returns:
            publisher, without location
        """
        string = ApaConverter.split_by_period(input_text)[2]
        location_publisher = string.split(':')
        if len(location_publisher) > 1:
            self.location = location_publisher[0].strip()
            return location_publisher[1].strip().replace('.', '')
        self.location = False
        return location_publisher[0].strip().replace('.', '')
    
    def get_journal(self, input_text: str) -> str:
        """Extract journal name

        Args:
            input_text = the entire citation
        Returns:
            journal name
        """
        string = ApaConverter.split_by_period(input_text)[2]
        string = string.split(',')
        if len(string) == 3:
            journal = string[0]
            volume = string[1]
            pages = string[2]
            return journal.strip(), volume.strip(), pages.strip().replace('.', '')
        if len(string) == 2:
            journal = string[0].strip().replace('.', '')
            output = string[1].strip().replace('.', '')
            return journal, output

        journal = string[0]
        return journal.strip().replace('.', '')

    @staticmethod
    def split_by_period(input_text):
        """Split citation by period

        Args:
            input_text = the entire citation
        Returns:   
            split strings
        """
        pattern = r'(?<=\S\S)\. '
        split_strings = re.split(pattern, input_text)
        return split_strings

    @staticmethod
    def remove_non_numeric_chars(input_string):
        """Remove non-numeric characters except hyphen, preserving hyphen between numbers
        Args:
            input_string: input string
        Returns:
            cleaned string
        """
        cleaned_string = re.sub(r'[^0-9-]', '', input_string)
        if '-' in cleaned_string:
            parts = cleaned_string.split('-')
            if all(part.isdigit() for part in parts):
                cleaned_string = '-'.join(parts)
        return cleaned_string

