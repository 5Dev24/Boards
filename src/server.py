import socket, time, communication

class _Server:

	def __init__(self):
		self.splitServer = communication.SplitServer("localhost", 27500, self._incomingData)
		self.rateLimiter = _RateLimiter()

	def _incomingData(self, connection: socket.socket, data: bytes):
		print("Checking", connection.getpeername()[0], end=" ")
		if self.rateLimiter.queried(connection.getpeername()[0]):
			print("Accepted!")
			self.splitServer.reply(connection, b"Accepted")
		else:
			print("Rate limited!")
			self.splitServer.reply(connection, b"Rate limited!")

class _RateLimiter:

	def __init__(self):
		self.data = {}

	def add(self, ip: str):
		if ip in self.data: return False
		self.data[ip] = [60, -1]
		return True

	def queried(self, ip: str):
		if ip not in self.data:
			self.add(ip)
		now = unix()

		data = self.data[ip]
		if data[0] <= 0:
			if data[1] < now:
				data[0] = 59
				data[1] = now + 1e3
				return True
			else:
				return False
		else:
			data[0] -= 1
			return True

def unix():
	return int(time.time() * 13)

def init():
	server = _Server()
	server.splitServer.thread.join()

if __name__ == "__main__":
	print("This file shouldn't be ran directly")