# -*- coding: utf-8 -*-
"""Process Module."""

from PyQt6 import QtCore  # type: ignore

# from PyQt6.QtCore import pyqtSignal
import sys

# from pineboolib.core import decorators

from typing import Any, List, Optional, Iterable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application import types  # noqa: F401 # pragma: no cover


class ProcessBaseClass(QtCore.QProcess):
    """Process base class."""

    _std_out: Optional[str]
    _std_error: Optional[str]
    _encoding: str

    def read_std_error(self) -> Any:
        """Return last std error."""

        return self._std_error

    def read_std_out(self) -> Any:
        """Return last std out."""
        return self._std_out

    def set_std_out(self, value: str) -> None:
        """Set last std out."""

        self._std_out = value

    def set_std_error(self, value: str) -> None:
        """Set last std error."""

        self._std_error = value

    def get_working_directory(self) -> str:
        """Return working directory."""

        return super().workingDirectory()

    def readLine(self) -> bytes:  # type: ignore [override] # noqa: F821
        """Readline overload."""

        return super().readLine().data()

    def set_working_directory(self, working_directory: str) -> None:
        """Set working directory."""

        super().setWorkingDirectory(working_directory)

    stdout: str = property(read_std_out, set_std_out)  # type: ignore [assignment] # noqa F821
    stderr: str = property(read_std_error, set_std_error)  # type: ignore [assignment] # noqa F821
    workingDirectory: str = property(  # type: ignore[assignment] # noqa : F821
        get_working_directory, set_working_directory
    )


class ProcessStatic(ProcessBaseClass):
    """Process static class."""

    @classmethod
    def executeNoSplit(cls, comando: Union[list, "types.Array"], stdin_buffer: str = "") -> int:
        """Execute command no splitted."""

        comando_ = []
        for item in comando:
            comando_.append(item)

        # programa = list_[0]
        # arguments = list_[1:]
        # self.setProgram(programa)
        # self.setArguments(arguments)
        process = Process()
        process.setProgram(comando_[0])
        argumentos = comando_[1:]
        process.setArguments(argumentos)

        process.start()

        stdin_as_bytes = stdin_buffer.encode(process._encoding)
        process.writeData(stdin_as_bytes)
        process.waitForFinished(30000)

        cls.stderr = process.readAllStandardError().data().decode(process._encoding)
        cls.stdout = process.readAllStandardOutput().data().decode(process._encoding)
        return process.exitCode()

    @classmethod
    def execute(
        cls, program: Union[str, List, "types.Array"], arguments: Optional[Iterable[str]] = None
    ) -> int:
        """Execute normal command."""
        comando_: List[str] = []
        if isinstance(program, list):
            comando_ = program
        else:
            comando_ = str(program).split(" ")

        process = Process()
        process.setProgram(comando_[0])
        argumentos = comando_[1:]
        process.setArguments(argumentos)

        process.start()
        process.waitForFinished(30000)
        cls.stderr = process.readAllStandardError().data().decode(process._encoding)
        cls.stdout = process.readAllStandardOutput().data().decode(process._encoding)
        return process.exitCode()


class Process(ProcessBaseClass):
    """Process class."""

    def __init__(self, *args) -> None:
        """Inicialize."""

        super().__init__()
        # cast(pyqtSignal, self.readyReadStandardOutput).connect(self.stdoutReady)
        # cast(pyqtSignal, self.readyReadStandardError).connect(self.stderrReady)
        self._encoding = sys.getfilesystemencoding()
        self.normalExit = self.ExitStatus.NormalExit  # pylint: disable=invalid-name
        self.crashExit = self.ExitStatus.CrashExit  # pylint: disable=invalid-name

        if args:
            self.setProgram(args[0])
            argumentos = args[1:]
            self.setArguments(argumentos)

    def stop(self) -> None:
        """Stop the process."""
        self.kill()

    def writeToStdin(self, stdin_) -> None:
        """Write data to stdin channel."""

        stdin_as_bytes = stdin_.encode(self._encoding)
        self.writeData(stdin_as_bytes)
        # self.closeWriteChannel()

    # @decorators.pyqtSlot()
    # def stdoutReady(self) -> None:
    #    self._stdout = str(self.readAllStandardOutput())

    # @decorators.pyqtSlot()
    # def stderrReady(self) -> None:
    #    self._stderr = str(self.readAllStandardError())

    def get_is_running(self) -> bool:
        """Return if the process is running."""

        return self.state() in (self.ProcessState.Running, self.ProcessState.Starting)

    def exitcode(self) -> Any:
        """Return exit code."""

        return self.exitCode()

    def readStderr(self) -> str:
        """Return standart error."""

        return self.stderr

    def readStdout(self) -> str:
        """Return standart output."""

        return self.stdout

    def executeNoSplit(self, comando: Union[list, "types.Array"], stdin_buffer: str = "") -> int:
        """Execute command no splitted."""

        comando_ = []
        for item in comando:
            comando_.append(item)

        # programa = list_[0]
        # arguments = list_[1:]
        # self.setProgram(programa)
        # self.setArguments(arguments)
        self.setProgram(comando_[0])
        argumentos = comando_[1:]
        self.setArguments(argumentos)

        self.start()

        stdin_as_bytes = stdin_buffer.encode(self._encoding)
        self.writeData(stdin_as_bytes)
        self.waitForFinished(30000)

        self.stderr = self.readAllStandardError().data().decode(self._encoding)
        self.stdout = self.readAllStandardOutput().data().decode(self._encoding)
        return self.exitCode()

    def execute(  # type: ignore[override] # noqa : F821
        self,
        program: Union[str, List[str], "types.Array"],
        arguments: Optional[Iterable[str]] = None,
    ) -> int:
        """Execute normal command."""
        comando_: List[str] = []
        if isinstance(program, list):
            comando_ = program
        else:
            comando_ = str(program).split(" ")

        self.setProgram(comando_[0])
        argumentos = comando_[1:]
        self.setArguments(argumentos)

        self.start()
        self.waitForFinished(30000)
        self.stderr = self.readAllStandardError().data().decode(self._encoding)
        self.stdout = self.readAllStandardOutput().data().decode(self._encoding)
        return self.exitCode()

    running = property(get_is_running)
