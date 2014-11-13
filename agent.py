__author__ = 'azenk'

import couchdb.client
import ConfigParser
import couchmon, couchmon.record
from datetime import datetime
import time
import socket

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
			time.sleep(self.interval)


class HostHeartBeatThread(couchmon.MonitoringThread):

	def run(self):
		# find/create doc for this host.  Key off of fqdn for now.  Maybe write doc_id to file?
		h = couchmon.record.Host()
		h["hostname"] = socket.getfqdn()
		try:
			doc_id, doc_rev = couchmon.CouchmonRecord.record_query(self._db, h)
			h["_id"] = doc_id
			h["_rev"] = doc_rev
		except Exception, e:
			print(e)
			host_id = self.report(h)
			h["_id"] = host_id
			pass
		while True:
			h["last_seen"] = "{0}".format(datetime.now())
			#print(h)
			self.report(h)
			time.sleep(self.interval)

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

	tm = HostHeartBeatThread(interval=15,db=db)
	tm.start()

	tm.join()
	rt.join()

if __name__ == "__main__":
	main()
