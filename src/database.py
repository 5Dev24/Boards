from enum import Enum
import zlib, sys, shared

class Type(Enum):

	Null = 0
	String  = 1
	Integer = 2
	Boolean = 3
	EmptyList = 4
	IntegerList = 5
	BooleanList = 6

	@staticmethod
	def GetObjectType(obj: object):
		objType = type(obj)

		if objType == str: return Type.String
		elif objType == int: return Type.Integer
		elif objType == bool: return Type.Boolean
		elif objType == list:
			if len(obj) < 1: return Type.EmptyList
			else:
				expectedType = type(obj[0])
				if expectedType not in (int, bool): return Type.Null

				for item in obj[1:]:
					if type(item) != expectedType:
						return Type.Null

				if expectedType == int:
					return Type.IntegerList
				elif expectedType == bool:
					return Type.BooleanList

		return Type.Null

class Compression:

	@staticmethod
	def Compress(obj: object):
		if type(obj) not in (str, int, bool, list): return None
		objType = Type.GetObjectType(obj)

		if objType == Type.String: return Compression.CompressString(obj)
		elif objType == Type.Integer: return Compression.CompressInteger(obj)
		elif objType == Type.Boolean: return Compression.CompressBoolean(obj)
		elif objType == Type.EmptyList: return bytes([0])
		elif objType == Type.IntegerList: return Compression.CompressIntegerList(obj)
		elif objType == Type.BooleanList: return Compression.CompressBooleanList(obj)

	@staticmethod
	def Decompress(obj: bytes, objType: Type):
		if type(obj) != bytes or type(objType) != Type: return None

		if objType == Type.String: return Compression.DecompressString(obj)
		elif objType == Type.Integer: return Compression.DecompressInteger(obj)
		elif objType == Type.Boolean: return Compression.DecompressBoolean(obj)
		elif objType == Type.EmptyList: return []
		elif objType == Type.IntegerList: return Compression.DecompressIntegerList(obj)
		elif objType == Type.BooleanList: return Compression.DecompressBooleanList(obj)

	@staticmethod
	def CompressString(obj: str):
		if type(obj) != str: return None
		compressed = zlib.compress(obj.encode("utf-8"), 9)

		if sys.getsizeof(obj) < sys.getsizeof(compressed): return None
		return compressed

	@staticmethod
	def DecompressString(obj: bytes):
		if type(obj) != bytes: return None
		decompressed = zlib.decompress(obj).decode("utf-8", "backslashreplace")

		return decompressed

	@staticmethod
	def CompressInteger(obj: int):
		if type(obj) != int: return None
		positive = obj >= 0
		obj = abs(obj)
		output = []
		while obj > 0:
			output.append(obj % 256)
			obj = obj // 256
		output.append(positive)

		return bytes(output[::-1])

	@staticmethod
	def DecompressInteger(obj: bytes):
		if type(obj) != bytes: return None
		output = 0
		count = len(obj) - 2

		for value in obj[1:]:
			output += value * 256 ** count
			count -= 1

		if not obj[0]: output *= -1
		return output

	@staticmethod
	def CompressBoolean(obj: bool):
		if type(obj) != bool: return None
		return bytes([1]) if obj else bytes([0])

	@staticmethod
	def DecompressBoolean(obj: bytes):
		if type(obj) != bytes: return None
		return obj[0] == 1

	@staticmethod
	def CompressIntegerList(obj: list):
		if Type.GetObjectType(obj) not in (Type.IntegerList, Type.EmptyList): return None
		output = [len(obj)]
		
		for item in obj:
			compressed = Compression.CompressInteger(item)
			output.append(len(compressed))
			for byte in compressed:
				output.append(byte)

		return bytes(output)

	@staticmethod
	def DecompressIntegerList(obj: bytes):
		if type(obj) != bytes: return None

		length = obj[0]
		output = []

		index = 1
		objLength = len(obj)
		while index < objLength and len(output) < length:
			intLength = obj[index]
			if intLength == 0: return None
			index += 1

			gottenInteger = Compression.DecompressInteger(obj[index:index + intLength])
			output.append(gottenInteger)
			index += intLength

		return output

	@staticmethod
	def CompressBooleanList(obj: list):
		if Type.GetObjectType(obj) not in (Type.BooleanList, Type.EmptyList): return None
		output = [len(obj)]

		chunk = 0
		added = 0
		for item in obj:
			value = 1 if item else 0
			chunk <<= 1
			chunk |= value
			added += 1
			if added >= 8:
				output.append(chunk)
				chunk = 0
				added = 0

		if added > 0:
			chunk <<= 8 - added
			output.append(chunk)

		return bytes(output)

	@staticmethod
	def DecompressBooleanList(obj: bytes):
		if type(obj) != bytes: return None

		length = obj[0]
		output = []

		index = 1
		while index < length / 8 + 1 and len(output) < length:
			data = obj[index]
			read = min(length - (index - 1) * 8, 8)
			if read < 8: data >>= 8 - read
			falses = read - len(format(data, "b")) + (1 if not data else 0)

			for i in range(falses): output.append(False)
			tmp = []

			while data > 0:
				tmp.append(data & 1 == 1)
				data >>= 1

			for item in tmp[::-1]: output.append(item)

			index += 1

		return output

class Field:

	def __init__(self, title: str, acceptedType: Type):
		self.title = title
		self.acceptedType = acceptedType

