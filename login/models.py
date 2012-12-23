from db.models import Model

class User(Model):
    table = "users"
    
    def __init__(self, btid, access_key, confirmed=False, uids={}, **kwargs):
        super(User, self).__init__(
            btid = btid,
            access_key = access_key,
            confirmed = confirmed,
            uids = uids,
            **kwargs
        )
        
    def is_active(self):
        return self.confirmed
        
    def is_authenticated(self):
        return hasattr(self, '_id')
        
    def is_anonymous(self):
        return not hasattr(self, '_id')
        
    def get_id(self):
        return unicode(self._id)

    def get_username(self):
        return self.uids['twitter']
