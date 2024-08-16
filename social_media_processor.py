from abc import ABC, abstractmethod
from models.user import User

"""
This defines the abstract base class for social media processors.
It consists of the following methods:

        - run
        - authorize
        - fetch_data
        - save_data_to_db
        - extract_and_preprocess
        - enrich
"""


class SocialMediaProcessor(ABC):
    def __init__(self, user: User, platform: str = None):
        """
        Initialize the SocialMediaProcessor.

        """
        self.user = user
        self.platform = platform
        self.name = platform

    @abstractmethod
    def run(self):
        """
        Run the social media processer which will:

            - fetch data from the social media platform
            - extract and preprocess the data
            - save the fetched data to the database
            - process and enrich the data and save it to the database
        """
        pass

    @abstractmethod
    def authorize(self):
        """
        Authorize with the social media platform.
        """
        pass

    @abstractmethod
    def fetch_data(self):
        """
        Fetch data from the social media platform.
        """
        pass

    @abstractmethod
    def save_data_to_db(self, data):
        """
        Save data to the database.
        """
        pass

    @abstractmethod
    def extract_and_preprocess(self, data):
        """
        Extract and preprocess data.
        """
        pass

    @abstractmethod
    def enrich(self):
        """
        Process the data as desired and save it to the database.
        """
        pass
