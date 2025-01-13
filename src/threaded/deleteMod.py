import logging
import os

from PySide6.QtCore import QCoreApplication as qapp, Slot

import send2trash

from src.threaded.workerQObject import Worker

from src.constant_vars import MOD_CONFIG, OPTIONS_CONFIG, ModType

class DeleteMod(Worker):
    def __init__(self, *mods: str, optionsPath: str = OPTIONS_CONFIG, savePath: str = MOD_CONFIG) -> None:
        super().__init__(optionsPath=optionsPath, savePath=savePath)

        self.mods: tuple[str, ...] = mods

    @Slot()
    def start(self) -> None:
        '''Removes the mod(s) from the user's computer'''

        logging.info('Deleting mods from computer: %s', ', '.join(self.mods))

        self.setTotalProgress.emit(len(self.mods))

        disPath: str = self.optionsManager.getDispath()

        try: 
            for modName in self.mods:

                self.setCurrentProgress.emit(1, qapp.translate('DeleteMod', 'Deleting') + f'{modName}')

                enabled: bool = self.saveManager.getEnabled(modName)

                type: ModType | str | None = self.saveManager.getType(modName) if enabled else 'disabled'

                self.saveManager.removeMods(modName)

                path: list[str] | str = self.p.mod(type, modName) if type != 'disabled' else disPath

                if os.path.isdir(path):
                    send2trash.send2trash(path)
                else:
                    logging.error('An error was raised in FileMover.deleteMod(), %s path does not exist:\n%s', os.path.basename(path), path)

                self.cancelCheck()
                self.rest()

            self.succeeded.emit()

        except Exception as e:
            self.error.emit(qapp.translate('DeleteMod', 'An error was raised while deleting a mod:') + f'\n{e}')
