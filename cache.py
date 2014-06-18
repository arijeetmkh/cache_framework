class GlobalConnection(object):
    """
    This global singleton class keeps track of all connections currently active, restricts the number of connections, returns valid connections upon creation request, releases connections safely, and implements cache get, set operations on the global cache
    """
    
    _config = {}
    objects = {}
    _LIMIT = 1
    _cache = {}
    connections = set()
    _ALLOWED_BACKENDS = ['IN_MEMORY_DICT']
    _backend = None
    _host = None
    _port = None

    def __new__(cls, *args, **kwargs):
        """
        Check if the object exists or not. If not then create a new object and return it, else return same object
        """
        if cls not in cls.objects:
            cls.objects[cls] = super(GlobalConnection, cls).__new__(cls, *args, **kwargs)
            
        return cls.objects[cls]


    def _config(self, host, port, backend, limit):
        """
        Method to help set the configuration options
        """
        self._host = host

        if isinstance(port, (int,long)):
            self._port = port
        else:
            raise ValueError('Invalid Port. Must be Integer')

        if backend in self._ALLOWED_BACKENDS:
            self._backend = backend
        else:
            raise Exception('Unsupported Backend')

        self._LIMIT = limit


    def getConnection(self, name):
        """
        Method to get a new connection. Performs required checks before returning a valid connections.
        """
        if self._LIMIT <= 0:
            raise Exception('Connection Limit exceeded')
        
        conn_object = None

        try:
            conn_object = Connection(name)
            self.connections.add(conn_object)
            self._LIMIT = self._LIMIT - 1
        except:
            # Handle Server Down Exception Here
            pass
        finally:
            return conn_object

    def releaseConnection(self, obj):
        self.connections.remove(obj)
        self._LIMIT = self._LIMIT + 1

    def _cache_set(self, key, value):
        self._cache[key] = value
    
    def _cache_get(self, key):
        
        if key in self._cache:
            return self._cache[key]
        else:
            raise KeyError

    def _cache_del(self, key):

        if key not in self._cache:
            raise KeyError
        else:
            del self._cache[key]

    def is_valid(self, obj):
        return obj in self.connections
        

class Connection:
    """
    Instances of this Connection class constitute one of the connections governed by the overall singleton. This class also contains the API layer and provides member methods to support insertion and retreival from the cache.
    """
    
    err = None
    name = ""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
    def cache_set(self, key, value):
        if not _global_connection.is_valid(self):
            raise Exception('Invalid Connection')
        _global_connection._cache_set(key, value)
        return True

    def cache_get(self, key):
        if not _global_connection.is_valid(self):
            raise Exception('Invalid Connection')

        value = False
        try:
            value = _global_connection._cache_get(key)
        except KeyError as err:
            self.err = str(err)
        finally:
            return value

    def __delitem__(self, key):
        if not _global_connection.is_valid(self):
            raise Exception('Invalid Connection')
        _global_connection._cache_del(key)
        return True

    def is_valid(self):
        return _global_connection.is_valid(self)

    def get_last_error(self):
        return self.err


def configure(host='localhost', port=12345, backend='IN_MEMORY_DICT', limit=100):
    """
    Method to use the singleton connection class and set up its configuration
    """
    _global_connection._config(host, port, backend, limit)


def get_connection(name=""):
    """
    Helper method to call the singleton connection class's getConnection method i n order to return a valid connection
    """
    return _global_connection.getConnection(name)


def release_connection(obj):
    """
    Helper method which accepts an instance of Connection, and safely releases it by calling the singleton connection class's releaseConnection method.
    """
    if not isinstance(obj, Connection) and obj not in _global_connection.connections:
        return False
    else:
        _global_connection.releaseConnection(obj)
        return True

# Create the singleton object
_global_connection = GlobalConnection()