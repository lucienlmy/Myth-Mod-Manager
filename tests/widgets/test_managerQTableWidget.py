import tempfile
import os
from typing import Generator

from PySide6.QtWidgets import QTableWidgetItem
import pytest
from pytestqt.qtbot import QtBot

from PySide6.QtCore import Qt as qt

from src.widgets.managerQTableWidget import ModListWidget
from src.constant_vars import ModType, ModRole

MODS = (('mod1', ModType.mods, True, '2.3.0', ['cool']),
        ('mod2', ModType.mods_override, True, 'None', ['calm', 'cool']),
        ('mod3', ModType.maps, None, '2.4.0', None),
        )

@pytest.fixture(scope='module')
def create_QTable(createTemp_Config_ini: str, createTemp_Mod_ini: str) -> Generator:

    widget = ModListWidget(createTemp_Mod_ini, createTemp_Config_ini)

    widget.addMod(name=MODS[0][0], type=MODS[0][1], enabled=MODS[0][2], version=MODS[0][3], tags=MODS[0][4])
    widget.addMod(name=MODS[1][0], type=MODS[1][1], enabled=MODS[1][2], version=MODS[1][3], tags=MODS[1][4])
    widget.addMod(name=MODS[2][0], type=MODS[2][1], enabled=MODS[2][2], version=MODS[2][3], tags=MODS[2][4])

    yield widget

def test_addMods(create_QTable: ModListWidget) -> None:

    assert create_QTable.rowCount() == 3
    assert create_QTable.getEnabledItem(2).text() == 'Disabled'
    assert create_QTable.getNameItem(0).text() == 'mod1'
    assert create_QTable.getTypeItem(0).text() == 'mods'
    assert create_QTable.getVersionItem(1).text() == '1.0.0'
    assert create_QTable.getNameItem(0).data(ModRole.tags) == ('cool',)
    assert create_QTable.getNameItem(2).data(ModRole.tags) == ()

def test_sort(create_QTable: ModListWidget) -> None:

    create_QTable.sort(1)
    assert create_QTable.sortState['col'] == 1
    assert create_QTable.sortState['ascending'] == qt.SortOrder.AscendingOrder
    create_QTable.sort(2)
    assert create_QTable.sortState['col'] == 2
    assert create_QTable.sortState['ascending'] == qt.SortOrder.AscendingOrder
    create_QTable.sort(2)
    assert create_QTable.sortState['col'] == 2
    assert create_QTable.sortState['ascending'] == qt.SortOrder.DescendingOrder

def test_getSelectedNameItems(create_QTable: ModListWidget) -> None:

    create_QTable.selectAll()
    allNameItems: list[QTableWidgetItem] = create_QTable.getSelectedNameItems()
    assert len(allNameItems) == 3

    names: tuple[str, str, str] = (MODS[0][0], MODS[1][0], MODS[2][0])

    for item in allNameItems:
        assert item.text() in names

def test_getModTypeCount(create_QTable: ModListWidget) -> None:
    assert create_QTable.getModTypeCount(ModType.mods) == 1

def test_Icon(create_QTable: ModListWidget, create_mod_dirs: str) -> None:

    with tempfile.TemporaryDirectory(dir=os.path.join(create_mod_dirs, 'mods')) as tmp_mod:

        tmp_mod_name: list[str] = [os.path.basename(tmp_mod)]

        create_QTable.saveManager.addMods((tmp_mod_name, ModType.mods))
        create_QTable.saveManager.setModWorkshopAssetID(tmp_mod_name[0], '1234')

        create_QTable.refreshMods()
        tmp_mod_item: QTableWidgetItem = create_QTable.findItems(tmp_mod_name[0], qt.MatchFlag.MatchExactly)[0]

        assert tmp_mod_item.icon().isNull() is False

#TODO: Test installMods()
@pytest.mark.skip
def test_installMods() -> None:
    pass

def test_widget(qtbot: QtBot, create_QTable: ModListWidget) -> None:

    qtbot.addWidget(create_QTable)

    assert create_QTable.columnCount() == 4
    assert create_QTable.verticalHeader().isHidden() is True
    
