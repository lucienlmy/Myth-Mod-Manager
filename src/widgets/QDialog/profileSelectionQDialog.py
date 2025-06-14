from typing import List
import PySide6.QtWidgets as qtw
from PySide6.QtCore import Qt as qt, QCoreApplication as qapp, Slot

from src.widgets.QDialog.QDialog import Dialog

from src.profileManager import ProfileManager
from src.constant_vars import PROFILES_JSON

class SelectProfile(Dialog):

    profile: str = None

    def __init__(self, profilePath: str = PROFILES_JSON) -> None:
        super().__init__()

        self.setWindowTitle(qapp.translate('SelectProfile', 'Profile to copy mod(s) to:'))

        layout = qtw.QVBoxLayout()

        self.profileList = qtw.QListWidget(self)
        self.profileList.setHorizontalScrollBarPolicy(qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.profileList.setFocusPolicy(qt.FocusPolicy.NoFocus)
        self.profileList.setSelectionMode(qtw.QListWidget.SelectionMode.SingleSelection)

        self.searchBar = qtw.QLineEdit()
        self.searchBar.setPlaceholderText(qapp.translate('SelectProfile', 'Search...'))
        self.searchBar.textChanged.connect(self.search)

        profileManager = ProfileManager(profilePath)

        buttons = qtw.QDialogButtonBox.StandardButton.Ok | qtw.QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = qtw.QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.profileList.addItems(list(profileManager.getJSON().keys()))

        for widget in (self.searchBar, self.profileList, self.buttonBox):
            layout.addWidget(widget)
        
        self.setLayout(layout)
    
    @Slot(str)
    def search(self, input: str) -> None:

        results: List[qtw.QListWidgetItem] = self.profileList.findItems(
            f'{input}*',
            qt.MatchFlag.MatchWildcard | qt.MatchFlag.MatchExactly
        )

        for i in range(0, self.profileList.count() + 1):

            item: qtw.QListWidgetItem = self.profileList.item(i)

            if item not in results:
                self.profileList.setRowHidden(i, True)
            else:
                self.profileList.setRowHidden(i, False)
    
    @Slot()
    def accept(self) -> None:

        self.setResult(1)

        try:
            self.profile = self.profileList.selectedItems()[0].text()
        except IndexError:
            pass

        return super().accept()
    
    @Slot()
    def reject(self) -> None:
        self.setResult(0)
        return super().reject()
