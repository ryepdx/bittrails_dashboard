''''
Provides environment switching for settings via command line parameters.
Specifically, it allows the user to specify whether to use the "test" settings,
which comes in handy when starting up the server for the sake of running
automated tests against it.
'''
import app
import argparse
import nose
import pymongo
import settings
import settings_test
import sys

def get_args():
    parser = argparse.ArgumentParser(description='Run Bit Trails Dashboard.')
    parser.add_argument('--test', dest='env_settings', action='store_const',
        const = settings_test, default = settings,
        help=('use the settings in settings_test'))
    parser.add_argument('--unittests', dest='run_unittests',
        action='store_const', const = True, default = False,
        help='run unit tests')
    parser.add_argument('--no-server', dest='run_server',
        action='store_const', const = False, default = True,
        help='do not start the server')
    parser.add_argument('--reset-database', dest='reset_db',
        action='store_const', const = True, default = False,
        help='wipe out the database and restore from fixtures')
    parser.add_argument('--use-reloader', dest='use_reloader',
        action='store_const', const = True, default = False,
        help='reload server on file change (do not use with --reset-database)')
    return parser.parse_args()

def main(args):
    settings = args.env_settings
    
    if args.reset_db:
        if args.use_reloader:
            print "--use-reloader set. Ignoring --reset-database."
        else:
            really_reset = raw_input(
                "Resetting the %s database" % settings.DATABASE
                + " will permanently delete all the data in it!\nAre you sure "
                + "you want to do this? (Y/N)")
            
            if really_reset.upper() == "Y":
                print "Wiping db and loading fixtures..."
                pymongo.MongoClient().drop_database(settings.DATABASE)
            else:
                print "Ignoring --reset-database this time, then."
           
    if args.run_unittests:
        nose.run(argv = sys.argv[:1])
        
    if args.run_server:
        app.main(settings = settings, use_reloader = args.use_reloader)

if __name__ == '__main__':
    main(get_args())
