import os

from PySide6.QtCore import QMutex

from src.threaded.deleteMod import DeleteMod
from src.getPath import Pathing
from src.save import OptionsManager, Save


def test_thread(create_mod_dirs: str, createTemp_Config_ini: str, createTemp_Mod_ini: str) -> None:
    parser = OptionsManager(createTemp_Config_ini)
    parser.setGamepath(create_mod_dirs)
    parser.writeData()
    mutex = QMutex()
    worker = DeleteMod('make game easy mod')
    worker.optionsManager = parser
    worker.saveManager = Save(createTemp_Mod_ini)
    worker.mutex = mutex
    worker.p = Pathing(createTemp_Config_ini)

    worker.start()

    assert os.path.isdir(os.path.join(create_mod_dirs, 'mods', 'make game easy mod')) is False

    worker.deleteLater()
