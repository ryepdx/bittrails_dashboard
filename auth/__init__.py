from blinker import Namespace
from oauth_blueprint import OAuthBlueprint, OAuth2Blueprint
from settings import TWITTER_KEY, TWITTER_SECRET, \
                      FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET, \
                      FITBIT_KEY, FITBIT_SECRET
from auth import signals

def get_services():
    return [
        OAuthBlueprint(
            name = 'twitter',
            base_url = 'https://api.twitter.com/1/',
            request_token_url = 'https://api.twitter.com/oauth/request_token',
            access_token_url = 'https://api.twitter.com/oauth/access_token',
            authorize_url = 'https://api.twitter.com/oauth/authenticate',
            consumer_key = TWITTER_KEY,
            consumer_secret = TWITTER_SECRET,
            oauth_refused_view = 'home.index',
            oauth_completed_view = 'home.index'
        ),
        OAuth2Blueprint(
            name = 'foursquare',
            base_url = 'https://api.foursquare.com/v2/',
            access_token_url = 'https://foursquare.com/oauth2/access_token',
            authorize_url = 'https://foursquare.com/oauth2/authenticate',
            consumer_key = FOURSQUARE_CLIENT_ID, 
            consumer_secret = FOURSQUARE_CLIENT_SECRET,
            oauth_refused_view = 'home.index',
            oauth_completed_view = 'home.index'
        ),
        OAuthBlueprint(
            name = 'fitbit',
            base_url = 'http://api.fitbit.com/',
            request_token_url = 'http://api.fitbit.com/oauth/request_token',
            access_token_url = 'http://api.fitbit.com/oauth/access_token',
            authorize_url = 'http://api.fitbit.com/oauth/authorize',
            consumer_key = FITBIT_KEY, 
            consumer_secret = FITBIT_SECRET,
            oauth_refused_view = 'home.index',
            oauth_completed_view = 'home.index'
        )
    ]

def register_auth_blueprints(app):
    oauth_services = {}
     
    for service in get_services():
        app.register_blueprint(service.blueprint,
            url_prefix = '/auth/%s' % service.name)
        oauth_services[service.name] = service.api
        
    signals.blueprints_registered.send(oauth_services)
    
    return oauth_services
