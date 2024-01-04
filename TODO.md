# TODO LIST
## Current
- [x] Force flag on update and delete
- [x] "View" page for entities
- [x] Expand interactive list actions
- [x] Log file
- [x] Add badges/shields to README
- [x] Update readme
- [x] Update version
- [x] Update the version change script
- [x] Allow setting of NoneType for max_parts
- [x] Tag Search should be an AND not an OR over the searched tags

- [x] ListAction class
- [x] Classes in parsers.py for better SOC

## Next
- [ ] Adaptive name truncation
- [ ] Meaningful Boolean returns
- [ ] Handle window resize curses
- [ ] List all tags
- [ ] Delete returns deleted records
- [ ] Dataclasses/Attrs
- [ ] Further Tests
- [ ] SQL to dedicated script file that is read from
- [ ] Turn on type-checking and fix type-hint inconsistencies
- [ ] Use sentinels library instead of own SentinelClass implementation
- [ ] More info in list view about the selection (e.g. average rating)
- [ ] Fix Bugs
    - [ ] Completion doesn't set parts to max_parts
    - [ ] Completion doesn't set start date
    - [ ] Normalize "None" values e.g. Null, None, ?
    - [ ] Mismatched date timezones
- [ ] Add to Details Window
    - [ ] Number of Personnel attached to Consumable
    - [ ] Number of consumables attached to Series
    - [ ] Number of Consumables attached to Personnel
    - [ ] Refresh details after list action