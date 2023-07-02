# ConsumptionCLI

## About
Written in Python, **ConsumptionCLI** is a lightweight command line interface tool for keeping track of various types of media. It acts as a simpler alternative to services such as *goodreads* and *bookmeter* for Novels or *IMDb* and *Letterboxd* for TV Shows and Movies. It also provides enough flexibiltiy to keep track of any number of other formats.

## Installation
### Method 1. pip install (Recommended)
#### Requirements
- Python 3+
- pip

```console
$ pip install consumptioncli
```
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

## Basic Usage

### Create

**ConsumptionCLI** includes the ability to create, manage and view 2 distinct types of entities (Consumables and Staff) with 4 different actions. The most basic usage involves first creating a Consumable:

```console
$ cons --create consumable --name 1984 --type NOVEL
  #    ID  Type      Name    Major    Minor  Rating      Completions  Status    Started    Completed
---  ----  ------  ------  -------  -------  --------  -------------  --------  ---------  -----------
  1     1  NOVEL     1984        0        0                        0  PLANNING
```
On creation of a Consumable a table containing the values associated with the new Consumable including the type of media and name along with other properties. Each of these properties can be adjusted manually using the appropriate flags (e.g. --rating NUMBER).

Shorthand also exists and so the following input produces the same result:

```console
$ cons -c c -n 1984 -t NOVEL
  #    ID  Type      Name    Major    Minor  Rating      Completions  Status    Started    Completed
---  ----  ------  ------  -------  -------  --------  -------------  --------  ---------  -----------
  1     1  NOVEL     1984        0        0                        0  PLANNING
```
> Note that for flags/options consisting of a single character only a single hyphen prefix (-) is used while longer form flags/options use a double-hyphen prefix (--). This remains true for shorthand flags/options that still make use of multiple characters such as the shorthand for ```--startdate``` which is ```--sd```.

### Update

There are 5 statuses that can be associated with any one Consumable including ```PLANNING```,```IN_PROGRESS```,```ON_HOLD```, ```DROPPED``` and ```COMPLETED```. By default Consumables are set in the ```PLANNING``` stage but can be updated manually:

```console
$ cons --update consumable --id 1 --status IN_PROGRESS
  #    ID  Type      Name    Major    Minor  Rating      Completions  Status       Started     Completed
---  ----  ------  ------  -------  -------  --------  -------------  -----------  ----------  -----------
  1     1  NOVEL     1984        0        0                        0  IN_PROGRESS  2023/01/01
```

Date's are largely handled by the system automatically and setting the status of a Consumable to ```IN_PROGRESS``` which does not have an associated start date will automatically set it to present day. Alternatively, an update can be performed using the ```--continue``` flag.

```console
$ cons --update consumable --id 1 --continue --major 2 --minor 5
  #    ID  Type      Name    Major    Minor  Rating      Completions  Status       Started     Completed
---  ----  ------  ------  -------  -------  --------  -------------  -----------  ----------  -----------
  1     1  NOVEL     1984        2        5                        0  IN_PROGRESS  2023/01/01
$ cons --update consumable --id 1 --continue --major 2 --minor 5
  #    ID  Type      Name    Major    Minor  Rating      Completions  Status       Started     Completed
---  ----  ------  ------  -------  -------  --------  -------------  -----------  ----------  -----------
  1     1  NOVEL     1984        4       10                        0  IN_PROGRESS  2023/01/01
```

Which sets the status to ```IN_PROGRESS``` while also flagging the system to increment the *Major* and *Minor* fields instead of simply setting them (Note that repeated use of the same command increments these fields each time in the above example). These fields are intended to be used for tracking things like Volumes/Seasons and Chapters/Episodes respectively.

When marking a Consumable as complete it is expected that the ```--finish``` flag is used:

```console
$ cons --update consumable --id 1 --finish --rating 8.3
  #    ID  Type      Name    Major    Minor    Rating    Completions  Status     Started     Completed
---  ----  ------  ------  -------  -------  --------  -------------  ---------  ----------  -----------
  1     1  NOVEL     1984        4       10       8.3              1  COMPLETED  2023/01/01  2023/01/02
```

Which will set the status to ```COMPLETED```, increment completions and mark the end date as present day if this is the first completion of the Consumable. Additionally a rating can be added, although this can also be added at any point.

> Note that if you want to update the date fields manually the default format is **YYYY/mm/dd**. As a result this format should be used when specifying a date using the ```--startdate``` and ```--enddate``` options. Alternatively a different date format can be supplied using ```--dateformat```. E.g. ```--dateformat %d-%m-%Y```.

