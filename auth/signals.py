from blinker import Namespace

signals = Namespace()
blueprints_registered = signals.signal('auth.blueprints_registered')
