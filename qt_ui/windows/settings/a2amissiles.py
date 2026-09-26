import textwrap
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from game.data.a2amissiles import (
    A2A_MISSILE_TYPE_NAMES,
    missile_families,
    missile_family_named,
)
from game.data.weapons import WeaponType
from game.settings import Settings
from game.settings.ISettingsContainer import SettingsContainer

DESCRIPTION = (
    "Choose the air-to-air missiles every aircraft in the campaign carries, instead "
    "of the missiles set by each aircraft's default loadout. Each list is a ranking, "
    "best missile first. Any pylon that carries a missile from a list is re-armed "
    "with the highest ranked missile from that list the pylon can carry. Missiles "
    "that are not in a list are never changed, and neither is anything else in the "
    "loadout (tanks, pods, bombs, or the number of missiles on a rack).\n\n"
    "Example: rank AIM-120D-3 above AIM-120C and every aircraft that normally "
    "carries AIM-120Cs carries AIM-120Ds wherever the pylon supports them.\n\n"
    "New campaigns always start with the default loadout missiles. Changes made "
    'here only take effect once they are saved with "Save Changes". Custom '
    "loadouts made in the payload editor are left untouched."
)

LIST_DETAILS = {
    WeaponType.AAM_RADAR: "Best missile first. Drag or use the buttons to reorder.",
    WeaponType.AAM_IR: "Best missile first. Drag or use the buttons to reorder.",
}


def _settings_label(title: str, detail: str) -> QLabel:
    """A label formatted like the ones on the other settings pages."""
    text = "<strong>{}</strong><br />{}".format(
        "<br />".join(textwrap.wrap(title, width=55)),
        "<br />".join(textwrap.wrap(detail, width=55)),
    )
    label = QLabel(text)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    return label


class RankedMissileList(QWidget):
    """Editor for one ranked list of preferred missiles.

    Edits are kept as a draft until the page saves them to the settings.
    """

    def __init__(
        self,
        settings: Settings,
        setting_name: str,
        weapon_type: WeaponType,
        on_edit: Callable[[], None],
    ) -> None:
        super().__init__()
        self.settings = settings
        self.setting_name = setting_name
        self.weapon_type = weapon_type
        self.on_edit = on_edit

        # Fixed width so the lists line up like the controls on other pages.
        self.setFixedWidth(360)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.list = QListWidget()
        self.list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setMinimumHeight(110)
        self.list.setMaximumHeight(150)
        self.list.model().rowsMoved.connect(lambda *_: self.edited())
        self.list.currentRowChanged.connect(self.update_buttons)
        layout.addWidget(self.list)

        add_row = QHBoxLayout()
        self.add_selector = QComboBox()
        self.add_selector.setPlaceholderText("Select a missile to add")
        self.add_selector.currentIndexChanged.connect(self.update_buttons)
        add_row.addWidget(self.add_selector, 1)
        # Same "+" button as the faction editor of the new game wizard.
        self.add_button = QPushButton("+")
        self.add_button.setStyleSheet("QPushButton{ font-weight: bold; }")
        self.add_button.setFixedWidth(50)
        self.add_button.setToolTip("Add the selected missile at the bottom")
        self.add_button.clicked.connect(self.add_selected)
        add_row.addWidget(self.add_button)
        layout.addLayout(add_row)

        button_row = QHBoxLayout()
        self.up_button = QPushButton("Move Up")
        self.up_button.clicked.connect(lambda: self.move_selected(-1))
        button_row.addWidget(self.up_button)
        self.down_button = QPushButton("Move Down")
        self.down_button.clicked.connect(lambda: self.move_selected(1))
        button_row.addWidget(self.down_button)
        self.remove_button = QPushButton("Remove")
        self.remove_button.setProperty("style", "btn-danger")
        self.remove_button.clicked.connect(self.remove_selected)
        button_row.addWidget(self.remove_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self.update_from_settings()

    @property
    def saved(self) -> list[str]:
        return list(getattr(self.settings, self.setting_name))

    @property
    def draft(self) -> list[str]:
        return [
            self.list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.list.count())
        ]

    @property
    def has_unsaved_changes(self) -> bool:
        return self.draft != self.saved

    def save(self) -> None:
        setattr(self.settings, self.setting_name, self.draft)

    def update_from_settings(self) -> None:
        self.list.clear()
        for name in self.saved:
            self.list.addItem(self._item_for(name))
        self.refresh_add_selector()
        self.update_buttons()

    @staticmethod
    def _item_for(name: str) -> QListWidgetItem:
        family = missile_family_named(name)
        item = QListWidgetItem(family.display_name if family else name)
        item.setData(Qt.ItemDataRole.UserRole, name)
        if family is None:
            item.setToolTip("Unknown missile. It will be ignored.")
        return item

    def refresh_add_selector(self) -> None:
        listed = set(self.draft)
        self.add_selector.clear()
        for family in missile_families(self.weapon_type):
            if family.name not in listed:
                self.add_selector.addItem(family.display_name, family.name)
        self.add_selector.setCurrentIndex(-1)

    def update_buttons(self) -> None:
        row = self.list.currentRow()
        selected = row >= 0
        self.up_button.setEnabled(selected and row > 0)
        self.down_button.setEnabled(selected and row < self.list.count() - 1)
        self.remove_button.setEnabled(selected)
        self.add_button.setEnabled(self.add_selector.currentIndex() >= 0)

    def edited(self) -> None:
        self.refresh_add_selector()
        self.update_buttons()
        self.on_edit()

    def add_selected(self) -> None:
        name = self.add_selector.currentData()
        if name is None:
            return
        item = self._item_for(name)
        self.list.addItem(item)
        self.list.setCurrentItem(item)
        self.edited()

    def move_selected(self, offset: int) -> None:
        row = self.list.currentRow()
        new_row = row + offset
        if row < 0 or not 0 <= new_row < self.list.count():
            return
        item = self.list.takeItem(row)
        self.list.insertItem(new_row, item)
        self.list.setCurrentRow(new_row)
        self.edited()

    def remove_selected(self) -> None:
        row = self.list.currentRow()
        if row < 0:
            return
        self.list.takeItem(row)
        self.edited()

    def clear(self) -> None:
        self.list.clear()
        self.edited()


