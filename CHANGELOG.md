# Changelog

All notable changes to this project will be documented in this file.
All issue numbers are relative to https://github.com/pywr-editor/editor


## v2.1 - 2024-02-18
### Fixed
- Disable action buttons (move and delete) after adding a new control curve. This prevents the editor from
crashing when no item is selected in the widget ([#202](https://github.com/pywr-editor/editor/issues/202))
- If the model has changes and is reloaded, two save prompts used to be displayed ([#212](https://github.com/pywr-editor/editor/issues/212))
- When user clicks on a searched item in the global search, no action is triggered ([#214](https://github.com/pywr-editor/editor/issues/214))
- Scroll with the mouse wheel was too slow in the panel used to add new nodes and shapes ([#216](https://github.com/pywr-editor/editor/issues/216))

### Changed
- Updated dependencies ([#197](https://github.com/pywr-editor/editor/issues/197))
- The list of model parameters are now alphabetically sorted in the UI dropdown menus ([#205](https://github.com/pywr-editor/editor/issues/204))
- To improve user experience dialogs are automatically closed after a form is saved ([#208](https://github.com/pywr-editor/editor/issues/208))

### Added
- Added ability to clone a node from the schematic. By right-clicking on a node and pressing "Clone" the node and 
its model is configuration are cloned. The new node is assigned a random name ([#205](https://github.com/pywr-editor/editor/issues/204))
- Updated support for pywr to 1.23. The `loss_factor `in `LossLink `can now be provided as a parameter ([#210](https://github.com/pywr-editor/editor/issues/210))
- Users can now double click on a schematic item (node or shape) to edit it ([#214](https://github.com/pywr-editor/editor/issues/214))
- When selecting a named parameter or recorder from a dropdown, display its configuration in a tooltip ([#220](https://github.com/pywr-editor/editor/issues/220))
- Double click on a model component (recorder or parameter) to edit it in a list or table widget ([#222](https://github.com/pywr-editor/editor/issues/222))
- Listen for changes to the JSON file made externally (for example using a text editor). If there are any, the 
 editor will be reloaded to include the new changes ([#224](https://github.com/pywr-editor/editor/issues/224))


## v2.0.3 - 2023-08-19
### Fixed
- Negative costs could not be input for a `ControlCurvePiecewiseInterpolatedParameter`([#191](https://github.com/pywr-editor/editor/issues/191))
- Allow floats in the RBF bounds in the optimisation section ([#193](https://github.com/pywr-editor/editor/issues/193))
- When pywr is running and the inspector tree is open, the editor crashed due to a wrong function signature ([#195](https://github.com/pywr-editor/editor/issues/195))

### Changed
- Distributed application will now contain `pywr-1.21.0` and `Qt-6.5.2` ([#197](https://github.com/pywr-editor/editor/issues/197))


## v2.0.2 - 2023-07-29
### Fixed
- Fixed import of `tables` module in the GitHub pipeline ([#186](https://github.com/pywr-editor/editor/issues/186))
- Some dictionary keys of a nested `ConstantParameter` were dropped when the parameter configuration was saved ([#188](https://github.com/pywr-editor/editor/issues/188))
- The editor version in the Windows installer setup is updated during a release

## v2.0.1 - 2023-05-31
### Fixed
- The frozen application and installer did not include some imports needed by pywr ([#183](https://github.com/pywr-editor/editor/issues/183)).

## v2.0.0 - 2023-05-29
### Added
- Pywr is now bundled with the editor, and you can run and debug your model using the new Toolbar `Run` tab. You can also change the start, end date, timestep as well as run and pause the model to a specific date ([#122](https://github.com/pywr-editor/editor/issues/122))

### Changed
- The code of some classes have been improved ([PR #176](https://github.com/pywr-editor/editor/pull/176), [PR #177](https://github.com/pywr-editor/editor/pull/177), [PR #181](https://github.com/pywr-editor/editor/pull/181)) 
- Qt 6.5 is now required ([PR #175](https://github.com/pywr-editor/editor/pull/175))

### Fixed
- When values in `ControlCurvePiecewiseInterpolatedParameter` were provided as nested lists, the values were not transposed and were assigned to the wrong control curve. The parameter form now also shows a new column in the control curve and value fields to easily map and assign the values to each area defined by the control curves ([#173](https://github.com/pywr-editor/editor/issues/173)).
- If one or more nodes did not have the `position` attribute, the editor showed a warning message every time the schematic was reloaded. The message is now shown only when the schematic is first initialised. ([#178](https://github.com/pywr-editor/editor/issues/178)).


## v1.6.0 - 2023-04-02
### Added
- Added support to multi-line comments ([#146](https://github.com/pywr-editor/editor/issues/146)).
- Add icons to contextual menu actions and fixed menu style on right-click menu on form inputs ([#159](https://github.com/pywr-editor/editor/issues/159)).
- Added node icons in contextual menu. When you right-click on a node to change an edge, the contextual menu now shows the node icons to easily identify the node to connect or disconnect ([#166](https://github.com/pywr-editor/editor/issues/166)).

### Changed
- The window title now shows the model name first  ([#170](https://github.com/pywr-editor/editor/issues/170)).
- Open the start screen when user click on the "Open model file" button in the toolbar ([#153](https://github.com/pywr-editor/editor/issues/153)).
- The message box, after a validation tool is run, displays a different icon if the model validation is successful ([#155](https://github.com/pywr-editor/editor/issues/155)).
- The fields to select multiple nodes and parameters are now disabled if there are no nodes or parameters in the model ([#163](https://github.com/pywr-editor/editor/issues/163)).

### Fixed
- Fixed an exception when a H5 file has columns cast as integers ([#157](https://github.com/pywr-editor/editor/issues/157)).
- Fixed exception file logging when the exception hook creates a string instead of an Exception object ([#165](https://github.com/pywr-editor/editor/issues/165)).
- The metadata field in the table recorder is now optional ([#160](https://github.com/pywr-editor/editor/issues/160)).

## v1.5.1 - 2023-03-29
### Added
- A new reload button was added to the toolbar to reload the JSON file in case it was externally edited ([#148](https://github.com/pywr-editor/editor/issues/148)).
- Added comment field in the form of RBF parameter ([#126](https://github.com/pywr-editor/editor/issues/126)).

### Changed
- The width of form widgets handling float numbers have been shrank. Some fields also now restrict the value to a specific range (for ex `initial_volume_pc` is now constrained between 0 and 1) ([#144](https://github.com/pywr-editor/editor/issues/144)).
- When cloning a recorder or parameter, the latest saved configuration is now used ([#138](https://github.com/pywr-editor/editor/issues/138)).
- Integers are now allowed in the upper and lower bounds of a RBF parameter. Previously only a list of integers was allowed ([#136](https://github.com/pywr-editor/editor/issues/136)). 
- Increased the minimum width of the parameter dialog to hide the horizontal scrollbar in the scrollable area of the form. Some forms are too large to properly fit into the child widget. ([#127](https://github.com/pywr-editor/editor/issues/127)).

### Fixed
- When a parameter or recorder, sharing the same name of a node, was renamed, the node name was being replaced in 
  the `edges` as well ([#142](https://github.com/pywr-editor/editor/issues/142)).  
- To prevent duplicated entries, the paths in the recent projects are now normalised ([#140](https://github.com/pywr-editor/editor/issues/140)).
- Fixed appearance of ComboBox icon with tables. The icon appeared too large on some screens ([#134](https://github.com/pywr-editor/editor/issues/134)).
- Fixed validation of custom parameters when user attempted to add a table in the dictionary ([#132](https://github.com/pywr-editor/editor/issues/132)).
- Fixed validation of RBF parameter when the day field is empty or invalid. The form used to throw a TypeError exception ([#128](https://github.com/pywr-editor/editor/issues/128)).

## v1.5 - 2023-03-27
### Added
- The configuration of a selected recorder or parameter can now be copied as a new recorder or parameter by using the 
  "Clone" button in the dialogs ([#115](https://github.com/pywr-editor/editor/issues/115)).
- New icons (QtAwesome) have been added to all buttons to improve design and UI accessibility
  ([#117](https://github.com/pywr-editor/editor/issues/117)).
- Tables in the tree widget now display an icon depending on the table type ([#119](https://github.com/pywr-editor/editor/issues/119)).
- A new search functionality was added. Users can now search and quickly edit nodes, parameters, tables and recorders 
  by clicking on the "Search" button in the toolbar or pressing `CTRL+F` ([#123](https://github.com/pywr-editor/editor/issues/123)).

## v1.4.3 - 2023-03-25
### Changed
- Parameter, recorder, scenarios and tables are now sorted by name in the setting dialogs
  The components can now be easily identified in the left-hand side widget in the modal dialogs.
  ([#107](https://github.com/pywr-editor/editor/issues/107)). 
- Improve description of threshold parameters ([#109](https://github.com/pywr-editor/editor/issues/109)).
- Colour contrasts and some layouts have been changed to improve accessibility. 
  Tables also display an icon next to their names to identify the file extension
  ([#111](https://github.com/pywr-editor/editor/issues/111)).

### Fixed
- Fixed the form attribute name identifying the storage node in `MinimumVolumeStorageRecorder`. The recorder uses `node`
  instead of `storage` ([#105](https://github.com/pywr-editor/editor/issues/105)).

## v1.4.2 - 2023-03-20
### Changed
- Recent projects in the start screen are now sorted by date ([#89](https://github.com/pywr-editor/editor/issues/89)).
- Node names are now sorted alphabetically in any drop-down menus ([#90](https://github.com/pywr-editor/editor/issues/90)).
- The `mrf`, `mrf_cost` and `cost` attributes of a`RiverGauge` node are now optional
  ([#94](https://github.com/pywr-editor/editor/issues/94)).
- Some component types (nodes and recorders) were not detected correctly in tree widget
  ([#100](https://github.com/pywr-editor/editor/issues/100)).
- Improved release of Windows binary files using GitHub Actions
  ([#102](https://github.com/pywr-editor/editor/issues/102)).

### Fixed
- `NodesAndFactorsTableWidget` was not loading correctly when the flow factor list was
 empty or did not save the form data for certain node types
 ([#93](https://github.com/pywr-editor/editor/issues/93)).
- Pandas `read_excel` only supports integers as `index_col`. The editor now stores the index as integers
  instead of strings ([#98](https://github.com/pywr-editor/editor/issues/98)).

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