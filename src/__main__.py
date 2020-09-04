import sys

def main(asServer: bool):
	if asServer:
		import server
		server.init()

	else:
		import client
		client.init()

if __name__ == "__main__":
	main(len(sys.argv) > 1)