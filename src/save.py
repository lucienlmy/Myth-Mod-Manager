import os
import logging
from typing import TextIO, Sequence
from configparser import ConfigParser

from PySide6.QtCore import QSize

from src.JSONParser import JSONParser
from src.constant_vars import MOD_CONFIG, OPTIONS_CONFIG, ModType, LIGHT, MODS_DISABLED_PATH_DEFAULT, ModKeys, OptionKeys

class Save():
    '''Manages the data of each mod'''

    jsonParser: JSONParser = JSONParser(MOD_CONFIG)

    def __init__(self, file=MOD_CONFIG) -> None:
        Save.jsonParser.path = file
        Save.jsonParser.loadJSON()

    @staticmethod
    def saveJSON() -> None:
        Save.jsonParser.saveJSON()

    @staticmethod
    def mods() -> list[str]:
        return list(Save.jsonParser.file.keys())
    
    @staticmethod
    def hasModOption(mod: str, option: str) -> bool:
        if Save.hasMod(mod):
            return option in Save.getMod(mod)

        return False

    @staticmethod
    def hasMod(mod: str) -> bool:
        return Save.getMod(mod) is not None

    @staticmethod
    def getMod(mod: str) -> dict:
        return Save.jsonParser.file.get(mod, None)

    @staticmethod
    def addMods(*mods: tuple[list[str], ModType]) -> None:
        '''
        Saves new mods to the config file

        It takes both singular and lists of mods

        Param eg: `(List of mod names, ModType Enum)`
        '''

        for arg in mods:
            for mod in arg[0]:

                if not Save.hasMod(mod):
                    logging.info('Adding new mod to %s: %s', MOD_CONFIG, mod)
                    Save.jsonParser.file[mod] = {}

                Save.setEnabled(mod)
                Save.setType(mod, arg[1])

    @staticmethod
    def getEnabled(mod: str) -> bool:
        fallback = True
        if Save.hasMod(mod):
            return Save.getMod(mod).get(ModKeys.enabled.value, fallback)
        return fallback

    @staticmethod
    def setEnabled(mod: str, value: bool = True) -> None:
        if Save.hasMod(mod):
            Save.getMod(mod)[ModKeys.enabled.value] = value

    @staticmethod
    def getIgnored(mod: str) -> bool:
        fallback = False
        if Save.hasMod(mod):
            return Save.getMod(mod).get(ModKeys.ignored.value, fallback)
        else:
            return fallback

    @staticmethod
    def setIgnored(mod: str, value: bool = False) -> None:
        if Save.hasMod(mod):
            Save.getMod(mod)[ModKeys.ignored.value] = value
    
    @staticmethod
    def getType(mod: str) -> ModType | None:
        '''
        Converts the string into a `ModType` then returns it.
        Returns `None` if the mod doesn't have a type.
        '''

        if not Save.hasMod(mod):
            logging.error('save.GetType: %s does not exist in the files', mod)
            return

        modType = Save.getMod(mod).get(ModKeys.type.value)

        if modType:
            return ModType(modType)
        else:
            return None
    
    @staticmethod
    def setType(mod: str, type: ModType) -> None:
        if Save.hasMod(mod):
            Save.getMod(mod)[ModKeys.type.value] = type
    
    @staticmethod
    def getModworkshopAssetID(mod: str) -> str:
        fallback = ''
        if Save.hasMod(mod):
            return Save.getMod(mod).get(ModKeys.modworkshopid, fallback)
        else:
            return fallback
    
    @staticmethod
    def setModWorkshopAssetID(mod: str, id: str = '') -> None:
        if Save.hasMod(mod):
            Save.getMod(mod)[ModKeys.modworkshopid.value] = id
    
    @staticmethod
    def getTags(mod: str) -> list[str]:
        fallback = []
        if Save.hasMod(mod):
            tags = Save.getMod(mod).get(ModKeys.tags.value, fallback)
            return tags if tags is not None else fallback
        else:
            return fallback
    
    @staticmethod
    def getAllTags() -> list[str]:
        allTags = set()
        for mod in Save.mods():
            if not Save.getTags(mod):
                continue
            for tag in Save.getTags(mod):
                allTags.add(tag)

        return sorted(list(allTags))
    
    @staticmethod
    def setTags(tags: Sequence[str], *mods: str) -> None:
        if not tags:
            for mod in mods:
                if Save.hasMod(mod):
                    Save.getMod(mod)[ModKeys.tags] = None
            return

        for mod in mods:
            if not Save.hasMod(mod):
                continue

            currentTags = Save.getTags(mod)
            if currentTags is None:
                currentTags = []

            updatedTags = list(set(tags + currentTags))
            logging.info('Setting the tags of %s from %s to %s', mod, currentTags, updatedTags)

            Save.getMod(mod)[ModKeys.tags.value] = updatedTags
    
    @staticmethod
    def removeTags(tags: Sequence[str], *mods: str) -> None:
        logging.info('Removing the tags %s from %')
        for mod in mods:
            modTags = Save.getTags(mod)

            if not modTags:
                continue

            updatedTags = [x for x in modTags if x not in tags]
            logging.info('Removing the tags of %s from %s to %s', mod, modTags, updatedTags)

            Save.getMod(mod)[ModKeys.tags] = updatedTags
    
    @staticmethod
    def clearTags() -> None:
        logging.info('CLEARING ALL TAGS')
        for mod in Save.mods():
            Save.getMod(mod)[ModKeys.tags] = None

    @staticmethod
    def removeMods(*mods: str) -> None:
        '''Removes mods from MOD_CONFIG'''

        logging.info('Removing mod(s): %s', ', '.join(mods))

        for mod in mods:
            Save.jsonParser.file.pop(mod, None)

    @staticmethod
    def clearModData() -> None:
        '''Wipes the MOD_CONFIG's data'''

        logging.info('DELETING ALL MODS FROM %s', MOD_CONFIG)

        Save.jsonParser.file = Save.jsonParser.default

