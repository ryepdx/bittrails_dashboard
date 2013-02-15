from db import get_connection
from settings import DATABASE

class Model(dict):
    @classmethod
    def get_collection(cls):
        conn = get_connection(DATABASE)
        return conn[cls.table]
        
    @classmethod
    def find(cls, *args, **kwargs):
        return cls.get_collection().find(*args, **kwargs)
        
    @classmethod
    def find_one(cls, attrs, as_obj = False, **kwargs):
        result = cls.get_collection().find_one(attrs, **kwargs)
        
        if result and as_obj:
            return cls(**result)
        else:
            return result
    
    @classmethod
    def insert(cls, obj):
        return cls.get_collection().insert(obj)
        
    @classmethod
    def save(cls, obj):
        return cls.get_collection().save(obj)

    def __getattr__(self, attr):
        return self[attr]
        
    def __setattr__(self, attr, value):
        self[attr] = value
