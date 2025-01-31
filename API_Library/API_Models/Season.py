from dataclasses import dataclass,field
from typing import Dict
from .Event import Event
from .Team import Team

@dataclass
class Season:
    """
    Stats for Season.

    Attributes:
        seasonCode (str): The code for the season. Example: '2021'.
        events (Dict[str, Event]): A dictionary mapping event codes to Event objects. Example: events['USAZTUQ'].
    """
    rankedTeams: Dict[int, Team] = field(default_factory=dict)
    seasonCode: str = field(default_factory=str)
    totalTeams: int = field(default_factory=int)
    numAwarded: int = field(default_factory=int)
    events: Dict[str,Event] = field(default_factory=dict)

@dataclass
class History:
    Seasons: Dict[str,Season] = field(default_factory=dict)

    def __post_init__(self):
        self.numSeasons = len(self.Seasons)