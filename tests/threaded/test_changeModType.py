import os
import pytest
from typing import Generator

from PySide6.QtCore import QMutex

from pytestqt.qtbot import QtBot

from src.threaded.changeModType import ChangeModType
from src.constant_vars import ModType
from src.getPath import Pathing
from src.save import OptionsManager, Save

@pytest.fixture(scope="module")
def create_worker(create_mod_dirs: str, createTemp_Config_ini: str, createTemp_Mod_ini: str) -> Generator:
    parser = OptionsManager(createTemp_Config_ini)
    parser.setGamepath(create_mod_dirs)
    parser.writeData()

    url: str = os.path.join(create_mod_dirs, 'mods', 'make game easy mod')
    url2: str = os.path.join(create_mod_dirs, 'assets', 'mod_overrides', 'best mod ever')
    mutex = QMutex()
    worker = ChangeModType((url, ModType.mods_override), (url2, ModType.mods))
    worker.saveManager = Save(createTemp_Mod_ini)
    worker.p = Pathing(createTemp_Config_ini)
    worker.mutex = mutex

    yield worker

    worker.deleteLater()

def test_thread(qtbot: QtBot, create_worker: ChangeModType) -> None:
    with qtbot.wait_signal(create_worker.succeeded):
        create_worker.start()
    assert os.path.isdir(os.path.join(OptionsManager.getGamepath(), 'mods', 'make game easy mod')) is False
    assert os.path.isdir(os.path.join(OptionsManager.getGamepath(), 'assets', 'mod_overrides', 'make game easy mod')) is True

def test_cancel(qtbot: QtBot, create_worker: ChangeModType) -> None:
    create_worker.cancel = True

    with qtbot.wait_signal(create_worker.doneCanceling):
        create_worker.cancelCheck()
    
    assert os.path.isdir(os.path.join(OptionsManager.getGamepath(), 'mods', 'make game easy mod')) is True
    assert os.path.isdir(os.path.join(OptionsManager.getGamepath(), 'assets', 'mod_overrides', 'make game easy mod')) is False
