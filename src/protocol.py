import communication

class Protocol(type):

	__protocols__ = []

	def __new__(cls, name, bases, namespace, **kwargs):
		if type(kwargs) != dict or "version" not in kwargs: return None
		namespace["__version__"] = kwargs["version"]

		def _validate(self):
			print("Valid called form a", type(self).__name__)

		namespace["validate"] = _validate

		proto = super().__new__(cls, name, bases, namespace)
		if proto is not None:
			Protocol.__protocols__.append(proto)
			print(f"Loaded Protocol {name} v{namespace['__version__']}")
		return proto

	def valid(self):
		print("Valid called from a", type(self).__name__)

class ProtoObject:

	def __init__(self, data: bytes):
		if type(data) != bytes: return None
		self.data = data
		self._read = 0

	def readTo(self, stop: int):
		if (type(stop) != bytes or len(stop) != 1) and type(stop) != int: return None
		if type(stop) == bytes: stop = stop[0]

		start = self._read
		try:
			self._read = self.data.index(stop, self._read)
		except ValueError:
			self._read = len(self.data) - 1

		return self.data[start:self._read]

class ProtoSync(metaclass = Protocol, version = "1.0.0"):

	def step(self):
		pass

class Keys(metaclass = Protocol, version = "1.0.0"): pass
class Query(metaclass = Protocol, version = "1.0.0"): pass
class Post(metaclass = Protocol, version = "1.0.0"): pass