import json
import time
from flask_rauth import RauthOAuth1, session
from flask import redirect, url_for, request, Blueprint, render_template, abort
from blinker import Namespace
from auth_settings import TOKENS_KEY, REALMS_KEY
from auth import signals
from oauthlib.common import add_params_to_uri
from requests.auth import AuthBase

def oauth_completed(sender, request, access_token):
    realm = request.args['service']
            
    if REALMS_KEY not in session:
        session[REALMS_KEY] = []
        
    session[TOKENS_KEY] = access_token
    
    if realm not in session[REALMS_KEY]:
        session[REALMS_KEY].append(realm)
    
signals.oauth_completed.connect(oauth_completed)

class RealmAuth(AuthBase):
    def __init__(self, realm):
        self.realm = realm

    def __call__(self, r):
        r.data['realm'] = self.realm
        return r

class OAuthBlueprint(Blueprint):
    """
    Creates the endpoints necessary to connect to a webservice using OAuth.
    
    Sends a blinker signal called 'oauth_completed' when OAuth is completed.
    """
    
    def __init__(self, name, api, oauth_refused_view = '.index',
    oauth_completed_view = '.index', realms = []):
        """
        Dynamically builds views and creates endpoints in the routing table for
        connecting to an OAuth-protected webservice.
        """
        super(OAuthBlueprint, self).__init__(name, __name__)
        
        self.api = api
        self.realms = realms
        self.oauth_refused_view = oauth_refused_view
        self.oauth_completed_view = oauth_completed_view
        
        self.add_url_rule('/<realm>/', 'index',
            self.check_realms(self.generate_index()))
        self.add_url_rule('/<realm>/begin', 'begin',
            self.check_realms(self.generate_begin_oauth()))
        self.add_url_rule('/<realm>/finished', 'finished',
            self.check_realms(self.generate_oauth_finished()))

    def check_realms(self, view_func):
        def realm_check(realm):
            if realm in self.realms:
                return view_func(realm)
            else:
                abort(404)
        return realm_check
            
    def generate_index(self):
        """
        Creates a view that prompts the user to connect the OAuth webservice
        to ours.
        """
        def index(realm):
            return render_template('oauth_blueprint/index.html',
                                    service_name = self.name.title(),
                                    begin_url = url_for('.begin'))
        return index
            
    def generate_begin_oauth(self):
        """
        Creates the endpoint that prompts the user to authorize our app to use
        their data on the webservice we're connecting to.
        """
        def begin_oauth(realm):
            url = url_for('.finished', realm = realm, _external = True)
            resp = self.api.authorize(callback = url, method='POST',
                auth=RealmAuth(realm))
            return resp
        return begin_oauth

    def generate_oauth_finished(self):
        """
        Creates the endpoint that handles a successful OAuth completion.
        """
        @self.api.authorized_handler(method='POST')
        def oauth_finished(resp, access_token, realm = None):
            if resp is None or resp == 'access_denied':
                return redirect(self.oauth_refused_url)
            
            signals.oauth_completed.send(
                self, request = request, access_token = access_token)
            
            return redirect(url_for(self.oauth_completed_view))
        return oauth_finished

class BitTrailsOAuth(RauthOAuth1):
    def request(self, method, uri, user, **kwargs):
        if user:
            return super(BitTrailsOAuth, self).request(method, uri,
                oauth_token = user.access_key, **kwargs)
        else:
            return super(BitTrailsOAuth, self).request(method, uri, **kwargs)
    
    def get_datastreams(self, user):
        response = [ (stream, link
            ) for stream, link in self.get('root.json', user = user
            ).content['_links'].items(
            ) if stream != 'self' and stream != 'custom' ]
            
        if 'custom' in response:
            response += self.get_custom_datastreams(user)
            
        return response
    
    def get_custom_datastreams(self, user):
        return [ (stream, link
            ) for stream, link in self.get('custom.json', user = user
            ).content['_links'].items() if stream != 'self' ]    
        
    def get_dimensions(self):
        response = self.get('dimensions.json', user = None).content
        
    def get_chart_data(self, user, path, group_by, start = None, end = None,
    continuous = True):
        params = [
            ('groupBy', json.dumps(group_by))
        ]
        
        if start:
            params.append(('minDate', start))
            
        if end:
            params.append(('maxDate', end))
            
        if continuous:
            params.append(('continuous', 'true'))
        
        return self.get(add_params_to_uri(
            '%s.json' % path, params), user = user).content
        
    def get_correlations(self, user, paths, group_by, start,
    thresholds = ['> 0.5', '< -0.5'], continuous = False):
        params = [
             ('paths', json.dumps(paths)),
             ('minDate', start.isoformat()),
             ('thresholds', json.dumps(thresholds)),
             ('groupBy', json.dumps(group_by)),
             ('continuous', json.dumps(continuous))]
        
        return json.loads(self.get(add_params_to_uri(
            'correlations.json', params), user = user).content)
            
    def create_custom_datastream(self, user, url, name):
        self.post('root.json', data = {
            'url': url, 'path': '/custom/' + name.replace(' ', '_'),
            'title': name }, user = user)
