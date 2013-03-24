import unittest
import app as dashboard

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        dashboard.app.config['TESTING'] = True
        self.app = dashboard.app.test_client()

    def test_pass(self):
        assert True
        print "Tested"