class Table:

	@staticmethod
	def FromFile(file = None):
		if file is None: return None

		try:
			title, fieldsCount, entriesCount = Compression.DecompressString(shared.Util.FromBase64Bytes(\
				shared.Util.ReadLine(file))).split(" ")
			title = shared.Util.FromBase64String(title)
			fieldsCount, entriesCount = (int(fieldsCount), int(entriesCount))
			fields = []
			entries = []

			for i in range(fieldsCount):
				fieldTitle, fieldType = Compression.DecompressString(shared.Util.FromBase64Bytes(\
					shared.Util.ReadLine(file))).split(" ")
				fieldTitle = shared.Util.FromBase64String(fieldTitle)
				fieldType = Type(int(fieldType))
				fields.append(Field(fieldTitle, fieldType))

			for i in range(entriesCount):
				entry = shared.Util.FromBase64Bytes(shared.Util.ReadLine(file)).split(b" ")
				for j in range(len(entry)):
					item = Compression.Decompress(entry[j], fields[j].acceptedType)

					if item is None:
						raise ValueError(f"Entry {i + 1}, Item {j + 1} could be decompressed into type {fields[j].acceptedType.name}")

					entry[j] = item

				entries.append(entry)

			if fieldsCount != len(fields) or entriesCount != len(entries): return None
			table = Table(title, fields)
			table.entries = entries

			return table
		except IOError:
			return None
		except Exception as e:
			print("An error was thrown while trying to read a Table from a file")
			raise e

	def __init__(self, title: str, fields: list):
		self.title = title
		self.fields = fields
		self.entries = []

	def getField(self, fieldTitle: str):
		if type(fieldTitle) != str: return None

		index = 0
		for field in self.fields:
			if field.title == fieldTitle: return (index, field)
			index += 1

		return None

	def addEntry(self, entry: list):
		if type(entry) != list: return False
		if len(entry) != len(self.fields): return False

		for i in range(len(self.fields)):
			if (tmp := Type.GetObjectType(entry[i])) != self.fields[i].acceptedType:
				if tmp == Type.EmptyList and self.fields[i].acceptedType in (Type.IntegerList, Type.Boolean):
					continue
				return False

		self.entries.append(entry)

	def searchEntriesByField(self, field: str, obj: object, limit: int = -1):
		field = self.getField(field)

		if field is None: return (-1,)
		if Type.GetObjectType(obj) != field[1].acceptedType: return (-1,)
		found = 0
		entries = []

		index = 0
		for entry in self.entries:
			try:
				if limit >= 0 and found >= limit:
					break

				if entry[field[0]] == obj:
					entries.append([index] + entry)
					found += 1

				index += 1
			except IndexError:
				return (-1,)

		return tuple([found] + entries)

	def searchEntriesByFieldComparable(self, field: str, comparable = None, limit: int = -1):
		field = self.getField(field)

		if field is None: return (-1,)
		found = 0
		entries = []
		index = 0

		for entry in self.entries:
			try:
				if limit >= 0 and found >= limit:
					break

				if comparable(entry[field[0]]):
					entries.append([index] + entry)
					found += 1

				index += 1
			except IndexError:
				return (-1,)

		return tuple([found] + entries)

	def removeEntry(self, index: int):
		if type(index) != int or index < 0 or index > len(self.entries): return False
		initCount = len(self.entries)
		del self.entries[index]
		if len(self.entries) == initCount - 1: return True
		return False

	def removeEntries(self, indexes: list):
		if type(indexes) not in (tuple, list): return False
		
		for index in indexes:
			if type(index) != int or index < 0: return False

		initCount = len(self.entries)
		for index in sorted(indexes, reverse = True):
			del self.entries[index]

		if len(self.entries) == initCount - len(indexes): return True
		return False

	def save(self, file = None):
		if file is None: return False

		# Table has entires but no fields?
		if not len(self.fields) and len(self.entries) > 0: return False

		file.write(shared.Util.ToBase64Bytes(Compression.Compress(\
			shared.Util.ToBase64String(self.title) + f" {len(self.fields)} {len(self.entries)}")))

		for field in self.fields:
			file.write(b"\n")
			file.write(shared.Util.ToBase64Bytes(Compression.Compress(\
				shared.Util.ToBase64String(field.title) + f" {field.acceptedType.value}")))

		for entry in self.entries:
			file.write(b"\n")
			line = bytearray()

			for i in range(len(entry)):
				compressed = Compression.Compress(entry[i])
				if compressed is None:
					raise ValueError(f"Couldn't compress a \"{type(entry[i]).__name__}\" object")

				for byte in compressed:
					line.append(byte)

				if i != len(entry) - 1:
					line.append(b" "[0])

			file.write(shared.Util.ToBase64Bytes(line))

class Database:

	@staticmethod
	def FromFile(file = None):
		if file is None: return None

		try:
			title, tableCount = Compression.DecompressString(shared.Util.FromBase64Bytes(\
				shared.Util.ReadLine(file))).split(" ")
			title = shared.Util.FromBase64String(title)
			tableCount = int(tableCount)
			tables = []

			for i in range(tableCount):
				table = Table.FromFile(file)

				if table is None: return None
				tables.append(table)

			if len(tables) == tableCount:
				return Database(title, tables)
		except EOFError:
			return None
		except Exception as e:
			print("An error was thrown while trying to read a Database from a file")
			raise e

	def __init__(self, title: str, tables: list):
		self.title = title
		self.tables = tables

	def getTable(self, tableTitle: str):
		if tableTitle is None or type(tableTitle) != str: return None

		for table in self.tables:
			if table.title == tableTitle: return table

		return None

	def save(self, file = None):
		if file is None:
			file = open(f"{self.title}.db", "wb")

		file.write(shared.Util.ToBase64Bytes(Compression.Compress(\
			shared.Util.ToBase64String(self.title) + f" {len(self.tables)}")))

		for table in self.tables:
			file.write(b"\n")
			table.save(file)
