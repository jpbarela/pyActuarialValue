import os

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class BaseDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database_path = os.path.join(os.path.dirname(__file__), '../data/test.db')

        cls.engine = create_engine('sqlite:///'+database_path, convert_unicode=True)
        cls.Session = sessionmaker()

    def setUp(self):
        self.Session.configure(bind=self.engine)
        self.session = self.Session(bind=self.engine)
