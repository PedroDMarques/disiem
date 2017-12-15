import json

CREATE_INDEX = json.dumps({
	"mappings": {
		"disiem": {
			"properties": {
				"username": {
					"type": "keyword",
				},
				"syslog_severity_code": {
					"type": "integer",
				},
			}
		},
	}
})