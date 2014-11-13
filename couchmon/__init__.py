__author__ = 'azenk'
from threading import Thread, Event, Lock
import couchdb.client
import uuid
import time

class DocumentQueue(object):
	_queue_notifier = Event()
	_queue = []
	_queue_lock = Lock()

	def __init__(self):
		pass

	def enqueue(self, doc):
		doc_id = uuid.uuid4().hex
		doc["_id"] = doc_id
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
	def __init__(self, interval=60):
		Thread.__init__(self)
		self._doc_queue = DocumentQueue()
		self._interval = interval

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