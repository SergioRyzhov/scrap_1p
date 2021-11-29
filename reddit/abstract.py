from abc import ABC, abstractmethod


class CrudHandlerAbs(ABC):
    @abstractmethod
    def _add_data(self):
        pass

    @abstractmethod
    def _read_data(self):
        pass

    @abstractmethod
    def _update_data(self):
        pass

    @abstractmethod
    def _delete_data(self):
        pass
