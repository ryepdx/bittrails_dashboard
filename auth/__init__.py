import settings
from blinker import Namespace
from oauth_blueprint import OAuthBlueprint, BitTrailsOAuth
                      
from auth import signals

API = BitTrailsOAuth(
            name = 'bittrails',
            base_url = 'http://' + settings.BITTRAILS_API_HOST + '/v1/',
            request_token_url = 'http://' + settings.BITTRAILS_HOST + '/request_token',
            access_token_url = 'http://' + settings.BITTRAILS_HOST + '/access_token',
            authorize_url = 'http://' + settings.BITTRAILS_HOST + '/authorize',
            consumer_key = settings.BITTRAILS_KEY,
            consumer_secret = settings.BITTRAILS_SECRET,
)

BLUEPRINT = OAuthBlueprint(
            name = 'bittrails',
            api = API,
            oauth_refused_view = 'home.index',
            oauth_completed_view = 'home.index',
            realms = ['twitter', 'foursquare', 'lastfm', 'google']
)

def register_auth_blueprint(app):
    oauth_services = {}
    
    app.register_blueprint(BLUEPRINT, url_prefix = '/auth')
    oauth_services = dict([(realm, BLUEPRINT.api) 
                            for realm in BLUEPRINT.realms])
    
    signals.services_registered.send(oauth_services)
    
    return oauth_services
