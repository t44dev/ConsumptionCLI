# TODO LIST
### Features
#### High Priority
- [ ] Allow direct access from command-line on all platforms.
- [ ] Consumable Status: Planning/In Progress/On Hold/Finished/Rewatching/Reading
- [ ] Consider using only generalized Consumable instead of subclasses
- [ ] Novel/Movie/Comic/TV Series
- [ ] Migrate backend to new repo
#### Medium Priority
- [ ] Search consumables by staff
- [ ] Tags
- [ ] Brainstorm more sensible re-completion flow
- [ ] Staff list contains consumable information, e.g. count
#### Low Priority
- [ ] Characters & Character assignment
- [ ] Docstrings
- [ ] Subclass ArgumentParser for better Subdict action
- [ ] stdin reading when too few parameters given
- [ ] Advanced find (regex for strings)
- [ ] Advanced find (<, >, <=, >=, = for numerical values)
### Bugs/Problems
- [ ] Cant finish consumable without iterate flag set


### Finished
- [x] Features
    - [x] Append/Remove staff
    - [x] Multiple staff on a Consumable
    - [x] Single staff class with role field
    - [x] Allow update to progress
    - [x] In progress functionality
    - [x] Update general fields that don't require processing
    - [x] Update dates
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