from enum import Enum
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Hash import SHA1
from Crypto.Random import random as Random
import socket, threading, inspect, shared, cryptography

class IOType:

	Unset = 0
	Server = 1
	Client = 2

class BaseIO:

	def __init__(self, ip: str, port: int):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.address = (ip, port)
		self.type = IOType.Unset
		self.dying = False

	def asServer(self):
		if self.type == IOType.Unset:
			self.socket.bind(self.address)
			self.socket.listen(32)
			self.type = IOType.Server

		return self

	def asClient(self):
		if self.type == IOType.Unset:
			self.socket.connect(self.address)
			self.type = IOType.Client

		return self

	def close(self):
		self.dying = True

		if self.socket is not None:
			self.socket.close()
			self.socket = None

class Server(BaseIO):

	def __init__(self, ip: str, port: int, handle = None, timeout: int = .5):
		if not hasattr(handle, "__call__"):
			raise ValueError("handle isn't callable")

		if len(inspect.signature(handle).parameters) < 2:
			raise ValueError("handle's signature wasn't at least 2 parameters")

		super().__init__(ip, port)
		self.socket.settimeout(timeout)
		self.threads = []
		self.handle = handle
		self.asServer()
		self.thread = threading.Thread(target = self.internalGet, daemon = True)
		self.thread.start()

	def internalGet(self):
		if self.socket is None: return

		while not self.dying:
			self.checkDeathThreads()
			try:
				client, addr = self.socket.accept()
				thread = threading.Thread(target = self.handle, args = (client, addr), daemon = True)
				self.threads.append(thread)
				thread.start()
			except socket.timeout: pass
			except OSError as e:
				if self.dying: return
				else: raise e

	def checkDeathThreads(self):
		for i in range(len(self.threads))[::-1]:
			thread = self.threads[i]
			if not thread.is_alive():
				del self.threads[i]

	def close(self):
		super().close()

		if self.thread is not None:
			self.thread.join()
			self.thread = None

		for thread in self.threads:
			thread.join()
		self.threads = tuple()

