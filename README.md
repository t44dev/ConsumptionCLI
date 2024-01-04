# ConsumptionCLI

![PyPI - Version](https://img.shields.io/pypi/v/consumptioncli) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/consumptioncli) ![GitHub commit activity (branch)](https://img.shields.io/github/commit-activity/t/track-44/consumptioncli) ![GitHub repo size](https://img.shields.io/github/repo-size/track-44/consumptioncli) ![PyPI - License](https://img.shields.io/pypi/l/consumptioncli) 


## About
Written in Python, **ConsumptionCLI** is a lightweight command line interface tool for keeping track of various types of media. It acts as a simpler alternative to services such as *goodreads* and *bookmeter* for Novels or *IMDb* and *Letterboxd* for TV Shows and Movies. It also provides enough flexibiltiy to keep track of any number of other formats.

## Installation
### Method 1. pip install (Recommended)
#### Requirements
- Python 3+
- pip

1. Execute the follwoing:
```console
$ pip install consumptioncli
```
2. You're Done!

### Method 2. Self Build
#### Requirements

- Python 3+
- pip
- [PyPa's *build* frontend](https://github.com/pypa/build) 
- [consumptionbackend](https://github.com/track-44/consumptionbackend)

#### Steps

> The same steps can be followed for **consumptionbackend** and should be done so beforehand as **ConsumptionCLI** is dependent on it.

1. Clone the repository and navigate inside 
2. Execute the following:
```console
$ py -m build
$ pip install .
```

3. You're Done!

## Basic Usage
**ConsumptionCLI** includes 3 different entities:
- *Consumables* - Main entity type and are intended to represent things such as Movies, TV Shows, Novels, etc. However, they can be used for whatever purposes you desire.
- *Series* - Secondary entity. Each *Consumable* can be affiliated with one of these. Intended to represent an entire series, for example if a TV Show has multiple seasons each season may be represented with its own *Consumable* and all of these *Consumables* may be attached to the same *Series*.
- *Personnel* - Secondary entity. Can be affiliated with *Consumables* along with some role such as Author, Illustrator, etc.

There are 4 main actions that can be performed on each of these entities. Namely *New*, *Update*, *Delete* and *List*. More detail on these actions is given in the sections below.

### New

Concerned with the creation of entities. An example on how to create a *Consumable* is given below:

```console
$ cons consumable new --name 1984 --type NOVEL
  #    ID  Type      Name  Parts    Rating      Completions  Status    Started    Completed
---  ----  ------  ------  -------  --------  -------------  --------  ---------  -----------
  1     1  NOVEL     1984  0/?                            0  PLANNING
```

Observe that on creation of a *Consumable* a table containing the values associated with the new *Consumable* including the type of media and name along with other properties is displayed. Each of these properties can be adjusted manually using the appropriate flags (e.g. `--rating NUMBER`). 

Some fields can be ommited and are filled with sensible defaults while others, such as `name` and `type` in the case of *Consumables*, are required and will be prompted for if not provided initially.

Creation of *Series* and *Personnel* can be done with `series` and `personnel` in place of `consumable` respectively. 

Shorthand also exists and so the following input produces the same result:

```console
$ cons c n -n 1984 -t NOVEL
  #    ID  Type      Name  Parts    Rating      Completions  Status    Started    Completed
---  ----  ------  ------  -------  --------  -------------  --------  ---------  -----------
  1     1  NOVEL     1984  0/?                            0  PLANNING
```
> Note that for flags/options consisting of a single character only a single hyphen prefix (-) is used while longer form flags/options use a double-hyphen prefix (--). This remains true for shorthand flags/options that still make use of multiple characters such as the shorthand for ```--startdate``` which is ```--sd```.

### Update

All the fields for each of the entities can be changed using the update action. Note that there are some constraints on how these can be changed in order to prevent invalid states and help maintain consistency but in general the system is very flexible. 

One main reason you may want to update a *Consumable* is to change the status. There are 5 statuses that can be associated with any one *Consumable* including ```PLANNING```,```IN_PROGRESS```,```ON_HOLD```, ```DROPPED``` and ```COMPLETED```. By default *Consumables* are set in the ```PLANNING``` stage. Updating can be performed through the following:

```console
$ cons consumable update --name 1984 set --status IN_PROGRESS --parts 2
  #    ID  Type      Name  Parts    Rating      Completions  Status       Started     Completed
---  ----  ------  ------  -------  --------  -------------  -----------  ----------  -----------
  1     1  NOVEL     1984  2/?                            0  IN_PROGRESS  2023/11/30
```

Observe that we first specify some search paramaters by which to find the *Consumable(s)* we are looking to update and then using the keyword `set` specify the updates we want to make. In this case the status has been set to ```IN_PROGRESS``` and the number of parts set to 2; which could represent chapters read in this case.

Note that if multiple *Consumables* match the search conditions then you will be prompted to confirm the update of each one. Additionally, fields such as names are not case-sensitive and only have to include part of the entire string allowing easy mass updating of related entities (e.g. setting the same series for multiple *Consumables*). 

Dates are largely handled by the system automatically and setting the status of a *Consumable* to ```IN_PROGRESS``` which does not have an associated start date will automatically set it to present day. 

> Note that if you want to update the date fields manually the default format is **YYYY/mm/dd**. As a result this format should be used when specifying a date using the ```--startdate``` and ```--enddate``` options. Alternatively a different date format can be supplied using ```--dateformat```. E.g. ```--dateformat %d-%m-%Y```.

### Delete
*Consumables* can also be deleted by any field:

```console
$ cons consumable delete --name 1984
1 Consumable(s) deleted.
```

The same logic applies to deletions as does to updates in terms of search paramaters. Again, confirmation of deletion will be required when multiple entities match the search parameters.

### List
All *Consumables*, or a subset according to some search parameters, can be viewed using the list action. The most basic example is to provide no paramaters and simply view all results. By default this opens an interactive session which can be scrolled through using the keyboard:

```console
cons consumable list
    #    ID  Type    Name                   Parts      Rating    Completions  Status       Started     Completed
  ---  ----  ------  ---------------------  -------  --------  -------------  -----------  ----------  -----------
>   1     1  NOVEL   1984                   23/23         8.3              1  COMPLETED    2023/07/02  2023/07/02 <
    2     2  NOVEL   A Tale of Two Cities   45/45         7                5  COMPLETED    1994/11/26  1996/03/22
    3     3  MOVIE   Avatar                 1/1           5.3              2  COMPLETED    2002/12/17  2002/12/17
    4     4  TV      Breaking Bad           35/?                           0  DROPPED      2011/06/22
    5     5  MOVIE   Jurassic Park          0/?                            0  IN_PROGRESS  1998/03/03
    6     6  MOVIE   Pulp Fiction           7/7           7.6              2  COMPLETED    2016/06/11  2016/08/19
    7     7  NOVEL   The Hobbit             10/?                           0  DROPPED      2011/06/22
    8     9  TV      The Office             101/?                          0  IN_PROGRESS  2018/08/06
    9     8  TV      The Simpsons           234/?                          0  DROPPED      2022/12/24

[K/↑] Up   [J/↓] Down   [Enter] Select   [Q] Quit
```

By default the listed *Consumables* are ordered by name however the ordering can be changed using ```--order``` (and ```--reverse``` to reverse the order):

```console
$ cons consumable list --order rating --reverse
    #    ID  Type    Name                   Parts      Rating    Completions  Status       Started     Completed
  ---  ----  ------  ---------------------  -------  --------  -------------  -----------  ----------  -----------
>   1     1  NOVEL   1984                   23/23         8.3              1  COMPLETED    2023/07/02  2023/07/02 <
    2     6  MOVIE   Pulp Fiction           7/7           7.6              2  COMPLETED    2016/06/11  2016/08/19
    3     2  NOVEL   A Tale of Two Cities   45/45         7                5  COMPLETED    1994/11/26  1996/03/22
    4     3  MOVIE   Avatar                 1/1           5.3              2  COMPLETED    2002/12/17  2002/12/17
    5     4  TV      Breaking Bad           35/?                           0  DROPPED      2011/06/22
    6     5  MOVIE   Jurassic Park          0/?                            0  IN_PROGRESS  1998/03/03
    7     7  NOVEL   The Hobbit             10/?                           0  DROPPED      2011/06/22
    8     8  TV      The Simpsons           234/?                          0  DROPPED      2022/12/24
    9     9  TV      The Office             101/?                          0  IN_PROGRESS  2018/08/06

[K/↑] Up   [J/↓] Down   [Enter] Select   [Q] Quit
 ```

And the entries listed can be filtered using the same attributes specified in the new and update actions.
```console
$ cons consumable list --type NOVEL
    #    ID  Type    Name                   Parts      Rating    Completions  Status     Started     Completed
  ---  ----  ------  ---------------------  -------  --------  -------------  ---------  ----------  -----------
>   1     1  NOVEL   1984                   23/23         8.3              1  COMPLETED  2023/07/02  2023/07/02 <
    2     2  NOVEL   A Tale of Two Cities   45/45         7                5  COMPLETED  1994/11/26  1996/03/22
    3     7  NOVEL   The Hobbit             10/?                           0  DROPPED    2011/06/22
    4    10  NOVEL   To Kill a Mockingbir.  0/?                            0  PLANNING
    5    11  NOVEL   War and Peace          0/?                            0  PLANNING

[K/↑] Up   [J/↓] Down   [Enter] Select   [Q] Quit
```

#### List Actions

In addition to being able to traverse the interactive list other actions such as updating and deleting selected entries, attaching *Series* or *Personnel* to *Consumable(s)*, managing tags and viewing more info of an entry can be done using the various given button prompts at the bottom of the listing. 

The **View Info** action is significant as it can be used to see additional information on an entry that is not presented in the compact list view such as *Series* and associated *Personnel* for a *Consumable*. This action itself allows viewing of this information from another interactive session:

```console
Info───────────────────────────────────────────────────────┐Personnel──────────────────────────────────────────────────┐
│#1 "1984"                                                 ││> [author] George Orwell <                                │
│NOVEL - No Series                                         ││  [publisher] "Secker & Warburg"                          │
│                                                          ││                                                          │
│23/23 parts, 1 Completion(s)                              ││                                                          │
│COMPLETED, 2023/07/02 - 2023/07/02                        ││                                                          │
│                                                          ││                                                          │
│Tag(s): 1949 english                                      ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││[K/↑] Up   [J/↓] Down   [Enter] Select   [A] Deselect All │
│                                                          ││[R] Remove Selected   [Q] Quit                            │
└──────────────────────────────────────────────────────────┘└──────────────────────────────────────────────────────────┘
```

### More
#### Help
While these are the most significant ther are other possibilities. Specifically for *Consumables* there are many more actions that further streamline adding *Personnel*, assigning a *Series* and tagging. These possibilities and more can be explored using the ``--help`` flag after any given command or partial command.

```console
$ cons --help
$ cons consumable new --help
```