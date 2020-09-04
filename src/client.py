import communication, time

class _Client:

	def __init__(self):
		self.client = communication.Client("localhost", 27500, self._incomingData)
		self.client.send(b"REEEEEEEEEEE")

	def _incomingData(self, data: bytes):
		print("Got", data, "from the server")
		time.sleep(3)
		self.client.send(b"REEEEEE")

def init():
	client = _Client()
	client.client.thread.join()

if __name__ == "__main__":
	print("This file shouldn't be ran directly")