# PPS w/ SHA256 or SHA512

from Crypto.Signature import pss
from Crypto.PublicKey import RSA as _RSA
from Crypto.Cipher import PKCS1_OAEP as _PKCS
from Crypto.Util.number import size, ceil_div
from Crypto.Hash import SHA512

class RSA:

	@staticmethod
	def SignMessageRaw(privateKey: str, message: bytes):
		if type(privateKey) != str or type(message) != bytes: return None

		try:
			privateKey = _RSA.import_key(privateKey)
			return RSA.SignMessage(privateKey, message)

		except (TypeError, ValueError, IndexError): pass

	@staticmethod
	def SignMessage(rsaObject: _RSA.RsaKey, message: bytes):
		if type(rsaObject) != _RSA.RsaKey or type(message) != bytes: return None
		if rsaObject.can_sign() and not len(message):
			return pss.new(rsaObject).sign(SHA512.new(message))

		return None

	@staticmethod
	def VerifyMessageRaw(publicKey: str, signature: bytes, message: bytes):
		if type(publicKey) != str or type(signature) != bytes or type(message) != bytes: return False

		try:
			publicKey = _RSA.import_key(publicKey)
			return RSA.VerifyMessage(publicKey, signature, message)

		except (TypeError, ValueError, IndexError): pass

	@staticmethod
	def VerifyMessage(rsaObject: _RSA.RsaKey, signature: bytes, message: bytes):
		if type(rsaObject) != _RSA.RsaKey or type(signature) != bytes or type(message) != bytes: return False

		checker = pss.new(rsaObject)

		try:
			checker.verify(SHA512.new(message), signature)
			return True
		except (ValueError, TypeError):
			return False

	@staticmethod
	def EncryptMessageRaw(publicKey: str, message: bytes):
		if type(publicKey) != str or type(message) != bytes: return None

		try:
			publicKey = _RSA.import_key(publicKey)
			return RSA.EncryptMessage(publicKey, message)

		except (TypeError, ValueError, IndexError): pass

	@staticmethod
	def EncryptMessage(rsaObject: _RSA.RsaKey, message: bytes):
		if type(rsaObject) != _RSA.RsaKey or type(message) != bytes: return None

		if rsaObject.can_encrypt() and len(message):
			pkcs = _PKCS.new(rsaObject, SHA512)
			maxLength = int(size(pkcs._key.n) / 8) - 2 * pkcs._hashObj.digest_size - 2

			if len(message) > maxLength:
				output = []
				index = 0
				stop = (len(message) // maxLength) + (1 if (len(message) % maxLength) > 0 else 0)
				while index < stop:
					encrypted = RSA.EncryptMessage(rsaObject, message[index * maxLength:(index + 1) * maxLength])
					output.append(encrypted)
					index += 1

				return tuple(output)
			else:
				return pkcs.encrypt(message)

	@staticmethod
	def DecryptMessageRaw(privateKey: str, message: bytes):
		if type(privateKey) != str or type(message) != bytes: return None

		try:
			privateKey = _RSA.import_key(privateKey)
			return RSA.DecryptMessage(privateKey, message)

		except (TypeError, ValueError, IndexError): return -3

	@staticmethod
	def DecryptMessage(rsaObject: _RSA.RsaKey, message: bytes):
		if type(rsaObject) != _RSA.RsaKey or type(message) != bytes: return None

		if rsaObject.can_encrypt() and len(message):
			pkcs = _PKCS.new(rsaObject, SHA512)
			try: return pkcs.decrypt(message)
			except ValueError: return -1
			except TypeError: return -2

	@staticmethod
	def ExportKeys(rsaObject: _RSA.RsaKey):
		if type(rsaObject) != _RSA.RsaKey: return None

		ret = [1, RSA._StripKeyDetail(rsaObject.publickey().export_key().decode("utf-8")), None]
		if rsaObject.has_private(): ret[:1] = (2, RSA._StripKeyDetail(rsaObject.export_key().decode("utf-8")))
		return tuple(ret)

	@staticmethod
	def ImportKeys(key: str):
		if type(key) != str: return None

		try:
			return _RSA.import_key(key)
		except (TypeError, ValueError, IndexError):
			return None

	@staticmethod
	def _StripKeyDetail(key: str):
		if type(key) != str or len(key.split("\n")) < 3: return None
		return "".join(key.split("\n")[1:-1])

	@staticmethod
	def _AddKeyDetail(key: str, pubKey: bool = True):
		if type(key) != str or type(pubKey) is not bool: return None
		keyType = ("PUBLIC" if pubKey else "PRIVATE") + " KEY-----"
		return f"-----BEGIN {keyType}\n{key}\n-----END {keyType}"

	@staticmethod
	def GenerateKey():
		return _RSA.generate(4096)