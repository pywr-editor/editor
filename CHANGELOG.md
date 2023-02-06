# Changelog

All notable changes to this project will be documented in this file.
All issue numbers are relative to https://github.com/pywr-editor/editor

## v1.3.0 - 2023-02-06
### Added
- Added support for pywr-1.20.0. The editor (1) recognises the new `RollingMeanFlowNodeParameter`; (2) it makes the relative and 
  absolute initial volume optional when the maximum volume of a storage node is constant; and (3) it adds support for the 
  timestep offset in the `DataFrameParameter` and `TablesArrayParameter` ([#55](https://github.com/pywr-editor/editor/issues/55)).

### Changed
- The toolbar save button is not enabled using a Slot when a change is applied to the model. This was previously 
  implemented using a `QTimer` object ([#47](https://github.com/pywr-editor/editor/issues/47)).
- Properly style tooltips ([#51](https://github.com/pywr-editor/editor/issues/51)).

### Fixed
- The parameter and recorder icons are now properly scaled on any screen when used in `QlineEdit` or `QComboBox` 
  widgets ([#5](https://github.com/pywr-editor/editor/issues/5)).
- Any `Storage` node was recognised as `Reservoir` node. The node type is now visible in the node library and 
  properly identified in all widgets ([#53](https://github.com/pywr-editor/editor/issues/53)).


## v1.2.0 - 2023-01-02

### Added
- Added support for `WeightedAverageProfileParameter` (added in pywr-1.19.0) ([#3](https://github.com/pywr-editor/editor/issues/3)).
- The schematic now supports undo/redo operations of the following actions: add node, connect node, delete nodes, disconnect 
  node and move nodes ([#41](https://github.com/pywr-editor/editor/issues/41)). The undo/redo actions can be triggered by 
  clicking on the new toolbar buttons or using the keyword shortcuts for undo operations in your OS (`CTRL+Z` or `CTRL+Y` in Windows)
- The nodes on the schematic show a tooltip summarising all the node's properties ([#45](https://github.com/pywr-editor/editor/issues/45))

### Fixed
- Fixed item manipulation in `TableView` and `ListView` widgets. Selection in clear after an item is deleted or moved to
  prevent unexpected behaviours ([#30](https://github.com/pywr-editor/editor/issues/30))

### Changed
- When a modal dialog is open, inputs to the `MainWindow` are now blocked ([#36](https://github.com/pywr-editor/editor/issues/36))
- The save button in the toolbar is now enabled using a Slot instead of a `QTimer` object ([#47](https://github.com/pywr-editor/editor/issues/47))

## v1.1.0 - 2022-12-17

### Fixed
- Prevent the editor from crashing when user was asked to save the model file on exit ([#11](https://github.com/pywr-editor/editor/issues/11))
- Check if Microsoft Excel is installed. If it is not, the import/export buttons, available in some widgets, will now be hidden ([#15](https://github.com/pywr-editor/editor/issues/15))
- The file names, in the recent project list in the welcome screen, were clipped ([#17](https://github.com/pywr-editor/editor/issues/17))
- When the editor was launched with the option to generate the debug/log file, the file was saved in the wrong path ([#19](https://github.com/pywr-editor/editor/issues/19))
- Prevent the editor from crashing when the model dictionary, loaded from a JSON file, does not have the "table" key ([#21](https://github.com/pywr-editor/editor/issues/21))

## v1.0.0
- This is the first release of pywr editor