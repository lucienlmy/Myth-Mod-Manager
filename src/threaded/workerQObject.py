import logging
import os
import shutil
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QCoreApplication as qapp
from PySide6.QtCore import QObject, Signal, QMutex, QMutexLocker

import src.errorChecking as errorChecking
from src.constant_vars import MOD_CONFIG, OPTIONS_CONFIG
from src.getPath import Pathing
from src.save import OptionsManager, Save


class Worker(QObject):
    setTotalProgress = Signal(int)

    addTotalProgress = Signal(int)

    setCurrentProgress = Signal(int, str)

    succeeded = Signal()

    doneCanceling = Signal()

    error = Signal(str)

    cancel = False

    mutex: QMutex = None # Should be set externally by the ProgressWidget class

    def __init__(self, optionsPath: str = OPTIONS_CONFIG, savePath: str = MOD_CONFIG) -> None:
        super().__init__()
        logging.getLogger(__name__)

        self.saveManager = Save(savePath)
        self.optionsManager = OptionsManager(optionsPath)

        self.p = Pathing(optionsPath)

    def start() -> None:
        ...

    def onCancel(self) -> None:
        ...

    def cancelCheck(self) -> None:
        with QMutexLocker(self.mutex):
            isCanceled: bool = self.cancel

        if isCanceled:
            logging.info('%s was canceled', self.__class__)
            self.onCancel()
            self.doneCanceling.emit()

    def move(self, src: str, dest: str) -> None:
        '''`shutil.move()` with some extra exception handling'''

        # Overwrite mod
        if os.path.exists(dest):
            shutil.rmtree(dest, onerror=self.onError)

        # Will try to move the file, if there is an exception, fix the issue and try again
        try:
            shutil.move(src, dest)
            logging.info('Moved file %s to destination %s', src, dest)

        except PermissionError:
            
            # Grab all files in mod
            for root, dirs, files in os.walk(src):

                self.addTotalProgress.emit(2 + len(dirs) + len(files))
                
                # Checking files for perm errors
                for file in files:
                    self.setCurrentProgress.emit(1, qapp.translate('Worker', 'Checking file permissions of') + f' {file}')
                    file_path = os.path.join(root, file)
                    errorChecking.permissionCheck(file_path)
                
                # Checking folders for perm errors
                for dir in dirs:
                    self.setCurrentProgress.emit(1, qapp.translate('Worker', 'Checking folder permissions of') + f' {dir}')
                    dir_path = os.path.join(root, dir)
                    errorChecking.permissionCheck(dir_path)
                
                # Checking mod directory for perm errors
                self.setCurrentProgress.emit(1, qapp.translate('Worker', 'Checking folder permissions of') + f' {root}')
                errorChecking.permissionCheck(root)

            self.setCurrentProgress.emit(1, qapp.translate('Worker', 'Fixing install for') + f' {os.path.basename(src)}')
            # If shutil.move made a partial dir of the mod delete it
            if os.path.exists(dest):
                shutil.rmtree(dest, onerror=self.onError)

    def onError(self, func: Callable[[Any], Any], path: str, exc_info: int) -> None:
        """Used for `shutil.rmtree()`s `onerror` kwarg"""

        logging.warning('An error was raised in shutil:\n%s', exc_info)

        if not errorChecking.permissionCheck(path):

            func(path)
