__author__ = 'azenk'

import couchdb.client
import ConfigParser
import couchmon
from datetime import datetime
import time


class AgentConfigParser(ConfigParser.SafeConfigParser):

	def get_or_default(self,section,option,default):
		try:
			value = self.get(section,option)
		except ConfigParser.NoOptionError:
			value = default
		except ConfigParser.NoSectionError:
			value = default

		return value


class TestMonitoringThread(couchmon.MonitoringThread):

	def run(self):
		while True:
			t = datetime.now()
			print(self.report({"time":"{0}".format(t)}))
			time.sleep(5)

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

	rt = couchmon.ReportingThread(db)
	rt.start()

	tm = TestMonitoringThread()
	tm.start()

	tm.join()
	rt.join()

if __name__ == "__main__":
	main()
