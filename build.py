import os
from pathlib import Path

import PyInstaller.__main__
import typer

from pywr_editor.assets import get_nodes, get_parameters, get_recorders

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def freeze():
    """
    Creates the executable.
    """
    typer.secho(
        ">> Building executable with PyInstaller",
        fg=typer.colors.GREEN,
        bold=True,
    )
    PyInstaller.__main__.run(["main.spec", "--noconfirm"])
    typer.secho(">> Done :)", fg=typer.colors.GREEN, bold=True)


@app.command()
def editor_assets():
    """
    Generates the editor assets.
    """
    assets_path = Path(__file__).parent / "pywr_editor" / "assets"
    qrc_file = assets_path / "assets.qrc"
    py_file = assets_path.parent / "style" / "assets.py"
    os.system(f'pyside6-rcc.exe "{qrc_file}" -o "{py_file}"')

    typer.secho(f">> Generated {py_file}", fg=typer.colors.GREEN, bold=True)


@app.command()
def pywr_assets():
    """
    Generates the pywr assets.
    """
    typer.secho(
        ">> Creating parameter names dictionary",
        fg=typer.colors.GREEN,
        bold=True,
    )
    get_parameters()
    typer.secho(">> Creating node names dictionary", fg=typer.colors.GREEN, bold=True)
    get_nodes()
    typer.secho(
        ">> Creating recorder names dictionary",
        fg=typer.colors.GREEN,
        bold=True,
    )
    get_recorders()

    qrc_file = Path(__file__).parent / "pywr_editor" / "assets" / "pywr_resources.qrc"
    py_file = Path(__file__).parent / "pywr_editor" / "model" / "pywr_resources.py"
    os.system(f'pyside6-rcc.exe "{qrc_file}" -o "{py_file}"')

    typer.secho(f">> Generated {py_file}", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    app()
