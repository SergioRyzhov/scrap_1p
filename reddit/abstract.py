from abc import ABC, abstractmethod


class CrudHandlerAbs(ABC):
    """CRUD class

    It handles the data received from the server according to the CRUD methods
    """

    @abstractmethod
    def add_data(self):
        """Add method

        One of the CRUD method which creates data in db
        """
        pass

    @abstractmethod
    def read_data(self):
        """Read method

        The CRUD method which reads the data from db by UNIQUE_ID or without
        (all the data)
        """
        pass

    @abstractmethod
    def update_data(self):
        """Update method

        The CRUD method which updates the data in the db by UNIQUE_ID
        """
        pass

    @abstractmethod
    def delete_data(self):
        """Delete method

        The CRUD method which deletes the data in the db by UNIQUE_ID
        """
        pass
