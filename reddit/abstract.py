from abc import ABC, abstractmethod


class CrudHandlerAbs(ABC):
    @abstractmethod
    def add_data(self):
        pass

    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def update_data(self):
        pass

    @abstractmethod
    def delete_data(self):
        pass
