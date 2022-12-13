import os
import sys
from dataclasses import dataclass
import pythoncom
from pathlib import Path
from pywr_editor.utils import Logging

# noinspection PyUnresolvedReferences
from win32com.shell import shell

# noinspection PyUnresolvedReferences
from win32com.propsys import propsys, pscon


"""
 Add items to the Windows jump list. Items can be:
 - specific tasks
 - recently opened files.

 While tasks are always visible, recent files may be
 hidden depending on the Windows settings. To display
 recent projects go to Open Settings > Personalization
 > Start > Turn On the switch against Show recently
 opened items in Start, Jump Lists, and File Explorer.

 WIN32 API: http://timgolden.me.uk/pywin32-docs/PyICustomDestinationList.html
"""


@dataclass
class JumpListItemLink:
    title: str
    """ The link title """
    command: str
    """ The command to execute """
    command_args: list[str] = ()
    """ The command arguments """
    icon: Path | None = None
    """ The link icon file as Path instance """
    icon_index: int = 0
    """ The link icon index """
    working_directory: str | None = None
    """ The working directory """

    # noinspection PyUnresolvedReferences
    def link(self) -> "PyIShellLink":  # noqa: F821
        """
        Get the link as pythocom instance.
        :return: An instance of PyIShellLink.
        """
        # noinspection PyUnresolvedReferences
        link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink,
        )

        link.SetPath(self.command)
        if self.command_args:
            # args = " ".join(map(shlex.quote, self.command_args))
            args = " ".join(self.command_args)
            link.SetArguments(args)

        if self.working_directory:
            link.SetWorkingDirectory(self.working_directory)

        if self.icon and self.icon.exists():
            link.SetIconLocation(str(self.icon), self.icon_index)

        properties = link.QueryInterface(propsys.IID_IPropertyStore)
        properties.SetValue(
            pscon.PKEY_Title, propsys.PROPVARIANTType(self.title)
        )
        properties.Commit()
        return link


class JumpListItems:
    def __init__(self):
        """
        Initialises the class.
        """
        self._items: list[JumpListItemLink] = []

    # noinspection PyUnresolvedReferences
    @property
    def items(self) -> list["PyIObjectArray"] | None:  # noqa: F821
        """
        Returns the items.
        :return: A list of items as PyIObjectArray or None if there are no items.
        """
        if not self._items:
            return None

        # noinspection PyUnresolvedReferences
        collection = pythoncom.CoCreateInstance(
            shell.CLSID_EnumerableObjectCollection,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IObjectCollection,
        )
        for i in self._items:
            collection.AddObject(i.link())

        return collection

    def add(self, item: JumpListItemLink) -> None:
        """
        Adds a new item to the item list
        :param item: An instance of JumpListItems.
        :return: None
        """
        self._items.append(item)


class JumpList:
    def __init__(self):
        """
        Initialises the class.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        # noinspection PyUnresolvedReferences
        self._jumplist: "PyICustomDestinationList" = (  # noqa: F821
            pythoncom.CoCreateInstance(
                shell.CLSID_DestinationList,
                None,
                pythoncom.CLSCTX_INPROC_SERVER,
                shell.IID_ICustomDestinationList,
            )
        )

        # Windows locally stores the jump list tasks. Clear the list first
        self.logger.debug("Erasing list")
        self.erase()

        self.tasks = JumpListItems()
        self.recent_files = JumpListItems()

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # noinspection PyProtectedMember
            # self.app_path = Path(__file__).parent / "Pywr Editor.exe"
            self.app_path = str(Path(sys._MEIPASS) / "Pywr Editor.exe")
            self.app_args = []
            self.logger.debug(f"Using {self.app_path}")
        # dev
        else:
            self.app_path = sys.executable
            self.app_args = [str(Path(__file__).parent / "main.py")]

    def add_task(
        self,
        title: str,
        app_argument: list[str] | None = None,
        icon: Path | None = None,
        icon_index: int = 0,
    ) -> None:
        """
        Opens the application to run a task.
        :param title: The task title.
        :param app_argument: The application argument needed to run the task.
        Default to None.
        :param icon: The link icon file. Default ot None.
        :param icon_index: The link icon index. Default to 0.
        :return: None
        """
        if not app_argument:
            app_argument = []

        self.logger.debug(f"Adding task '{title}'")
        self.tasks.add(
            JumpListItemLink(
                title=title,
                command=self.app_path,
                command_args=self.app_args + app_argument,
                working_directory=os.getcwd(),
                icon=icon,
                icon_index=icon_index,
            )
        )

    def add_recent_file(self, title: str, file: Path) -> None:
        """
        Adds a new recent file to the list.
        :param title: The model title.
        :param file: The path to the file.
        :return: None
        """
        self.logger.debug(f"Adding recent file '{file}'")

        self.recent_files.add(
            JumpListItemLink(
                title=f"{title} - {file.name}",
                command=self.app_path,
                command_args=self.app_args + [str(file)],
                working_directory=os.getcwd(),
            )
        )

    def update(self) -> None:
        """
        Updates the jump list with the changes.
        :return: None
        """
        self._jumplist.BeginList()

        if self.recent_files.items:
            self._jumplist.AppendCategory(
                "Recent projects", self.recent_files.items
            )
        if self.tasks.items:
            self._jumplist.AddUserTasks(self.tasks.items)

        self._jumplist.CommitList()

    def erase(self) -> None:
        """
        Erases the jump list.
        :return: None
        """
        self._jumplist.DeleteList()
