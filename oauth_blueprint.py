from flask_oauth import OAuth
from flask import redirect, url_for, request, Blueprint, render_template
from blinker import Namespace

class OAuthBlueprint(object):
    """
    Creates the endpoints necessary to connect to a webservice using OAuth.
    """
    
    def __init__(self, service_name, api_url, request_token_url, 
    access_token_url, authorize_url, consumer_key, consumer_secret,
    oauth_refused_view = '.index',
    oauth_completed_view = '.index'):
        """
        Dynamically builds views and creates endpoints in the routing table for
        connecting to an OAuth-protected webservice.
        """
        
        oauth = OAuth()  
        signals = Namespace()
        self.access_token = None
        self.service_name = service_name
        self.oauth_refused_url = oauth_refused_url
        self.oauth_completed_url = oauth_completed_url
        
        self.blueprint = Blueprint('%s_auth' % service_name, __name__)
        self.oauth_app = oauth.remote_app(
            service_name,
            base_url = api_url,
            request_token_url = request_token_url,
            access_token_url = access_token_url,
            authorize_url = authorize_url,
            consumer_key = consumer_key,
            consumer_secret = consumer_secret
        )
        
        self.oauth_completed = signals.signal('oauth_completed')
        
        self.blueprint.add_url_rule('/', 'index', self.generate_index())
        self.blueprint.add_url_rule('/begin_oauth', 'begin_oauth', self.generate_begin_oauth())
        self.blueprint.add_url_rule('/oauth_finished', 'oauth_finished',
            self.generate_oauth_finished())
        self.generate_get_oauth_token()
    
    def generate_index(self):
        """
        Creates a view that prompts the user to connect the OAuth webservice
        to ours.
        """
        def index():
            return render_template('oauth_blueprint/index.html',
                                    self.service_name)
        return index
            
    def generate_begin_oauth(self):
        """
        Creates the endpoint that prompts the user to authorize our app to use
        their data on the webservice we're connecting to.
        """
        def begin_oauth():
            url = url_for('.authorized', 
                next = '/connected_%s' % self.service_name)
            resp = self.oauth_app.authorize(callback = url)
            return resp
        return begin_oauth

    def generate_oauth_finished(self):
        """
        Creates the endpoint that handles a successful OAuth completion.
        """
        @self.oauth_app.authorized_handler
        def oauth_finished(resp):
            next_url = request.args.get('next') or url_for(self.oauth_refused_view)
            if resp is None:
                return redirect(next_url)
            
            self.access_token = (
                resp['oauth_token'],
                resp['oauth_token_secret']
            )
            
            self.oauth_completed.send(self, resp)
            
            return redirect(url_for(self.oauth_completed_view))
        return oauth_finished

    def generate_get_oauth_token(self):
        """
        Registers the token-getter with Flask OAuth.
        """
        @self.oauth_app.tokengetter
        def get_oauth_token(token=None):
            return self.access_token
