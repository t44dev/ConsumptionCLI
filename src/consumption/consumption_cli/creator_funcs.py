# General Imports
from argparse import ArgumentParser
from tabulate import tabulate
from ..consumption_backend.Creators import Author

# Author
def author(parser : ArgumentParser, *args, **kwargs) -> str:
    subdict : dict = kwargs["subdict"]
    match kwargs:
        case {"list" : True}:
            sortkey =  kwargs["order"]
            # Thanks to Andrew Clark for solution to sorting list with NoneTypes https://stackoverflow.com/a/18411610
            if kwargs["reverse"]:
                authors = sorted(Author.find(**subdict), key = lambda a : (getattr(a, sortkey) is not None, getattr(a, sortkey)), reverse=True)
            else:
                authors = sorted(Author.find(**subdict), key = lambda a : (getattr(a, sortkey) is None, getattr(a, sortkey))) 
            authors = [[author.id, author.pseudonym, author.first_name, author.last_name] for author in authors]
            return str(tabulate(authors, headers=["#", "Pseudonym", "First Name", "Last Name"]))
        case {"update" : True}:
            if "id" not in subdict:
                parser.error("No author ID specified.")
            try:
                author = Author.get(subdict["id"])
            except TypeError:
                parser.error(f"Author with ID {subdict['id']} not found.")
            for key, value in subdict.items():
                setattr(author, key, value)
            author.save()
            return str(author)
        case {"delete" : True}:
            if "id" not in subdict:
                parser.error("No author ID specified.")
            Author.delete(subdict["id"])
            return "Author deleted."
        case {"create" : True}:
            author = Author(**subdict)
            author.save()
            return str(author)
        case _:
            parser.error("No action specified.")