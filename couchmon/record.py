__author__ = 'azenk'

import couchmon

class Host(couchmon.CouchmonRecord):

	_type = 'host'
	_keyfields = ['hostname']


