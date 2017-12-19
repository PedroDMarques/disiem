import json

class BulkIterator:
	def __init__(self, fh, indexName):
		self.fh = fh
		self.indexName = indexName

	def __iter__(self):
		return self

	def next(self):
		return {
			"_op_type": "index",
			"_index": self.indexName,
			"_type": "document",
			"_source": json.loads(self.fh.readline()),
		}