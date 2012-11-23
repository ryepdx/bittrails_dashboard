from flask_rauth import RauthOAuth1, RauthOAuth2, session
from flask import redirect, url_for, request, Blueprint, render_template
from blinker import Namespace

def oauth_completed(sender, access_token):
    session[sender.access_token_key()] = access_token

class AccessTokenMixin(object):
    def access_token_key(self):
        return '%s_token' % self.name

class OAuthBlueprintBase(AccessTokenMixin):
    """
    Creates the endpoints necessary to connect to a webservice using OAuth.
    
    Sends a blinker signal called 'oauth_completed' when OAuth is completed.
    """
    
    def __init__(self, name, base_url,
    access_token_url, authorize_url, consumer_key, consumer_secret,
    oauth_refused_view = '.index',
    oauth_completed_view = '.index',
    request_token_url = None):
        """
        Dynamically builds views and creates endpoints in the routing table for
        connecting to an OAuth-protected webservice.
        """
        signals = Namespace()
        
        self.name = name
        self.oauth_refused_view = oauth_refused_view
        self.oauth_completed_view = oauth_completed_view
        
        self.oauth_completed = signals.signal('oauth_completed')
        self.oauth_completed.connect(oauth_completed, sender=self)
        
        self.blueprint = Blueprint('oauth_%s' % name, __name__)
        self.blueprint.add_url_rule('/', 'index', self.generate_index())
        self.blueprint.add_url_rule('/begin', 'begin', self.generate_begin_oauth())
        self.blueprint.add_url_rule('/finished', 'finished',
            self.generate_oauth_finished())
    
    def generate_index(self):
        """
        Creates a view that prompts the user to connect the OAuth webservice
        to ours.
        """
        def index():
            return render_template('oauth_blueprint/index.html',
                                    service_name = self.name.title(),
                                    begin_url = url_for('.begin'))
        return index
            
    def generate_begin_oauth(self):
        """
        Creates the endpoint that prompts the user to authorize our app to use
        their data on the webservice we're connecting to.
        """
        def begin_oauth():
            url = url_for('.finished', _external = True)
            resp = self.api.authorize(callback = url)
            return resp
        return begin_oauth

    def generate_oauth_finished(self):
        """
        Creates the endpoint that handles a successful OAuth completion.
        """
        @self.api.authorized_handler
        def oauth_finished(resp, access_token):
            if resp is None or resp == 'access_denied':
                return redirect(self.oauth_refused_url)
            
            self.oauth_completed.send(self, access_token = access_token)
            
            return redirect(url_for(self.oauth_completed_view))
        return oauth_finished


class OAuth(RauthOAuth1, AccessTokenMixin):
    def request(self, method, uri, **kwargs):
        return super(OAuth, self).request(method, uri,
            oauth_token = session[self.access_token_key()], **kwargs)

class OAuth2(RauthOAuth2, AccessTokenMixin):
    def request(self, method, uri, **kwargs):
        return super(OAuth2, self).request(method, uri,
            access_token = session[self.access_token_key()], **kwargs)


class OAuthBlueprint(OAuthBlueprintBase):
    """
    Creates the endpoints necessary to connect to a webservice using OAuth.
    
    Sends a blinker signal called 'oauth_completed' when OAuth is completed.
    """
    
    def __init__(self, **kwargs):
        """
        Dynamically builds views and creates endpoints in the routing table for
        connecting to an OAuth-protected webservice.
        """
        
        self.api = OAuth(
            name = kwargs['name'],
            base_url = kwargs['base_url'],
            request_token_url = kwargs['request_token_url'],
            access_token_url = kwargs['access_token_url'],
            authorize_url = kwargs['authorize_url'],
            consumer_key = kwargs['consumer_key'],
            consumer_secret = kwargs['consumer_secret']
        )
        return super(OAuthBlueprint, self).__init__(**kwargs)
            
class OAuth2Blueprint(OAuthBlueprintBase):
    """
    Creates the endpoints necessary to connect to a webservice using OAuth.
    
    Sends a blinker signal called 'oauth_completed' when OAuth is completed.
    """
    
    def __init__(self, **kwargs):
        """
        Dynamically builds views and creates endpoints in the routing table for
        connecting to an OAuth-protected webservice.
        """
        
        self.api = OAuth2(
            name = kwargs['name'],
            base_url = kwargs['base_url'],
            access_token_url = kwargs['access_token_url'],
            authorize_url = kwargs['authorize_url'],
            consumer_key = kwargs['consumer_key'],
            consumer_secret = kwargs['consumer_secret']
        )
        
        return super(OAuth2Blueprint, self).__init__(**kwargs)
