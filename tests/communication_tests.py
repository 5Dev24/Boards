import sys
sys.path.append("../src/")
import communication as com, cryptography as cr
from Crypto.PublicKey import RSA

def test(doPrints: bool = False):
	# Simple socket tests

	server_got = []
	client_got = []

	def server_handle(connection, data):
		data = int(data.decode("utf-8"))
		server_got.append(data)
		server.reply(connection, str(data + 1).encode("utf-8"))
		if data >= 5: return True

	def client_handle(data):
		data = int(data.decode("utf-8"))
		client_got.append(data)
		client.send(str(data + 1).encode("utf-8"))
		if data >= 5: return True

	server = com.SplitServer("localhost", 27500, server_handle)
	client = com.Client("localhost", 27500, client_handle)
	client.send("1".encode("utf-8"))

	client.thread.join()

	server.close()
	client.close()

	flag1 = server_got == [1, 3, 5]
	flag2 = client_got == [2, 4, 6]

	if doPrints:
		print("Server got:", server_got)
		print("Client got:", client_got)

	assert flag1 or flag2, "Both the server and client didn't recieve all data"
	assert flag1, "Server didn't receive all client data"
	assert flag2, "Client didn't receive all server data"

	del server, client, server_got, client_got, flag1, flag2, server_handle, client_handle

	print("Passed basic communications tests")



	# Packet tests

	packet = com.Packet("1.0.0", "00", {}, bytes([1, 0, 2, 3, 5, 4, 6, 8, 7]))
	packetBytes = packet.toBytes()
	if doPrints: print("Unencrypted Packet as bytes:", packetBytes)

	packetRebuilt = com.Packet.FromBytes(packetBytes)

	assert type(packetRebuilt) == com.Packet, f"Unable to rebuilt packet from bytes ({packetRebuilt})"

	# Feeding back in random from headers so that it doesn't generate a new random
	packetRebuiltBytes = packetRebuilt.toBytes(packetRebuilt.headers["Random"])
	if doPrints: print("Unencrypted Packet Rebuilt as bytes:", packetRebuiltBytes)

	assert packetBytes == packetRebuiltBytes, "Unencrypted packet's bytes didn't match"
	del packet, packetBytes, packetRebuilt, packetRebuiltBytes

	print("Passed unencrypted packet tests")

	rsaPrivateKey = "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\
EzfLzeLQCQ3raBnfPI+mcUzCPpZE0CfxJjYen/w=="

	key = cr.RSA.ImportKeys(cr.RSA._AddKeyDetail(rsaPrivateKey))

	data = bytes([6, 2, 5, 1, 0, 7, 8, 3, 4])
	packet = com.Packet("1.0.0", "00", {}, data)
	packetBytes = packet.toBytes(key = key)

	if doPrints: print("Encrypted Packet as bytes:", packetBytes)

	packetRebuilt = com.Packet.FromBytes(packetBytes, key)

	assert type(packetRebuilt) == com.Packet, f"Unable to rebuilt packet from bytes ({packetRebuilt})"

	# Feeding back in random from headers so that it doesn't generate a new random
	packetRebuiltBytes = packetRebuilt.toBytes(True, key)
	if doPrints: print("Encrypted Packet Rebuilt as bytes:", packetRebuiltBytes)

	assert packet.version == packetRebuilt.version and packet.code == packetRebuilt.code and packet.headers == packetRebuilt.headers and packet.body == packetRebuilt.body and data == packetRebuilt.body, "Encrypted packet's bytes didn't match"
	del packet, packetBytes, packetRebuilt, packetRebuiltBytes, data

	print("Passed encrypted packet tests")

	data = bytes([2, 1, 8, 3, 7, 6, 4, 5, 0] * 1000)
	packet = com.Packet("1.0.0", "00", {}, data)
	packetBytes = packet.toBytes(key = key)

	if doPrints: print("Long Encrypted Packet as bytes:", packetBytes)

	packetRebuilt = com.Packet.FromBytes(packetBytes, key)

	assert type(packetRebuilt) == com.Packet, f"Unable to rebuilt packet from bytes ({packetRebuilt})"

	# Feeding back in random from headers so that it doesn't generate a new random
	packetRebuiltBytes = packetRebuilt.toBytes(True, key)
	if doPrints: print("Long Encrypted Packet Rebuilt as bytes:", packetRebuiltBytes)

	assert packet.version == packetRebuilt.version and packet.code == packetRebuilt.code and packet.headers == packetRebuilt.headers and packet.body == packetRebuilt.body and data == packetRebuilt.body, "Long encrypted packet's bytes didn't match"
	del packet, packetBytes, packetRebuilt, packetRebuiltBytes, data, rsaPrivateKey, key

	print("Passed long encrypted packet tests")

if __name__ == "__main__":
	from sys import argv
	test(len(argv) > 1)