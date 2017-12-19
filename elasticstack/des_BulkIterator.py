import json

class BulkIterator:
	def __init__(self, fh, indexName):
		self.fh = fh
		self.indexName = indexName

	def __iter__(self):
		return self

	def next(self):
		line = self.fh.readline()

		if not line:
			raise StopIteration()

		else:
			return {
				"_op_type": "index",
				"_index": self.indexName,
				"_type": "disiem",
				"_source": json.loads(line),
			}