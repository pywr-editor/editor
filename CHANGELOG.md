# Changelog

All notable changes to this project will be documented in this file.
All issue numbers are relative to https://github.com/pywr-editor/editor

## v1.1.0 - 2022-12-17

### Fixed
- Prevent the editor from crashing when user was asked to save the model file on exit ([#11](https://github.com/pywr-editor/editor/issues/11))
- Check if Microsoft Excel is installed. If it is not, the import/export buttons, available in some widgets, will now be hidden ([#15](https://github.com/pywr-editor/editor/issues/15))
- The file names, in the recent project list in the welcome screen, were clipped ([#17](https://github.com/pywr-editor/editor/issues/17))
- When the editor was launched with the option to generate the debug/log file, the file was saved in the wrong path ([#19](https://github.com/pywr-editor/editor/issues/19))
- Prevent the editor from crashing when the model dictionary, loaded from a JSON file, does not have the "table" key ([#21](https://github.com/pywr-editor/editor/issues/21))

## v1.0.0
- This is the first release of pywr editor