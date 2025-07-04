import pytest
from typing import Generator

from pytestqt.qtbot import QtBot

from src.constant_vars import ModType

from src.widgets.tagViewerQWidget import TagViewer
from src.widgets.managerQTableWidget import ModListWidget

MODS = (
    ('mod1', ModType.mods, True, '2.3.0', ['cool']),
    ('mod2', ModType.mods_override, True, 'None', ['calm', 'cool']),
    ('mod3', ModType.maps, None, '2.4.0', None),
)

@pytest.fixture(scope='module')
def create_modListWidget(createTemp_Mod_ini: str, createTemp_Config_ini: str) -> Generator:
    widget = ModListWidget(createTemp_Mod_ini, createTemp_Config_ini)

    widget.addMod(name=MODS[0][0], type=MODS[0][1], enabled=MODS[0][2], version=MODS[0][3], tags=MODS[0][4])
    widget.addMod(name=MODS[1][0], type=MODS[1][1], enabled=MODS[1][2], version=MODS[1][3], tags=MODS[1][4])
    widget.addMod(name=MODS[2][0], type=MODS[2][1], enabled=MODS[2][2], version=MODS[2][3], tags=MODS[2][4])

    yield widget

@pytest.fixture(scope='module')
def create_tagViewer(create_modListWidget: ModListWidget) -> Generator:
    widget = TagViewer(create_modListWidget)
    yield widget

@pytest.mark.skip
def test_addTags(create_tagViewer: TagViewer) -> None:
    raise NotImplementedError

@pytest.mark.skip
def test_removeTags(create_tagViewer: TagViewer) -> None:
    raise NotImplementedError

def test_tagViewer(qtbot: QtBot, create_tagViewer: TagViewer) -> None:
    widget: TagViewer = create_tagViewer

    qtbot.addWidget(widget.managerTable)
    qtbot.addWidget(widget)
