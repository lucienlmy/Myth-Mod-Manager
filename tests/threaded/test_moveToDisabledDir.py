import os
import pytest
from typing import Generator

from PySide6.QtCore import QMutex

from pytestqt.qtbot import QtBot

from src.threaded.moveToDisabledDir import MoveToDisabledDir
from src.getPath import Pathing
from src.save import OptionsManager

@pytest.fixture(scope='module')
def create_worker(create_mod_dirs: str, createTemp_Config_ini: str, createTemp_Mod_ini: str) -> Generator:
    dispath: str = os.path.join(create_mod_dirs, 'disabledMods')
    parser = OptionsManager(createTemp_Config_ini)
    parser.setGamepath(create_mod_dirs)
    parser.setDispath(dispath)
    parser.writeData()

    mutex = QMutex()
    worker = MoveToDisabledDir('make game easy mod', optionsPath=createTemp_Config_ini, savePath=createTemp_Mod_ini)
    worker.p = Pathing(createTemp_Config_ini)
    worker.mutex = mutex

    yield worker

    worker.deleteLater()

def test_thread(qtbot: QtBot, create_worker: MoveToDisabledDir) -> None:
    with qtbot.wait_signal(create_worker.succeeded):
        create_worker.start()

    assert os.path.exists(os.path.join(OptionsManager.getDispath(), 'make game easy mod'))
    assert not os.path.exists(os.path.join(OptionsManager.getGamepath(), 'mods', 'make game easy mod'))

def test_cancel(qtbot: QtBot, create_worker: MoveToDisabledDir) -> None:
    create_worker.cancel = True
    with qtbot.wait_signal(create_worker.doneCanceling):
        create_worker.cancelCheck()

    assert not os.path.exists(os.path.join(OptionsManager.getDispath(), 'make game easy mod'))
    assert os.path.exists(os.path.join(OptionsManager.getGamepath(), 'mods', 'make game easy mod'))
