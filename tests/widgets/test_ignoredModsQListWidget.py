import pytest
from typing import Generator

from src.widgets.ignoredModsQListWidget import IgnoredMods

@pytest.fixture(scope='module')
def create_ignoredModList(createTemp_Mod_ini: str) -> Generator:
    widget = IgnoredMods(savePath=createTemp_Mod_ini)
    yield widget
    widget.deleteLater()

def test_refreshList(create_ignoredModList: IgnoredMods) -> None:
    
    create_ignoredModList.saveManager.setIgnored('super fun mod', True)
    create_ignoredModList.saveManager.saveJSON()

    create_ignoredModList.refreshList()

    assert create_ignoredModList.count() == 1