# Testing app / config
from repoze.sendmail.interfaces import IMailDelivery
from zope.interface import implements
from zope.password.password import SSHAPasswordManager
from cartouche.interfaces import IRegistrations

DIVIDER =  "#" * 80

class FauxMailDelivery(object):
    implements(IMailDelivery)

    def send(self, from_addr, to_addrs, message):
        print DIVIDER
        print 'From:    %s' % from_addr
        print 'To:      %s' % ', '.join(to_addrs)
        print '-' * 80
        print message
        print DIVIDER


class Dummy(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

def _factory(_make_info):
    class FauxRegistrations(object):
        implements(IRegistrations)
        _store = {} # yes, a mutable default

        def __init__(self, context):
            pass

        def set(self, key, **kw):
            print DIVIDER
            print 'Setting registration for key: %s' % key
            print DIVIDER
            info = _make_info(key, kw)
            self._store[key] = info

        def set_record(self, key, record):
            print DIVIDER
            print 'Adding copied registration for key: %s' % key
            print DIVIDER
            self._store[key] = record

        def get(self, key, default=None):
            return self._store.get(key, default)

        def remove(self, key, default=None):
            print DIVIDER
            print 'Removing registration for key: %s' % key
            print DIVIDER
            del self._store[key]
    return FauxRegistrations


def _make_pending(key, kw):
    token = kw['token']
    return Dummy(email=key, token=token)


def _make_confirmed(key, kw):
    return Dummy(email=key, login=key,
                 password=None, security_question=None, security_answer=None)


FauxPendingRegistrations = _factory(_make_pending)
FauxByEmailRegistrations = _factory(_make_confirmed)
FauxByLoginRegistrations = _factory(_make_confirmed)


class FauxAuthentication(object):
    def authenticate(self, environ, identity):
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None
        pwd_mgr = SSHAPasswordManager()
        record = FauxByLoginRegistrations(None).get(login)
        if pwd_mgr.checkPassword(record.password, password):
            return login
