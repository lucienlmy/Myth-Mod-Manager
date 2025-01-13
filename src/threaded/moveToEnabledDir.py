import logging
import os

from PySide6.QtCore import QCoreApplication as qapp, Slot

from src.threaded.workerQObject import Worker

from src.constant_vars import MOD_CONFIG, OPTIONS_CONFIG

class MoveToEnabledModDir(Worker):

    def __init__(self, *mods: str, optionsPath: str = OPTIONS_CONFIG, savePath: str = MOD_CONFIG) -> None:
        super().__init__(optionsPath=optionsPath, savePath=savePath)

        self.mods: tuple[str, ...] = mods
        self.mods_moved: list[tuple[str, str]] = []

    @Slot()
    def start(self) -> None:
        '''Returns a mod to their respective directory'''

        self.setTotalProgress.emit(len(self.mods))

        disabledModsPath: str = self.optionsManager.getDispath()

        for mod in self.mods:

            self.setCurrentProgress.emit(1, qapp.translate('MoveToEnabledModDir', 'Enabling') + f' {mod}')

            modPath: str = os.path.join(disabledModsPath, mod)

            if os.path.isdir(modPath):

                modDestPath: list[str] | str = self.p.mod(self.saveManager.getType(mod), mod)

                self.move(modPath, modDestPath)
                self.mods_moved.append((modPath, modDestPath))
            else:
                logging.warning('%s was not found in:\n%s\nIgnoring...', mod, disabledModsPath)

            self.cancelCheck()
            self.rest()

        self.succeeded.emit()
    
    def onCancel(self) -> None:
        self.setTotalProgress.emit(len(self.mods_moved))
        for modPaths in self.mods_moved:
            self.setCurrentProgress.emit(1, qapp.translate('MoveToEnabledDir', 'Moving') + f' {os.path.basename(modPaths[0])}')
            self.move(modPaths[1], modPaths[0])
            self.rest()
