from db import get_connection

class Model(object):
    def __init__(self, **kwargs):
        self.attrs = kwargs
        
    def __dict__(self):
        return self.attrs

    @classmethod
    def get_collection(cls):
        conn = get_connection()
        return conn[cls.table]

    def __getitem__(self, item):
        return self.attrs[item]
