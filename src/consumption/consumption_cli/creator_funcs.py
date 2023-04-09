# General Imports
from tabulate import tabulate
from ..consumption_backend.Creators import Author

# Author
author_arg2class_mapping = {
    "id" : "id",
    "firstname" : "first_name",
    "lastname" : "last_name",
    "pseudonym" : "pseudonym"
}

def author(*args, **kwargs) -> str:
    print("Args: ", args, "Kwargs: ", kwargs)
    match kwargs:
        case {"list" : True}:
            sortkey = author_arg2class_mapping[kwargs["order"]]
            authors = sorted(Author.find(**kwargs["subdict"]), key = lambda a : getattr(a, sortkey))
            authors = [[author.id, author.pseudonym, author.first_name, author.last_name] for author in authors]
            return str(tabulate(authors, headers=["#", "Pseudonym", "First Name", "Last Name"]))
        case {"update" : True}:
            print("update")
        case {"delete" : True}:
            print("delete")
        case {"create" : True}:
            author = kwargs_to_author(kwargs)
            if not author.first_name and not author.last_name and not author.pseudonym:
                raise TypeError("No values specified for Author.")
            else:
                author.save()
                return str(author)
        case _:
            raise ValueError("No action specified.")

def kwargs_to_author(kwargs : dict) -> Author:
    return Author(id=kwargs["id"], first_name=kwargs["firstname"], last_name=kwargs["lastname"], pseudonym=kwargs["pseudonym"])
