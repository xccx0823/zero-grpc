from abc import abstractmethod

from zero import Zero


class ZeroPkgInitBase:

    @abstractmethod
    def init_app(self, app: Zero):
        raise NotImplementedError("Initialization with Zero app must implement the init app method.")