class CoalitionMissilesGroup(QGroupBox):
    def __init__(
        self,
        title: str,
        settings: Settings,
        radar_setting: str,
        ir_setting: str,
        on_edit: Callable[[], None],
    ) -> None:
        super().__init__(title)
        layout = QGridLayout()
        self.setLayout(layout)
        self.lists: list[RankedMissileList] = []
        for row, (weapon_type, setting) in enumerate(
            [(WeaponType.AAM_RADAR, radar_setting), (WeaponType.AAM_IR, ir_setting)]
        ):
            layout.addWidget(
                _settings_label(
                    f"{A2A_MISSILE_TYPE_NAMES[weapon_type]} missiles",
                    LIST_DETAILS[weapon_type],
                ),
                row,
                0,
            )
            missile_list = RankedMissileList(settings, setting, weapon_type, on_edit)
            layout.addWidget(missile_list, row, 1, Qt.AlignmentFlag.AlignRight)
            self.lists.append(missile_list)


class A2AMissilesPage(QWidget):
    def __init__(self, sc: SettingsContainer, on_save: Callable[[], None]) -> None:
        super().__init__()
        self.sc = sc
        self.on_save = on_save

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        # Styled like the plugin descriptions on the "LUA Plugins Options" page.
        about = QGroupBox("Preferred Air-to-Air Missiles")
        about_layout = QVBoxLayout()
        about.setLayout(about_layout)
        description = QLabel(DESCRIPTION)
        description.setWordWrap(True)
        font = description.font()
        font.setItalic(True)
        description.setFont(font)
        description.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        about_layout.addWidget(description)
        layout.addWidget(about)

        self.groups = [
            CoalitionMissilesGroup(
                "Player coalition",
                sc.settings,
                "player_preferred_radar_missiles",
                "player_preferred_ir_missiles",
                self.update_save_state,
            ),
            CoalitionMissilesGroup(
                "Enemy coalition",
                sc.settings,
                "enemy_preferred_radar_missiles",
                "enemy_preferred_ir_missiles",
                self.update_save_state,
            ),
        ]
        for group in self.groups:
            layout.addWidget(group)

        # Same buttons as the air wing configuration dialog.
        button_row = QHBoxLayout()
        self.status = QLabel()
        button_row.addWidget(self.status)
        button_row.addStretch()
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setToolTip(
            "Empty every list, so aircraft carry their default loadout missiles"
        )
        self.clear_button.clicked.connect(self.clear_all)
        button_row.addWidget(self.clear_button)
        self.discard_button = QPushButton("Discard Changes")
        self.discard_button.setProperty("style", "btn-danger")
        self.discard_button.clicked.connect(self.discard)
        button_row.addWidget(self.discard_button)
        self.save_button = QPushButton("Save Changes")
        self.save_button.setProperty("style", "btn-accept")
        self.save_button.clicked.connect(self.save)
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

        self.update_save_state()

    @property
    def lists(self) -> list[RankedMissileList]:
        return [missile_list for group in self.groups for missile_list in group.lists]

    @property
    def has_unsaved_changes(self) -> bool:
        return any(missile_list.has_unsaved_changes for missile_list in self.lists)

    def update_save_state(self) -> None:
        unsaved = self.has_unsaved_changes
        self.save_button.setEnabled(unsaved)
        self.discard_button.setEnabled(unsaved)
        self.clear_button.setEnabled(any(ml.draft for ml in self.lists))
        if unsaved:
            self.status.setText("<strong>You have unsaved changes.</strong>")
        elif any(ml.saved for ml in self.lists):
            self.status.setText("Preferred missiles are in use.")
        else:
            self.status.setText("Aircraft carry their default loadout missiles.")

    def save(self) -> None:
        for missile_list in self.lists:
            missile_list.save()
        self.update_save_state()
        self.on_save()

    def discard(self) -> None:
        self.update_from_settings()

    def clear_all(self) -> None:
        for missile_list in self.lists:
            missile_list.clear()

    def confirm_close(self, parent: QWidget) -> bool:
        """Asks what to do with unsaved changes. Returns False to stay open."""
        if not self.has_unsaved_changes:
            return True
        answer = QMessageBox.question(
            parent,
            "Unsaved air-to-air missile changes",
            "The preferred air-to-air missiles have unsaved changes. Save them?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Save:
            self.save()
        elif answer == QMessageBox.StandardButton.Discard:
            self.discard()
        return answer != QMessageBox.StandardButton.Cancel

    def update_from_settings(self) -> None:
        for missile_list in self.lists:
            missile_list.update_from_settings()
        self.update_save_state()
