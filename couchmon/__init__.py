__author__ = 'azenk'
from threading import Thread, Event, Lock
import couchdb.client
import uuid
import time


class CouchmonRecord(couchdb.client.Document):

	_type = None
	_keyfields = []

	def __init__(self):
		couchdb.client.Document.__init__(self)
		self['type'] = self.type

	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value):
		self._type = value

	@property
	def keyfields(self):
		return self._keyfields

	@keyfields.setter
	def keyfields(self, value):
		self._keyfields = value

	@staticmethod
	def record_query(db, record):
		if isinstance(record,CouchmonRecord):
			query_conds = " && ".join(["doc.type == '{0}'".format(record.type)] +
																map(lambda x: "doc.{0} == '{1}'".format(x,record[x]),record.keyfields))
			query_func = "function(doc){{if ({0}){{emit(doc._id,doc)}}}};".format(query_conds)
			print(query_func)
			result = db.query(map_fun=query_func)
			if result.total_rows == 1:
				row = result.rows[0]
				return row.key
			else:
				raise Exception("Too many records returned")

class DocumentQueue(object):
	_queue_notifier = Event()
	_queue = []
	_queue_lock = Lock()

	def __init__(self):
		pass

	def enqueue(self, doc):
		if "_id" not in doc:
			doc_id = uuid.uuid4().hex
			doc["_id"] = doc_id
		else:
			doc_id = doc["_id"]

		DocumentQueue._queue_lock.acquire()
		DocumentQueue._queue.append(doc)
		DocumentQueue._queue_lock.release()
		DocumentQueue._queue_notifier.set()
		return doc_id

	def dequeue(self):
		DocumentQueue._queue_lock.acquire()
		try:
			doc = DocumentQueue._queue.pop(0)
		except:
			doc = None
		finally:
			DocumentQueue._queue_lock.release()

		if doc is None:
			raise LookupError()
		return doc

	def wait(self, timeout=None):
		DocumentQueue._queue_notifier.wait(timeout)


class ReportingThread(Thread):
	def __init__(self, couchmon_db):
				Thread.__init__(self)
				self._db = couchmon_db
				self._doc_queue = DocumentQueue()

	def run(self):
		while True:
			try:
				doc = self._doc_queue.dequeue()
				self._db.save(doc)
			except LookupError, e:
				self._doc_queue.wait(5)

class MonitoringThread(Thread):
	def __init__(self, interval=60, db=None):
		Thread.__init__(self)
		self._doc_queue = DocumentQueue()
		self._interval = interval
		self._db = db

	@property
	def interval(self):
		return self._interval

	@interval.setter
	def interval(self, value):
		self._interval = value

	def run(self):
		while True:
			# Do some work
			doc_id = self.report({"Some key":"Some data"})
			time.sleep(self.interval)

	def report(self, data):
		return self._doc_queue.enqueue(data)