class SplitServer(Server):

	def __init__(self, ip: str, port: int, handle = None, timeout: int = .5):
		if not hasattr(handle, "__call__"):
			raise ValueError("handle isn't callable")

		if len(inspect.signature(handle).parameters) < 2:
			raise ValueError("handle's signature wasn't at least 2 parameters")

		super().__init__(ip, port, self.internalHandle, timeout)
		self.simpleHandle = handle
		self.timeout = timeout

	def internalHandle(self, connection: socket.socket, address: tuple):
		if self.socket is None: return
		connection.settimeout(self.timeout)

		while not self.dying:
			try:
				data = connection.recv(3)
				if not len(data): break
				if len(data) < 3 or data[2] != 10: continue
				data = connection.recv(data[0] * 256 + data[1])
				timer = shared.Timer()
				ret = self.simpleHandle(connection, data)
				took = timer.stop()
				if took > 3: print(f"Time warning, call to handle took {took} seconds")

				if type(ret) is bool and ret:
					connection.close()
					break
			except socket.timeout: pass
			except ConnectionError: return

	def reply(self, connection: socket.socket, data: bytes):
		if connection is None: return

		if type(data) == bytes:
			dataLength = len(data)
			if dataLength > 65535:
				self.close()
				raise ValueError("Tried to send more than 65535 bytes")
			connection.sendall(bytes([dataLength // 256, dataLength % 256, 10]) + data)
		else: raise ValueError("Tried to send non-bytes object")

class Client(BaseIO):

	def __init__(self, ip: str, port: int, handle = None):
		if not hasattr(handle, "__call__"):
			raise ValueError("handle isn't callable")

		if len(inspect.signature(handle).parameters) < 1:
			raise ValueError("handle's signature wasnt' at least 1 parameter")

		super().__init__(ip, port)
		self.socket.settimeout(.5)
		self.handle = handle
		self.asClient()
		self.thread = threading.Thread(target = self.internalGet, daemon = True)
		self.thread.start()

	def internalGet(self):
		if self.socket is None: return

		while not self.dying:
			try:
				data = self.socket.recv(3)
				if not len(data): break
				if len(data) < 3 or data[2] != 10: continue
				data = self.socket.recv(data[0] * 256 + data[1])
				if type(data) is bytes:
					timer = shared.Timer()
					ret = self.handle(data)
					took = timer.stop()
					if took > 3: print(f"Time warning, call to handle took {took} seconds")

					if type(ret) is bool and ret:
						self.socket.close()
						self.socket = None
						break
			except socket.timeout: pass
			except ConnectionError: return

	def send(self, data: bytes):
		if self.socket is None: return

		if type(data) == bytes:
			dataLength = len(data)
			if dataLength > 65535: return
			self.socket.sendall(bytes([dataLength // 256, dataLength % 256, 10]) + data)
		else: raise ValueError("Tried to send non-bytes object")

	def close(self):
		super().close()
		if self.thread is not None:
			self.thread.join()
			self.thread = None

class Packet:

	@staticmethod
	def FromBytes(data: bytes, key: RsaKey = None):
		if type(data) not in (bytes, bytearray): return 0 # Bytes weren't given

		lines = data.split(b"\n")
		if len(lines) < 4: return 1 # Data is too short to actually be a packet
		version, code, body = (None,) * 3
		headers = {}

		try:
			tmpSplit = lines[0].split(b" ")
			version, code = (tmpSplit[0].split(b"/")[1].decode("utf-8"), tmpSplit[1].decode("utf-8"))
		except IndexError: return 2 # Unable to get packet header info

		offset = 1
		while (line := lines[(offset := offset + 1)]) != b"":
			tmpSplit = line.split(b" ")
			if len(tmpSplit) < 2: return 3 # Malformed header
			try:
				_key = tmpSplit[0].decode("utf-8")
				value = b" ".join(tmpSplit[1:]).decode("utf-8")
				headers[_key] = value
			except UnicodeDecodeError: return 4 # Failed to decode strings

		if offset + 1 < len(lines):
			body = b"\n".join(lines[offset + 1:])

		if "Encrypted" in headers and headers["Encrypted"] == "true":
			if type(key) != RsaKey: return 5 # Missing key when required
			else:
				decrypted = cryptography.RSA.DecryptMessage(key, shared.Util.FromBase64Bytes(headers["Random"]))
				headers["Random"] = decrypted.decode("utf-8")

				if body is not None:
					if body.count(b"\n") > 0:
						output = bytearray()
						for part in body.split(b"\n"):
							decrypted = cryptography.RSA.DecryptMessage(key, shared.Util.FromBase64Bytes(part))
							if type(decrypted) is bytes: output += decrypted
							else: return 6 # Unable to decrypt a line of the body

						body = bytes(output)
					else:
						decrypted = cryptography.RSA.DecryptMessage(key, shared.Util.FromBase64Bytes(body))
						if type(decrypted) == bytes: body = decrypted
						else: return 7 # Unable to decrypt the body
		elif body is not None:
			body = shared.Util.FromBase64Bytes(body)

		if body is not None:
			try:
				bodyLength = int(headers["Length"])
				bodyChecksum = headers["Checksum"]

				if bodyLength != len(body): return 10 # Body length and length header didn't match
				if bodyChecksum != Checksum(body): return 11 # Body checksum and checksum header didn't match
			except KeyError:
				return 8 # Missing required headers
			except ValueError:
				return 9 # Length header value couldn't be casted to an integer

		return Packet(version, code, headers, body)

	def __init__(self, version: str, code: str, headers: dict, body: bytes):
		self.version = version
		self.code = code
		self.headers = headers
		self.body = body

	def toBytes(self, random: str = None, key: RsaKey = None):
		if not len(self.version):
			raise ValueError("Packet is missing version information")
		if not len(self.code):
			raise ValueError("Packet is missing code information")

		hasKey = type(key) == RsaKey and key.can_encrypt()

		output = bytearray(0)

		if type(self.code) != str or len(self.code) != 2:
			self.code = "41"

		output += f"Boards/{self.version} {self.code}\n".encode("utf-8")

		def _cleanChar(c):
			if c.isalnum(): return c
			elif c.isspace() and not "\n\r".count(c): return "-"
			return ""

		hasBody = type(self.body) in (bytes, bytearray) and len(self.body) > 0

		# Prevent replay attacks
		if type(random) != str or len(random) != 30:
			if type(random) == bool and random and type(self.headers["Random"]) == str and len(self.headers["Random"]) == 30:
				random = self.headers["Random"]
			else:
				random = str(Random.randint(int("1" + "0" * 29), int("9" * 30)))

		if hasBody:
			# SHA256 or SHA512 could be used but a simple SHA1 checksum should be fine
			self.headers["Checksum"] = Checksum(self.body)
			self.headers["Length"] = str(len(self.body))

		headers = dict(self.headers)
		self.headers["Random"] = random

		if hasKey:
			self.headers["Encrypted"] = "true"
			headers["Encrypted"] = "true"
			encrypted = cryptography.RSA.EncryptMessage(key, random.encode("utf-8"))
			if type(encrypted) == bytes:
				headers["Random"] = shared.Util.ToBase64String(encrypted)
			else: return None
		else:
			self.headers["Encrypted"] = "false"
			headers["Encrypted"] = "false"
			headers["Random"] = random

		for _key, value in headers.items():
			if type(_key) is str and type(value) is str:
				_key = "".join([_cleanChar(c) for c in _key])
				output += f"\n{_key} {value}".encode("utf-8")

		if hasBody:
			output += b"\n"
			if hasKey:
				encrypted = cryptography.RSA.EncryptMessage(key, self.body)
				if type(encrypted) == bytes:
					output += b"\n"
					output += shared.Util.ToBase64Bytes(encrypted)
				elif type(encrypted) in (list, tuple):
					for part in encrypted:
						output += b"\n"
						output += shared.Util.ToBase64Bytes(part)
			else:
				output += b"\n"
				output += shared.Util.ToBase64Bytes(self.body)

		return bytes(output)

def Checksum(data: bytes):
	return SHA1.new(data).digest().hex()