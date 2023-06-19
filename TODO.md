# TODO LIST
### Features
#### High Priority
- [ ] Tie data integrity constraints more to the backend than frontend with appropriate errors being sent and handled for bad data.
#### Medium Priority
- [ ] Search consumables by staff
- [ ] Tags
- [ ] Brainstorm more sensible re-completion flow
- [ ] Staff list contains consumable information, e.g. count
- [ ] Row number in list
- [ ] Log file
- [ ] Display all information on update
- [ ] --continue flag should set status to IN_PROGRESS
#### Low Priority
- [ ] Characters & Character assignment
- [ ] Docstrings
- [ ] Subclass ArgumentParser for better Subdict action
- [ ] stdin reading when too few parameters given
- [ ] Advanced find (regex for strings)
- [ ] Advanced find (<, >, <=, >=, = for numerical values)
### Bugs/Problems
- [ ] Start date possible after end date
- [ ] Can't undo startdate

### Finished
- [x] Features
    - [x] Consider using only generalized Consumable instead of subclasses - Implemented this method
    - [x] Migrate backend to new repo
    - [x] Consumable Status: Planning/In Progress/On Hold/Finished/Rewatching/Reading
    - [x] Append/Remove staff
    - [x] Multiple staff on a Consumable
    - [x] Single staff class with role field
    - [x] Allow update to progress
    - [x] In progress functionality
    - [x] Update general fields that don't require processing
    - [x] Update dates
    - [x] Allow direct access from command-line on all platforms.
- [x] Code Cleanliness
    - [x] Don't repeat code across classes for database operations
    - [x] No SQL in non-database classes
    - [x] General DatabaseHandler for usage of multiple DB solutions
- [x] Tests
    - [x] Novel Tests
    - [x] Database Tests
    - [x] Staff Tests
- [x] Basic Backend Classes
    - [x] DatabaseEntity
    - [x] DatabaseHandler
    - [x] Consumable
    - [x] Novel Backend
    - [x] Staff Backend
- [x] Bugs/Problems
    - [x] Cant finish consumable without iterate flag set
    - [x] Consumable created as COMPLETED does not set completions = 1 by default
    - [x] Fixed logic error with increment always occuring even when not set in update of consumable