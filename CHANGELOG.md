# Changelog

All notable changes to this project will be documented in this file.
All issue numbers are relative to https://github.com/pywr-editor/editor


## v1.4.1 - 2023-03-18
### Added
- A red, purple or pink circle can now be set to customise the appearance of a schematic node
  ([#86](https://github.com/pywr-editor/editor/issues/86)).

### Changed
- Improved label and description of relative storage field in nodes. The editor now checks that the provided storage
  is between 0 and 1 ([#77](https://github.com/pywr-editor/editor/issues/77)).
- If the model title is changed, the window title is now updated to use the new
  model name ([#83](https://github.com/pywr-editor/editor/issues/83)).

### Fixed
- Fixed `TableValuesWidget` initialisation when widget uses multiple variables and the provided value is `None` 
  ([#79](https://github.com/pywr-editor/editor/issues/79)).
- When a node, with an already-set edge colour, is connected, the edge color is set to gray instead of the 
  preferred colour ([#81](https://github.com/pywr-editor/editor/issues/81)).
- Fixed Inno Setup installation script

## v1.4.0 - 2023-03-11
### Added
- Custom shapes can now be added onto the schematic (text, arrow and rectangle) using the node panel in the toolbar. Their
  appearance can also be customised and all shapes are stored in the JSON file
  ([#44](https://github.com/pywr-editor/editor/issues/44)).

### Changed
- Only unique values from a DataFrame index are not provided when setting up a table   
  ([#61](https://github.com/pywr-editor/editor/issues/61)).

### Fixed
- The Windows installer release did not build on GitHub actions due to a wrong file 
  pattern in the `.iss` config file ([#58](https://github.com/pywr-editor/editor/issues/58)).
- Fixed an exception when the dialog to open a new JSON file was disregarded   
  ([#59](https://github.com/pywr-editor/editor/issues/59)).
- Custom nodes could not be added on the schematic when dragged from the node panel   
  ([#64](https://github.com/pywr-editor/editor/issues/64)).
- When changing a nested parameter for a node, the "Save button" in the main form did not get enabled.
  Users were not able to save the node form ([#66](https://github.com/pywr-editor/editor/issues/66)).
- A tooltip in the parameter dialog was not rendering the node name ([#68](https://github.com/pywr-editor/editor/issues/68)).
- Allow users to input negative numbers when setting up a control curve ([#70](https://github.com/pywr-editor/editor/issues/70)).
- Fixed an exception when validating the form for `ControlCurvePiecewiseInterpolatedParameter` 
  ([#72](https://github.com/pywr-editor/editor/issues/72)).
- Fixed an exception when saving a recorder form ([#74](https://github.com/pywr-editor/editor/issues/74)).

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