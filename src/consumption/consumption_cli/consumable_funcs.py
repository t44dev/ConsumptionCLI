# General Imports
from argparse import ArgumentParser
from tabulate import tabulate
from ..consumption_backend.Consumables import Novel
from datetime import datetime

def novel(parser : ArgumentParser, *args, **kwargs) -> str:
    # print("Args: ", args, "Kwargs: ", kwargs)
    subdict : dict = kwargs["subdict"]
    match kwargs:
        case {"list" : True}:
            sortkey =  kwargs["order"]
            # Thanks to Andrew Clark for solution to sorting list with NoneTypes https://stackoverflow.com/a/18411610
            if kwargs["reverse"]:
                novels = sorted(Novel.find(**subdict), key = lambda a : (getattr(a, sortkey) is not None, getattr(a, sortkey)), reverse=True)
            else:
                novels = sorted(Novel.find(**subdict), key = lambda a : (getattr(a, sortkey) is None, getattr(a, sortkey))) 
            novels = [[novel.id, novel.name, novel.major_parts, novel.minor_parts, novel.rating, novel.completions, novel.start_date, novel.end_date] for novel in novels]
            return str(tabulate(novels, headers=["#", "Name", "Volumes", "Chapters", "Rating", "Completions", "Started", "Completed"]))
        case {"update" : True}:
            if "id" not in subdict:
                parser.error("No novel ID specified.")
            try:
                novel = Novel.get(subdict["id"])
            except TypeError:
                parser.error(f"Novel with ID {subdict['id']} not found.")
            # Add Volumes, Chapters, set End Date
            if kwargs["finish"]:
                novel.end_date = datetime.utcnow()
            if kwargs["read"]:
                subdict["major_parts"] = novel.major_parts + (subdict["major_parts"] if "major_parts" in subdict else 0)
                subdict["minor_parts"] = novel.minor_parts + (subdict["minor_parts"] if "minor_parts" in subdict else 0)
            # Update Values
            for key, value in subdict.items():
                setattr(novel, key, value)
            novel.save()
            return str(novel)
        case {"delete" : True}:
            if "id" not in subdict:
                parser.error("No novel ID specified.")
            Novel.delete(subdict["id"])
            return "Novel deleted."
        case {"create" : True}:
            novel = Novel(**subdict)
            novel.save()
            return str(novel)
        case _:
            parser.error("No action specified.")