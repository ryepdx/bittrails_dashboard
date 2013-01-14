from blinker import Namespace
from oauth_blueprint import OAuthBlueprint, OAuth
from settings import (BITTRAILS_KEY, BITTRAILS_SECRET)
                      
from auth import signals

API = OAuth(
            name = 'bittrails',
            base_url = 'http://localhost:5000/api/',
            request_token_url = 'http://localhost:5000/request_token',
            access_token_url = 'http://localhost:5000/access_token',
            authorize_url = 'http://localhost:5000/authorize',
            consumer_key = BITTRAILS_KEY,
            consumer_secret = BITTRAILS_SECRET,
)

BLUEPRINT = OAuthBlueprint(
            name = 'bittrails',
            api = API,
            oauth_refused_view = 'home.index',
            oauth_completed_view = 'home.index',
            realms = ['twitter', 'foursquare', 'lastfm', 'google_tasks']
)

def register_auth_blueprint(app):
    oauth_services = {}
    
    app.register_blueprint(BLUEPRINT, url_prefix = '/auth')
    oauth_services = dict([(realm, BLUEPRINT.api) 
                            for realm in BLUEPRINT.realms])
    
    signals.services_registered.send(oauth_services)
    
    return oauth_services