### Delete
Consumables can also be deleted by their unique id:

```console
$ cons --delete c --id 1
Consumable deleted.
```

### List
All consumables, or a subset according to some search parameters, can be viewed using the list action. The most basic example is to provide no paramaters and simply view all results:

```console
$ cons --list consumable
  #    ID  Type    Name                     Major    Minor    Rating    Completions  Status       Started     Completed
---  ----  ------  ---------------------  -------  -------  --------  -------------  -----------  ----------  -----------
  1     1  NOVEL   1984                         4       10       8.3              1  COMPLETED    2023/07/02  2023/07/02
  2     7  NOVEL   A Tale of Two Cities        19       94       7                5  COMPLETED    1994/11/26  1996/03/22
  3     5  MOVIE   Avatar                      19       19       5.3              2  COMPLETED    2002/12/17  2003/09/01
  4     8  TV      Breaking Bad                20      198                        0  DROPPED      2014/02/18
  5    10  MOVIE   Jurassic Park               19      182                        0  IN_PROGRESS  1998/03/03
  6     3  MOVIE   Pulp Fiction                 9      200       7.6              2  COMPLETED    2016/06/11  2016/08/19
  7     4  NOVEL   The Hobbit                  25       58                        0  DROPPED      2011/06/22
  8     6  TV      The Office                  24      179                        0  IN_PROGRESS  2018/08/06
  9     2  TV      The Simpsons                 3       90                        0  DROPPED      2022/12/24
 10     9  NOVEL   To Kill a Mockingbird        7       93                        0  PLANNING
 11    11  NOVEL   War and Peace                0        0                        0  PLANNING
11 Results...
```

By default the listed Consumables are ordered by name however the ordering can be changed using ```--order``` (and ```--reverse``` to reverse the order):

```console
$ cons --list consumable --order rating --reverse
  #    ID  Type    Name                     Major    Minor    Rating    Completions  Status       Started     Completed
---  ----  ------  ---------------------  -------  -------  --------  -------------  -----------  ----------  -----------
  1     1  NOVEL   1984                         4       10       8.3              1  COMPLETED    2023/07/02  2023/07/02
  2     3  MOVIE   Pulp Fiction                 9      200       7.6              2  COMPLETED    2016/06/11  2016/08/19
  3     7  NOVEL   A Tale of Two Cities        19       94       7                5  COMPLETED    1994/11/26  1996/03/22
  4     5  MOVIE   Avatar                      19       19       5.3              2  COMPLETED    2002/12/17  2003/09/01
  5     2  TV      The Simpsons                 3       90                        0  DROPPED      2022/12/24
  6     4  NOVEL   The Hobbit                  25       58                        0  DROPPED      2011/06/22
  7     6  TV      The Office                  24      179                        0  IN_PROGRESS  2018/08/06
  8     8  TV      Breaking Bad                20      198                        0  DROPPED      2014/02/18
  9     9  NOVEL   To Kill a Mockingbird        7       93                        0  PLANNING
 10    10  MOVIE   Jurassic Park               19      182                        0  IN_PROGRESS  1998/03/03
 11    11  NOVEL   War and Peace                0        0                        0  PLANNING
 ```

And the entries listed can be filtered using the same attributes specified in the create and update actions.
```console
$ cons --list consumable --type NOVEL
  #    ID  Type    Name                     Major    Minor    Rating    Completions  Status     Started     Completed
---  ----  ------  ---------------------  -------  -------  --------  -------------  ---------  ----------  -----------
  1     1  NOVEL   1984                         4       10       8.3              1  COMPLETED  2023/07/02  2023/07/02
  2     7  NOVEL   A Tale of Two Cities        19       94       7                5  COMPLETED  1994/11/26  1996/03/22
  3     4  NOVEL   The Hobbit                  25       58                        0  DROPPED    2011/06/22
  4     9  NOVEL   To Kill a Mockingbird        7       93                        0  PLANNING
  5    11  NOVEL   War and Peace                0        0                        0  PLANNING
5 Results...
```

### More
#### Help
A concise overview of all the possibilities can be viewed using the ``--help`` flag.

```console
$ cons --help
$ cons --create consumable --help
```

#### Staff Entity
Another entity, besides the Consumable entity type, exists and can be created, updated, deleted and listed in the same way. This is the Staff entity and can be tied to specific Consumables under a certain role. This is intended to be used to associate Authors, Directors, Illustrators, etc. with their works. Note that staff functionality is still somewhat limited besides the basic actions and the ability to add them to Consumables. However, this should change in the future.
