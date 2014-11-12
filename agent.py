__author__ = 'azenk'

import couchdb.client
import ConfigParser


class AgentConfigParser(ConfigParser.SafeConfigParser):

	def get_or_default(self,section,option,default):
		try:
			value = self.get(section,option)
		except ConfigParser.NoOptionError:
			value = default
		except ConfigParser.NoSectionError:
			value = default

		return value


class Person(couchdb.client.Document):

	def __init__(self,name):
		couchdb.client.Document.__init__(self)
		self['type'] = 'Person'
		self['name'] = name


def main():
	cp = AgentConfigParser()
	cp.read('agent.cfg')
	server_url = cp.get_or_default('Server','url','http://localhost:5984')
	db_name = cp.get_or_default('Server','db','python-tests')

	server = couchdb.client.Server(server_url)
	if db_name not in server:
		db = server.create(db_name)
	else:
		db = server[db_name]

	p = Person('Mary Jane')
	doc_id, doc_rev = db.save(p)
	print(p['type'])
	print(p['name'])

	del db[doc_id]

if __name__ == "__main__":
	main()