class OptionsManager():
    '''Manages Program's Settings'''

    config = ConfigParser()
    file = OPTIONS_CONFIG

    def __init__(self, file=OPTIONS_CONFIG) -> None:

        OptionsManager.file = file

        # Ensuring that file exists if file isn't a falsy value
        if not os.path.exists(OptionsManager.file) and OptionsManager.file:
            logging.warning('%s does not exist, creating...', OptionsManager.file)

            # Create a new .ini
            with open(OptionsManager.file, 'w+') as _f:
                pass

        OptionsManager.read()

        if not OptionsManager.config.has_section(OptionKeys.section.value):
            OptionsManager.config.add_section(OptionKeys.section.value)
    
    @staticmethod
    def getList(section: str, option: str, delimiter: str = ',') -> list:
        sequenceString = OptionsManager.config.get(section, option, fallback=None)

        if isinstance(sequenceString, str) and sequenceString:
            sequence = sequenceString.split(delimiter)
            return sequence
        else:
            return []
    
    @staticmethod
    def setList(section: str, option: str, value: Sequence, delimiter: str = ',', sort: bool = False) -> None:
        if sort:
            value = sorted(value)

        list_ = delimiter.join(value)

        OptionsManager.config.set(section, option, list_)
    
    @staticmethod
    def read() -> list[str]:
        '''Reads `OptionsManager.file`'''
        return OptionsManager.config.read(OptionsManager.file)

    @staticmethod
    def writeData() -> None:
        with open(OptionsManager.file, 'w') as f:
            f: TextIO
            OptionsManager.config.write(f)

        logging.info('%s has been saved', OptionsManager.file)

    @staticmethod
    def hasOption(option: str) -> bool:
        return OptionsManager.config.has_option(OptionKeys.section.value, option)

    @staticmethod
    def getMMMUpdateAlert() -> bool:
        return OptionsManager.config.getboolean(OptionKeys.section.value, OptionKeys.mmm_update_alert.value, fallback=True)

    @staticmethod
    def setMMMUpdateAlert(alert: bool = True) -> None:
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.mmm_update_alert.name, str(alert))

    @staticmethod
    def getTheme() -> str:
        return OptionsManager.config.get(OptionKeys.section.value, OptionKeys.color_theme.name, fallback=LIGHT)

    @staticmethod
    def setTheme(theme: str = LIGHT) -> None:
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.color_theme.value, theme)

    @staticmethod
    def getGamepath() -> str:
        return os.path.abspath(OptionsManager.config.get(OptionKeys.section.value, OptionKeys.game_path, fallback=''))

    @staticmethod
    def setGamepath(path: str = '') -> None:
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.game_path.name, os.path.abspath(path))

    @staticmethod
    def getDispath() -> str:
        return os.path.abspath(OptionsManager.config.get(OptionKeys.section, OptionKeys.dispath, fallback=MODS_DISABLED_PATH_DEFAULT))

    @staticmethod
    def setDispath(path: str = MODS_DISABLED_PATH_DEFAULT) -> None:
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.dispath.value, os.path.abspath(path))

    @staticmethod
    def getWindowSize() -> QSize:
        width = OptionsManager.config.getint(OptionKeys.section.value, OptionKeys.windowsize_w.value, fallback=800)
        height = OptionsManager.config.getint(OptionKeys.section.value, OptionKeys.windowsize_h.value, fallback=800)
        return QSize(width, height)

    @staticmethod
    def setWindowSize(size: QSize = QSize(800, 800)) -> None:
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.windowsize_w.value, str(size.width()))
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.windowsize_h.value, str(size.height()))
    
    @staticmethod
    def getLang() -> str:
        return OptionsManager.config.get(OptionKeys.section.value, OptionKeys.lang.value, fallback='en_US')

    @staticmethod
    def setLang(lang: str = 'en_US') -> None:
        OptionsManager.config.set(OptionKeys.section.value, OptionKeys.lang.value, lang)
