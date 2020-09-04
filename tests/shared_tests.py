import sys
sys.path.append("../src/")
import shared as sh

def test(doPrints: bool = False):

	# Pool checks

	pool1 = sh.Pool()
	pool2 = sh.Pool()

	assert len(sh.Pool.__pools__) == 2, "Pools failed check 1"

	obj1 = "Test"
	obj2 = "Test 2"

	ref1 = pool1.add(obj1)
	ref2 = pool1.add(obj2)

	assert pool1.get(ref1) is obj1, "Pool get check 1 failed"
	assert pool1.get(ref2) is obj2, "Pool get check 2 failed"

	# Bad! Should never do!
	obj3 = 27
	ref3 = sh.Reference(pool1.id.index, len(pool1._data))
	pool1._data.append((ref3, obj3))

	assert pool1.get(ref3) is obj3, "Pool get check 3 failed"

	response1 = pool1.verify()
	pool1.purge()
	response2 = pool1.verify()

	assert not response1, "Pool 1 failed to detect a forcefully added int"
	assert response2, "Pool 1 failed to purge a forcefully added int"
	assert len(pool1._data) == 2, "Pool 1 failed to purge a forcefully added int"

	pool1.destroy()

	assert pool2.id.index == 0, "Pool 1's destruction didn't update indexes of other pools"

	ref4 = pool2.add(25)
	ref5 = pool2.add(78)
	ref6 = pool2.add(67)

	pool2.remove(ref4)

	assert len(pool2._data) == 2, "Pool 2 failed to remove an object"

	try:
		pool2.add("This should raise an error")

		print("Pool 2 failed to detect a non-int type being added")
		return
	except ValueError:
		pass

	pool2.destroy()

	assert len(sh.Pool.__pools__) == 0, "Pools failed check 4"
	del pool1, pool2, ref1, ref2, ref3, obj1, obj2, obj3, response1, response2, ref4, ref5, ref6

	print("Passed Pool Checks")

if __name__ == "__main__":
	from sys import argv
	test(len(argv) > 1)