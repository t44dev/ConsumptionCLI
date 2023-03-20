# General Imports
from tabulate import tabulate
from ..consumption_backend.Creators import Author

# Author
author_arg2db_mapping = {
    "id" : "author_id",
    "firstname" : "author_first_name",
    "lastname" : "author_last_name",
    "pseudonym" : "author_pseudonym"
}

author_arg2sortkey_mapping = {
    "id" : 0,
    "firstname" : 1,
    "lastname" : 2,
    "pseudonym" : 3
}

def author(*args, **kwargs) -> str:
    #print("Args: ", args, "Kwargs: ", kwargs)
    match kwargs:
        case {"list" : True}:
            query = dict()
            for key, value in author_arg2db_mapping.items():
                if kwargs[key]: query[value] = kwargs[key]
            sortkey = author_arg2sortkey_mapping[kwargs["order"]]
            authors = Author.find(**query)
            authors = sorted([[author.id, author.pseudonym, author.first_name, author.last_name] for author in authors], key=lambda x : x[sortkey])
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
