import sys
sys.path.append("../src/")
import database as db

def test(doPrints: bool = False):
	# String test

	shortString = "A short string"
	longString = """This is a longer string to test that a string
can be compressed and decompressed and you'll
get back the same data that you put in"""

	compressedShortString = db.Util.CompressString(shortString)
	compressedLongString = db.Util.CompressString(longString)

	uncompressedShortString = db.Util.DecompressString(compressedShortString)
	uncompressedLongString = db.Util.DecompressString(compressedLongString)

	if doPrints:
		print("Short String\nInit\n", shortString, "\n\nCompressed\n", compressedShortString, "\n\nUncompressed\n", uncompressedShortString, sep="")
		print("\n\nLong String\nInit\n", longString, "\n\nCompressed\n", compressedLongString, "\n\nUncompressed\n", uncompressedLongString, sep="")

	assert shortString == uncompressedShortString, "Short strings didn't match"
	assert longString == uncompressedLongString, "Long strings didn't match"
	del shortString, longString, compressedShortString, compressedLongString, uncompressedShortString, uncompressedLongString

	print("Passed Strings Tests")



	# Integer test

	positiveShortInteger = 724
	negativeShortInteger = -519
	positiveLongInteger = 97237098238709148709439807134708961370986134097861340987613709846018793
	negativeLongInteger = -83289548705209315290513907623860894620879608791347098431098743208791340

	compressedPositiveShortInteger = db.Util.CompressInteger(positiveShortInteger)
	compressedNegativeShortInteger = db.Util.CompressInteger(negativeShortInteger)
	compressedPositiveLongInteger = db.Util.CompressInteger(positiveLongInteger)
	compressedNegativeLongInteger = db.Util.CompressInteger(negativeLongInteger)

	uncompressedPositiveShortInteger = db.Util.DecompressInteger(compressedPositiveShortInteger)
	uncompressedNegativeShortInteger = db.Util.DecompressInteger(compressedNegativeShortInteger)
	uncompressedPositiveLongInteger = db.Util.DecompressInteger(compressedPositiveLongInteger)
	uncompressedNegativeLongInteger = db.Util.DecompressInteger(compressedNegativeLongInteger)

	if doPrints:
		print("\n\nPositive Short Integer\nInit\n", positiveShortInteger, "\n\nCompressed\n", compressedPositiveShortInteger, "\n\nUncompressed\n", uncompressedPositiveShortInteger, sep="")
		print("\n\nNegative Short Integer\nInit\n", negativeShortInteger, "\n\nCompressed\n", compressedNegativeShortInteger, "\n\nUncompressed\n", uncompressedNegativeShortInteger, sep="")
		print("\n\nPositive Long Integer\nInit\n", positiveLongInteger, "\n\nCompressed\n", compressedPositiveLongInteger, "\n\nUncompressed\n", uncompressedPositiveLongInteger, sep="")
		print("\n\nNegative Long Integer\nInit\n", negativeLongInteger, "\n\nCompressed\n", compressedNegativeLongInteger, "\n\nUncompressed\n", uncompressedNegativeLongInteger, sep="")

	assert positiveShortInteger == uncompressedPositiveShortInteger, "Positive short integers didn't match"
	assert negativeShortInteger == uncompressedNegativeShortInteger, "Negative short integers didn't match"
	assert positiveLongInteger == uncompressedPositiveLongInteger, "Positive long integers didn't match"
	assert negativeLongInteger == uncompressedNegativeLongInteger, "Negative long integers didn't match"
	del positiveShortInteger, negativeShortInteger, positiveLongInteger, negativeLongInteger
	del compressedPositiveShortInteger, compressedNegativeShortInteger, compressedPositiveLongInteger, compressedNegativeLongInteger
	del uncompressedPositiveShortInteger, uncompressedNegativeShortInteger, uncompressedPositiveLongInteger, uncompressedNegativeLongInteger

	print("Passed Integer Tests")



	# Boolean tests

	true = True
	false = False

	compressedTrue = db.Util.CompressBoolean(true)
	compressedFalse = db.Util.CompressBoolean(false)

	uncompressedTrue = db.Util.DecompressBoolean(compressedTrue)
	uncompressedFalse = db.Util.DecompressBoolean(compressedFalse)

	if doPrints:
		print("\n\nTrue Boolean\nInit\n", true, "\n\nCompressed\n", compressedTrue, "\n\nUncompressed\n", uncompressedTrue, sep="")
		print("\n\nFalse Boolean\nInit\n", false, "\n\nCompressed\n", compressedFalse, "\n\nUncompressed\n", uncompressedFalse, sep="")

	assert true == uncompressedTrue, "True booleans didn't match"
	assert false == uncompressedFalse, "False booleans didn't match"
	del true, false, compressedTrue, compressedFalse, uncompressedTrue, uncompressedFalse

	print("Passed Boolean Tests")



	# Integer List tests

	emptyIntegerList = []
	shortIntegerList = [6, -2, 8, 1, -1, 78, 12, -87]
	longIntegerList = [46, 34, 23, 2, -622, 38, 192, 959, -83, 125, -90, 2591, 98, -12, 89, 87, 34, -709]

	compressedEmptyIntegerList = db.Util.CompressIntegerList(emptyIntegerList)
	compressedShortIntegerList = db.Util.CompressIntegerList(shortIntegerList)
	compressedLongIntegerList = db.Util.CompressIntegerList(longIntegerList)

	uncompressedEmptyIntegerList = db.Util.DecompressIntegerList(compressedEmptyIntegerList)
	uncompressedShortIntegerList = db.Util.DecompressIntegerList(compressedShortIntegerList)
	uncompressedLongIntegerList = db.Util.DecompressIntegerList(compressedLongIntegerList)

	if doPrints:
		print("\n\nEmpty Integer List\nInit\n", emptyIntegerList, "\n\nCompressed\n", compressedEmptyIntegerList, "\n\nUncompressed\n", uncompressedEmptyIntegerList, sep="")
		print("\n\nShort Integer List\nInit\n", shortIntegerList, "\n\nCompressed\n", compressedShortIntegerList, "\n\nUncompressed\n", uncompressedShortIntegerList, sep="")
		print("\n\nLong Integer List\nInit\n", longIntegerList, "\n\nCompressed\n", compressedLongIntegerList, "\n\nUncompressed\n", uncompressedLongIntegerList, sep="")

	assert emptyIntegerList == uncompressedEmptyIntegerList, "Empty integer lists didn't match"
	assert shortIntegerList == uncompressedShortIntegerList, "Short integer lists didn't match"
	assert longIntegerList == uncompressedLongIntegerList, "Long integer lists didn't match"
	del emptyIntegerList, shortIntegerList, longIntegerList, compressedEmptyIntegerList, compressedShortIntegerList, compressedLongIntegerList
	del uncompressedEmptyIntegerList, uncompressedShortIntegerList, uncompressedLongIntegerList

	print("Passed Integer List Tests")



	# Boolean list tests

	emptyBooleanList = []
	shortBooleanList = [True, False, False, True, False, True, True]
	longBooleanList = [False, True, False, True, True, False, False, False, False, True, True, False, False, True, False, True, False, False, True, False, False, True, False]

	compressedEmptyBooleanList = db.Util.CompressBooleanList(emptyBooleanList)
	compressedShortBooleanList = db.Util.CompressBooleanList(shortBooleanList)
	compressedLongBooleanList = db.Util.CompressBooleanList(longBooleanList)

	uncompressedEmptyBooleanList = db.Util.DecompressBooleanList(compressedEmptyBooleanList)
	uncompressedShortBooleanList = db.Util.DecompressBooleanList(compressedShortBooleanList)
	uncompressedLongBooleanList = db.Util.DecompressBooleanList(compressedLongBooleanList)

	if doPrints:
		print("\n\nEmpty Boolean List\nInit\n", emptyBooleanList, "\n\nCompressed\n", compressedEmptyBooleanList, "\n\nUncompressed\n", uncompressedEmptyBooleanList, sep="")
		print("\n\nShort Boolean List\nInit\n", shortBooleanList, "\n\nCompressed\n", compressedShortBooleanList, "\n\nUncompressed\n", uncompressedShortBooleanList, sep="")
		print("\n\nLong Boolean List\nInit\n", longBooleanList, "\n\nCompressed\n", compressedLongBooleanList, "\n\nUncompressed\n", uncompressedLongBooleanList, sep="")

	assert emptyBooleanList == uncompressedEmptyBooleanList, "Empty boolean lists didn't match"
	assert shortBooleanList == uncompressedShortBooleanList, "Short boolean lists didn't match"
	assert longBooleanList == uncompressedLongBooleanList, "Long boolean lists didn't match"
	del emptyBooleanList, shortBooleanList, longBooleanList, compressedEmptyBooleanList, compressedShortBooleanList, compressedLongBooleanList
	del uncompressedEmptyBooleanList, uncompressedShortBooleanList, uncompressedLongBooleanList

	print("Passed Boolean List Tests")



	# Table tests

	table = db.Table("Test Table", [db.Field("Author PGP", db.Type.String), db.Field("Author UUID", db.Type.String), db.Field("Author Post Count", db.Type.Integer), db.Field("Author Posts", db.Type.IntegerList)])
	table.addEntry(["Fake Author PGP 1", "Fake Author UUID 1", 12, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]])
	table.addEntry(["Fake Author PGP 2", "Fake Author UUID 2", 6, [12, 13, 14, 15, 16, 17]])
	table.addEntry(["Fake Author PGP 3", "Fake Author UUID 3", 7, [18, 19, 20, 21, 22, 23, 24]])
	table.addEntry(["Fake Author PGP 4", "Fake Author UUID 4", 0, []])

	response1 = table.searchEntriesByField("Author Post Count", 12, 1)
	response2 = table.searchEntriesByFieldComparable("Author Post Count", lambda item: item > 5)
	response3 = table.removeEntry(0)
	response4 = table.removeEntries([1, 2])

	if doPrints:
		print("Searched for 12 in the 'Author Post Count' field and found", response1[0], "matches")
		for i in range(response1[0]):
			print("Entry Index: ", response1[i + 1][0], ", Entry Data: ", response1[i + 1][1:], sep="")

		print("Serached for `> 5` in the 'Author Post Count' field and found", response2[0], "matches")
		for i in range(response2[0]):
			print("Entry Index: ", response2[i + 1][0], ", Entry Data: ", response2[i + 1][1:], sep="")

		print("Single entry remove was a " + ("success" if response3 else "failure"))
		print("Multiple entry remove was a " + ("success" if response4 else "failure"))

	assert len(response1) == 2, "Tables search failed"
	assert len(response2) == 4, "Tables search with comparable failed"
	assert response3, "Tables single entry remove failed"
	assert response4, "Tables multiple entry remove failed"
	del table, response1, response2, response3, response4

	print("Passed Table Tests")



	# Database tests

	table1 = db.Table("Test Table", [db.Field("Name", db.Type.String), db.Field("Age", db.Type.Integer), db.Field("Living", db.Type.Boolean)])
	table2 = db.Table("Test Table 2", [db.Field("Name", db.Type.String), db.Field("Student ID", db.Type.Integer)])

	table1.addEntry(["Person 1", 19, True])
	table1.addEntry(["Person 2", 32, True])
	table1.addEntry(["Person 3", 21, True])
	table1.addEntry(["Person 4", 56, True])
	table1.addEntry(["Person 5", 17, False])

	table2.addEntry(["Person 1", 123734])
	table2.addEntry(["Person 2", None])
	table2.addEntry(["Person 3", None])
	table2.addEntry(["Person 4", None])
	table2.addEntry(["Person 5", None])

	database = db.Database("Test", [table1, table2])

	if doPrints:
		print("Created database called", database.title, "with", len(database.tables), "table(s)")
		print("Table is called", database.tables[0].title)
		num = 1
		for entry in database.tables[0].entries:
			print("Entry #", num, ": ", entry, sep="")
			num += 1

	database.save()

	initialDatabaseFile = open("Test.db", "rb")
	initialDatabase = initialDatabaseFile.readlines()
	initialDatabaseFile.close()
	del initialDatabaseFile

	tmpFile = open("Test.db", "rb")
	database = db.Database.FromFile(tmpFile)
	tmpFile.close()
	del tmpFile

	if doPrints:
		print("\n\nRead a database called", database.title, "with", len(database.tables), "table(s)")
		print("Table is called", database.tables[0].title)
		num = 1
		for entry in database.tables[0].entries:
			print("Entry #", num, ": ", entry, sep="")
			num += 1

	database.save()

	finalDatabaseFile = open("Test.db", "rb")
	finalDatabase = finalDatabaseFile.readlines()
	finalDatabaseFile.close()
	del finalDatabaseFile

	assert initialDatabase == finalDatabase, "Databases didn't match"

	if not doPrints:
		import os
		os.remove(f"./{database.title}.db")
	del table1, table2, database, initialDatabase, finalDatabase

	print("Passed Database Tests")

if __name__ == "__main__":
	from sys import argv
	test(len(argv) > 1)
	#test(True)