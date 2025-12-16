import multiprocessing

if __name__ == "__main__":
    # fix infinite loop - https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing # noqa:E501
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)

    from pywr_editor import app

    app()
