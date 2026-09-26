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

INTRO_TEXT = (
    "Choose the air-to-air missiles aircraft carry, for every aircraft in the "
    "campaign, instead of the missiles set by each aircraft's default loadout.\n\n"
    "Each list is a ranking, best missile first. Any pylon that carries a missile "
    "from a list is re-armed with the highest ranked missile from that list the "
    "pylon can carry. Missiles that are not in a list are never changed, and "
    "neither is anything else in the loadout (tanks, pods, bombs, or the number of "
    "missiles on a rack).\n\n"
    "Example: rank AIM-120D-3 above AIM-120C and every aircraft that normally "
    "carries AIM-120Cs will carry AIM-120Ds wherever the pylon supports them. "
    "Aircraft that cannot carry the AIM-120D keep their AIM-120Cs.\n\n"
    "Custom loadouts made in the payload editor are left untouched. When "
    '"Restrict weapons by date" is enabled, missiles that are not in service yet '
    "are skipped."
)


class RankedMissileList(QWidget):
    """Editor for one ranked list of preferred missiles stored in the settings."""

    def __init__(
        self,
        settings: Settings,
        setting_name: str,
        weapon_type: WeaponType,
        on_change: Callable[[], None],
    ) -> None:
        super().__init__()
        self.settings = settings
        self.setting_name = setting_name
        self.weapon_type = weapon_type
        self.on_change = on_change

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        layout.addWidget(QLabel(f"<b>{A2A_MISSILE_TYPE_NAMES[weapon_type]}</b>"))

        self.list = QListWidget()
        self.list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setMinimumHeight(120)
        self.list.setMaximumHeight(180)
        self.list.setToolTip("Best missile first. Drag to reorder.")
        self.list.model().rowsMoved.connect(lambda *_: self.save())
        self.list.currentRowChanged.connect(self.update_buttons)
        layout.addWidget(self.list)

        add_row = QHBoxLayout()
        self.add_selector = QComboBox()
        # Editable so the long list of missiles can be searched by typing.
        self.add_selector.setEditable(True)
        self.add_selector.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        add_row.addWidget(self.add_selector, 1)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_selected)
        add_row.addWidget(self.add_button)
        layout.addLayout(add_row)

        button_row = QHBoxLayout()
        self.up_button = QPushButton("Move up")
        self.up_button.clicked.connect(lambda: self.move_selected(-1))
        button_row.addWidget(self.up_button)
        self.down_button = QPushButton("Move down")
        self.down_button.clicked.connect(lambda: self.move_selected(1))
        button_row.addWidget(self.down_button)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        button_row.addWidget(self.remove_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        button_row.addWidget(self.clear_button)
        layout.addLayout(button_row)

        self.update_from_settings()

    @property
    def ranked(self) -> list[str]:
        return list(getattr(self.settings, self.setting_name))

    def names_in_list(self) -> list[str]:
        return [
            self.list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.list.count())
        ]

    def update_from_settings(self) -> None:
        self.list.clear()
        for name in self.ranked:
            family = missile_family_named(name)
            item = QListWidgetItem(family.display_name if family else name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            if family is None:
                item.setToolTip("Unknown missile. It will be ignored.")
            self.list.addItem(item)
        self.refresh_add_selector()
        self.update_buttons()

    def refresh_add_selector(self) -> None:
        listed = set(self.names_in_list())
        self.add_selector.clear()
        for family in missile_families(self.weapon_type):
            if family.name not in listed:
                self.add_selector.addItem(family.display_name, family.name)
        self.add_selector.setCurrentIndex(-1)
        self.add_selector.lineEdit().setPlaceholderText("Type or pick a missile to add")

    def update_buttons(self) -> None:
        row = self.list.currentRow()
        selected = row >= 0
        self.up_button.setEnabled(selected and row > 0)
        self.down_button.setEnabled(selected and row < self.list.count() - 1)
        self.remove_button.setEnabled(selected)
        self.clear_button.setEnabled(self.list.count() > 0)

    def save(self) -> None:
        setattr(self.settings, self.setting_name, self.names_in_list())
        self.refresh_add_selector()
        self.update_buttons()
        self.on_change()

    def add_selected(self) -> None:
        index = self.add_selector.findText(self.add_selector.currentText())
        if index < 0:
            return
        name = self.add_selector.itemData(index)
        family = missile_family_named(name)
        item = QListWidgetItem(family.display_name if family else name)
        item.setData(Qt.ItemDataRole.UserRole, name)
        self.list.addItem(item)
        self.list.setCurrentItem(item)
        self.save()

    def move_selected(self, offset: int) -> None:
        row = self.list.currentRow()
        new_row = row + offset
        if row < 0 or not 0 <= new_row < self.list.count():
            return
        item = self.list.takeItem(row)
        self.list.insertItem(new_row, item)
        self.list.setCurrentRow(new_row)
        self.save()

    def remove_selected(self) -> None:
        row = self.list.currentRow()
        if row < 0:
            return
        self.list.takeItem(row)
        self.save()

    def clear(self) -> None:
        self.list.clear()
        self.save()


class CoalitionMissilesBox(QGroupBox):
    def __init__(
        self,
        title: str,
        settings: Settings,
        radar_setting: str,
        ir_setting: str,
        on_change: Callable[[], None],
    ) -> None:
        super().__init__(title)
        layout = QGridLayout()
        self.setLayout(layout)
        self.lists = [
            RankedMissileList(settings, radar_setting, WeaponType.AAM_RADAR, on_change),
            RankedMissileList(settings, ir_setting, WeaponType.AAM_IR, on_change),
        ]
        for column, missile_list in enumerate(self.lists):
            layout.addWidget(missile_list, 0, column)

    def update_from_settings(self) -> None:
        for missile_list in self.lists:
            missile_list.update_from_settings()


class A2AMissilesPage(QWidget):
    def __init__(self, sc: SettingsContainer, on_change: Callable[[], None]) -> None:
        super().__init__()
        self.sc = sc

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        intro = QLabel(INTRO_TEXT)
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.boxes = [
            CoalitionMissilesBox(
                "Player coalition",
                sc.settings,
                "player_preferred_radar_missiles",
                "player_preferred_ir_missiles",
                on_change,
            ),
            CoalitionMissilesBox(
                "Enemy coalition",
                sc.settings,
                "enemy_preferred_radar_missiles",
                "enemy_preferred_ir_missiles",
                on_change,
            ),
        ]
        for box in self.boxes:
            layout.addWidget(box)

    def update_from_settings(self) -> None:
        for box in self.boxes:
            box.update_from_settings()
