<h1 style="text-align:center">
  <br>
  <img src="./pywr_editor/assets/logo-color.png" alt="Pywr editor" width="200">
  <br>
  Pywr editor
  <br>
</h1>

<h4 align="center">A graphical user interface to edit Pywr models</h4>


<p  style="text-align:center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">
    <img src="https://img.shields.io/badge/license-GPL-blue"
         alt="GPL" />
  </a>
  <a href="paypal.me/ssimoncelli87">
    <img src="https://img.shields.io/badge/%C2%A3-donate-brightgreen" alt="Donate" />
  </a>
  <a href="https://github.com/pywr-editor/editor/actions/workflows/test_windows.yaml">
    <img src="https://github.com/pywr-editor/editor/actions/workflows/test_windows.yaml/badge.svg" alt="Windows" />
  </a>
  <a href="https://github.com/pywr-editor/editor/actions/workflows/flake8.yaml">
    <img src="https://github.com/pywr-editor/editor/actions/workflows/flake8.yaml/badge.svg" alt="Syntax check" />
  </a>
</p>


Pywr editor is a user-friendly, free and open‑source graphical user interface (UI) to build and customise [pywr](https://github.com/pywr/pywr) 
models written in [JSON-based document](https://pywr.github.io/pywr/json.html) format. 

Pywr editor provides the following features:

- Full and easy customisation of model parameters, nodes, recorders, metadata, tables, slots and imports directly from the UI
- Dynamic validation of model configuration  
- Support of custom model components
- Interactive model schematic
  - pan, zoom, resize, screenshotting of schematic
  - drag, drop or delete multiple nodes at the same time
  - connect or disconnect nodes
  - change colour and shape of nodes
- External data support
  - Automatic parsing of external files to offer suggestions of DataFrame index and column names, and values (from CSV, Excel or HDF files)
  - Import/ export value to Excel (Windows only)
  - Data visualisation with charts

> Note: although the software can run on any system that can run Python, 
> the editor is currently designed to work on Windows only. Upon request
> the UI can be optimised to work on Linux and Mac platforms.

# Getting Started
You can get started with Pywr editor by installing the Windows binary or fetching the
package from the Python Package Index (PyPI).

## Install the binary
The Windows executable is already bundles Python and all the necessary dependencies

## Install using pip
Pywr editor is available on PyPI. You can install it through pip:

    pip install pywr-editor

this requires Python >= 3.10

# License
This software is licensed under the GNU General Public License, version 3.0+. See the LICENSE file