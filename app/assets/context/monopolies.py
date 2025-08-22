from collections import defaultdict
from typing import Dict, Any, List, TYPE_CHECKING

from app.assets.context.abstract import Context
from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.fields.company import Company
from app.assets.objects.monopoly import Monopoly

if TYPE_CHECKING:
    from app.assets.objects.game import Game


class Monopolies(Context):
    def __init__(self) -> None:
        self._monopolies: Dict[MonopolyType, Monopoly] = defaultdict(Monopoly)
        self._game: Game | None = None

    def init(
            self,
            monopolies: Dict[str, Any] | None,
            companies: List[Company] | None,
            *,
            game: Game
    ) -> None:
        self._monopolies.clear()

        if monopolies is not None:
            for monopoly_type, monopoly in monopolies.items():
                self._monopolies[MonopolyType(monopoly_type)] = Monopoly.from_json(monopoly)

        if companies is None:
            return

        for company in companies:
            self.add(company)

    def to_json(self) -> Dict[str, Any]:
        return {monopoly_type: monopoly.to_json() for monopoly_type, monopoly in self._monopolies.items()}

    @property
    def game(self) -> Game:
        return self._game

    def add(
            self,
            company: Company
    ) -> None:
        company.monopoly = self._monopolies[company.monopoly_type]
        self._monopolies[company.monopoly_type].companies.append(company)

    def get(
            self,
            monopoly_type: MonopolyType
    ) -> Monopoly | None:
        if monopoly_type in self._monopolies:
            return self._monopolies[monopoly_type]

    def reset_all_filiations(self) -> None:
        for monopoly in self._monopolies.values():
            monopoly.is_filiated = False
