import json

CREATE_INDEX = json.dumps({
	"mappings": {
		"disiem": {
			"properties": {

				# General
				# -------
				"timestamp": { "type": "date" },
				
				"des_software_type": { "type": "keyword" },
				"des_device_name": { "type": "keyword" },
				
				"des_total_bytes": { "type": "integer" },
				"des_src_bytes": { "type": "integer" },
				"des_dst_bytes": { "type": "integer" },
				
				"src_ip": { "type": "ip" },
				"dst_ip": { "type": "ip" },
				
				"src_port": { "type": "integer" },
				"dst_port": { "type": "integer" },

				"ip_pair": { "type": "keyword" },
				"port_pair": { "type": "keyword" },
				"ip_port_pair": { "type": "keyword" },
				"protocol": { "type": "keyword" },

				# Bro fields
				# ----------
				"sub": { "type": "text" },
				"suppress_for": { "type": "float" },
				"peer_desc": { "type": "keyword" },
				"actions": { "type": "keyword" },
				"signature": { "type": "keyword" },
				"flow_id": { "type": "keyword" },
				"msg": { "type": "text" },

				# Ciscoasa
				# --------
				"dst_interface": { "type": "keyword" },
				"timezone": { "type": "keyword" },
				"syslog_severity_code": { "type": "integer" },
				"log_level": { "type": "integer" },
				"hashcode1": { "type": "keyword" },
				"hashcode2": { "type": "keyword" },
				"message_id": { "type": "keyword" },
				"ciscotag": { "type": "keyword" },
				"syslog_severity": { "type": "keyword" },
				"sysloghost": { "type": "keyword" },
				"src_interface": { "type": "keyword" },
				"interval": { "type": "keyword" },
				"hit_count": { "type": "integer" },
				"action": { "type": "keyword" },
				"policy_id": { "type": "keyword" },

				# Ciscovpn
				# --------
				"group": { "type": "keyword" },
				"message_id": { "type": "integer" },
				"username": { "type": "keyword" },
				"des_session_duration": { "type": "integer" },
				"session_type": { "type": "keyword" },
				"reason": { "type": "keyword" },
				
				# Pan
				# ---
				"ActionSource": { "type": "keyword" },
				"EgressInterface": { "type": "keyword" },
				"SourceZone": { "type": "keyword" },
				"LogForwardingProfile": { "type": "keyword" },
				"SerialNumber": { "type": "integer" },
				"DestinationZone": { "type": "keyword" },
				"DestinationLocation": { "type": "keyword" },
				"Application": { "type": "keyword" },
				"dstPostNAT": { "type": "ip" },
				"URLCategory": { "type": "keyword" },
				"srcPostNAT": { "type": "ip" },
				"Type": { "type": "keyword" },
				"SessionEndReason": { "type": "keyword" },
				"server_name": { "type": "keyword" },
				"RepeatCount": { "type": "integer" },
				"sequence": { "type": "integer" },
				"srcPostNATPort": { "type": "integer" },
				"ReceiveTime": { "type": "date" },
				"DeviceGroupHierarchyL1": { "type": "keyword" },
				"DeviceGroupHierarchyL2": { "type": "keyword" },
				"DeviceGroupHierarchyL3": { "type": "keyword" },
				"DeviceGroupHierarchyL4": { "type": "keyword" },
				"SessionID": { "type": "integer" },
				"totalPackets": { "type": "integer" },
				"dstPostNATPort": { "type": "integer" },
				"IngressInterface": { "type": "keyword" },
				"ActionFlags": { "type": "keyword" },
				"dstPackets": { "type": "integer" },
				"Subtype": { "type": "keyword" },
				"srcPackets": { "type": "integer" },
				"vSrcName": { "type": "keyword" },
				"VirtualSystem": { "type": "keyword" },
				"cat": { "type": "keyword" },
				"devTime": { "type": "date" },
				"StartTime": { "type": "date" },
				"RuleName": { "type": "keyword" },
				"action": { "type": "keyword" },
				"SourceLocation": { "type": "keyword" },

				# Suricata
				# --------
				"payload_printable": { "type": "keyword" },
				"event_type": { "type": "keyword" },
				"stream": { "type": "integer" },
				"in_iface": { "type": "keyword" },
				"alert.category": { "type": "text" },
				"alert.severity": { "type": "integer" },
				"alert.rev": { "type": "integer" },
				"alert.gid": { "type": "integer" },
				"alert.signature": { "type": "text" },
				"alert.action": { "type": "keyword" },
				"alert.signature_id": { "type": "integer" },
				"packet": { "type": "text" },
				"packet_info.linktype": { "type": "integer" },
				"payload": { "type": "text" },
				"http.hostname": { "type": "keyword" },
				"http.http_method": { "type": "keyword" },
				"http.http_user_agent": { "type": "keyword" },
				"http.length": { "type": "integer" },
				"http.url": { "type": "keyword" },
				"http.protocol": { "type": "keyword" },
				"tls.fingerprint": { "type": "keyword" },
				"tls.issuerdn": { "type": "text" },
				"tls.notafter": { "type": "date" },
				"tls.notbefore": { "type": "date" },
				"tls.sni": { "type": "keyword" },
				"tls.subject": { "type": "keyword" },
				"tls.version": { "type": "keyword" },
				"dns.id": { "type": "keyword" },
				"dns.rcode": { "type": "keyword" },
				"dns.rrname": { "type": "keyword" },
				"dns.rrtype": { "type": "keyword" },
				"dnt.ttl": { "type": "integer" },
				"dns.type": { "type": "keyword" },
			}
		},
	}
})