import multiprocessing

if __name__ == "__main__":
    # Freeze the program so it can be run as a standalone executable
    multiprocessing.freeze_support()
    from pywr_editor import app
    # Run the app
    app()
