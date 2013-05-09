import flask
import settings

app = flask.Flask('bittrails')

def setup_app(settings, app = app):
    app.secret_key = settings.APP_SECRET_KEY
    app.config['TRAP_BAD_REQUEST_ERRORS'] = settings.DEBUG
    app.config['DATABASE'] = settings.DATABASE
    
    import auth
    import errors
    import login
    import home.views
    import charts.views
    import buffs.views
    import terminal.views
    import flask.ext.login
    
    errors.register_error_pages(app)
    auth.register_auth_blueprint(app)
    app.register_blueprint(home.views.app)
    app.register_blueprint(charts.views.app, url_prefix='/charts')
    app.register_blueprint(buffs.views.app, url_prefix='/buffs')
    
    # Set up login and registration.
    login_manager = flask.ext.login.LoginManager()
    login_manager.login_view = "home.login"
    login_manager.setup_app(app)
    app.login_manager.user_loader(login.load_user)

    return app
    

# The function below gets called from __main__
def main(settings = settings, use_reloader = False):
    setup_app(settings)
        
    if settings.DEBUG:
        app.register_blueprint(terminal.views.app, url_prefix='/terminal')    
    
    # Run the app!
    app.run(host = '0.0.0.0', port = settings.PORT, debug = settings.DEBUG,
        use_reloader = use_reloader)

if __name__ == '__main__':
    main()
