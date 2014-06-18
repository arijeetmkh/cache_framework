cache_framework
===============

A dummy cache framework

USAGE
=====

1. import cache
2. cache.configure(host='localhost', port=12345, backend='IN_MEMORY_DICT', limit=100)
3. my_conn = cache.get_connection('CONNECTION_NAME')
4. my_conn.is_valid()
5. myconn.cache_set('key', 'value')
6. myconn.cache_get('key')
7. del myconn['key']
8. cache.release_connection(myconn)
