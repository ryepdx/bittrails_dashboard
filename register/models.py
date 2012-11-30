from models import Model

class User(Model):
    table = "Users"
    
    def __init__(self, email, access_keys, confirmed = False):
        super(User, self).__init__(
            email = email,
            access_keys = access_keys,
            confirmed = confirmed
        )
