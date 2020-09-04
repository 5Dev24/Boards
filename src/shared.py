import base64, threading, re, database
from timeit import default_timer

class Util:

	@staticmethod
	def ToBase64Bytes(inputString: str):
		if type(inputString) not in (str, bytes, bytearray): return None
		return base64.b64encode(bytes(inputString, "utf-8") if type(inputString) == str else inputString)

	@staticmethod
	def FromBase64Bytes(inputString: str):
		if type(inputString) not in (str, bytes, bytearray): return None
		return base64.b64decode(bytes(inputString, "utf-8") if type(inputString) == str else inputString)

	@staticmethod
	def ToBase64String(inputString: str):
		return Util.ToBase64Bytes(inputString).decode("utf-8", "backslashreplace")

	@staticmethod
	def FromBase64String(inputString: str):
		return Util.FromBase64Bytes(inputString).decode("utf-8", "backslashreplace")

	@staticmethod
	def ReadLine(file = None):
		if file is None: return None
		if (line := file.readline()) != b"":
			return line.rstrip(b"\n")
		raise EOFError()

class Timer:

	def __init__(self):
		self.start = default_timer()

	def stop(self):
		return default_timer() - self.start

class ConfigFile:

	NameCheck = re.compile("^[a-zA-Z-]*$")

	@staticmethod
	def FromFile(file = None):
		pass

	def __init__(self, name: str):
		if ConfigFile.NameCheck.match(name): self.name = name
		else: raise ValueError("name can only contain letters and dashes")
		self.items = {}

	def save(self, file = None):
		if file is None:
			file = open(f"{self.name}.cfg", "wb")

		file.write(database.Util.Compress(self.name))
		for key, value in self.items.items():
			if type(key) != str: continue
			if database.Type.GetObjectType(value) == database.Type.Null: continue
			encodedKey = key.encode("utf-8")
			if len(key) > 255: continue
			file.write(b"\n")
			file.write(bytes([len(encodedKey)]))
			file.write(encodedKey)
			file.write(database.Util.Compress(value))

class Reference:

	def __init__(self, pool: int, index: int):
		self.pool = pool
		self.index = index

	def update(self, index: int):
		self.index = index

class Pool:

	__pools__ = []
	__lock__ = threading.RLock()

	def __init__(self):
		try:
			Pool.__lock__.acquire()
			self.id = Reference(-1, len(Pool.__pools__))
			self.type = None
			self._data = []
			self._lock = threading.RLock()

			Pool.__pools__.append(self)
		finally:
			Pool.__lock__.release()

	def destroy(self):
		try:
			Pool.__lock__.acquire()
			Pool.__pools__.remove(self)

			for pool in Pool.__pools__:
				ref = pool.id
				if ref.index > self.id.index and ref.pool == -1:
					ref.index -= 1
		finally:
			Pool.__lock__.release()

	def get(self, ref: Reference):
		if type(ref) != Reference: raise ValueError("Reference to object wasn't a Reference object")

		try:
			self._lock.acquire()
			if ref.pool == self.id.index:
				objData = self._data[ref.index]
				if ref != objData[0]:
					raise ValueError("The reference given matches the pool and index but isn't the same object stored")

				return objData[1]

			raise ValueError(f"Reference to object's pool ({ref.pool}) didn't match self ({self.id.index})")
		finally:
			self._lock.release()

	def add(self, obj: object):
		try:
			self._lock.acquire()

			if self.type == None:
				self.type = type(obj)

			if self.type == type(obj):
				ref = Reference(self.id.index, len(self._data))
				self._data.append((ref, obj))
				return ref

			raise ValueError(f"Pool's type ({self.type.__name__}) didn't match object's type ({type(obj).__name__})")
		finally:
			self._lock.release()

	def remove(self, ref: Reference):
		if type(ref) != Reference: raise ValueError("Reference to object wasn't a Reference object")
		if ref.pool < -1 or ref.index < 0: return False # Reference was destroyed previously

		try:
			self._lock.acquire()

			if ref.pool == self.id.index:
				objRef = self._data[ref.index][0]
				if objRef != ref:
					raise ValueError("The reference given matches the pool and index but isn't the same object stored")

				objIndex = ref.index
				objRef.pool = -2
				objRef.index = -1

				del self._data[objIndex]

				# Fix indexes that follow the removed object
				for i in range(objIndex, len(self._data)):
					self._data[i][0].index -= 1

				return True

			return False
		finally:
			self._lock.release()

	def verify(self, shouldRaise: bool = False):
		try:
			self._lock.acquire()
			for point in self._data:
				if type(point) != tuple:
					raise TypeError(f"An object seemed to be malformed and isn't saved in a (reference, object) pair")

				pointType = type(point[1])
				if pointType != self.type:
					if shouldRaise:
						raise TypeError(f"An object was found (of type {pointType.__name__}) that didn't match the pool's type ({self.type.__name__})")
					else:
						return False

			return True
		finally:
			self._lock.release()

	def purge(self):
		try:
			self._lock.acquire()
			remove = []
			for i in range(len(self._data)):
				point = self._data[i]
				if type(point) != tuple or len(point) != 2 or type(point[0]) != Reference \
					or point[0].pool != self.id.index or point[0].index != i \
						or (self.type != None and type(point[1]) != self.type):
					remove.append(i)

			# Remove objects from greatests to least to not have to
			# correct indexes and edit their references to be unusable
			for i in remove[::-1]:
				objRef = self._data[i][0]
				objRef.pool = -2
				objRef.index = -1
				del self._data[i]

			# Correct indexes when deleting
			if len(remove) > 0:
				for i in range(remove[0], len(self._data)):
					self._data[i][0].index = i

		finally:
			self._lock.release()

class Identifiable:

	def __init__(self, id):
		self.id = id

class Author(Identifiable):

	def __init__(self, id, publicKey, postCount, posts):
		super().__init__(id)
		self.publicKey = publicKey
		self.postCount = postCount
		self.posts = posts

class Post(Identifiable):

	def __init__(self, id, signature, text):
		super().__init__(id)
		self.signature = signature
		self.text = text

class Thread(Identifiable):

	def __init__(self, id, posts):
		super().__init__(id)
		self.posts = posts

	@property
	def header(self):
		if not len(self.posts): return None
		return self.posts[0]

	@property
	def tail(self):
		if not len(self.posts): return None
		return self.posts[-1]

class Board(Identifiable):

	def __init__(self, id, threads):
		super().__init__(id)
		self.threads = threads
