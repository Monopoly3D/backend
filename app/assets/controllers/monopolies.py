from collections import defaultdict
from typing import Dict, Any, List

from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.fields.company import Company
from app.assets.objects.monopoly import Monopoly


class MonopoliesController:
    def __init__(self) -> None:
        self.__monopolies: Dict[MonopolyType, Monopoly] = defaultdict(Monopoly)
        self.__game_instance: Any = None

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value

    def setup(
            self,
            companies: List[Company] | None = None,
            *,
            game_instance: Any = None
    ) -> None:
        self.game = game_instance

        if companies is None:
            return

        for company in companies:
            self.__monopolies[company.monopoly_type].add(company)

    def to_json(self) -> Dict[str, Any]:
        return {monopoly_type: monopoly.to_json() for monopoly_type, monopoly in self.__monopolies.items()}

    def get(
            self,
            monopoly_type: MonopolyType
    ) -> Monopoly | None:
        if monopoly_type in self.__monopolies:
            return self.__monopolies[monopoly_type]

    def reset_all_filiations(self) -> None:
        for monopoly in self.__monopolies.values():
            monopoly.is_filiated = False
