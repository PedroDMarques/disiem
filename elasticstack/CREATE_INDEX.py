import json

CREATE_INDEX = json.dumps({
	"mappings": {
		"disiem": {
			"numeric_detection": True,

			"properties": {
				"username": {
					"type": "keyword"
				}
			}
		},
	}
})