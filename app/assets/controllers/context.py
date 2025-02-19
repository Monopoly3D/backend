from abc import ABC, abstractmethod


class ContextController(ABC):
    @abstractmethod
    def add(
            self,
            *args,
            **kwargs
    ) -> None:
        pass

    @abstractmethod
    def get(
            self,
            *args,
            **kwargs
    ) -> None:
        pass

    @abstractmethod
    def exists(
            self,
            *args,
            **kwargs
    ) -> None:
        pass

    @abstractmethod
    def remove(
            self,
            *args,
            **kwargs
    ) -> None:
        pass
