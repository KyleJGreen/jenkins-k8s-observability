LOGSTASH_INDEX_PATTERN=$1

invoke template-kibana-dashboard $LOGSTASH_INDEX_PATTERN

curl -X POST \
"localhost:5601/api/kibana/dashboards/import?exclude=index-pattern" \
-H 'kbn-xsrf: true' -H 'Content-Type: application/json' --data-binary \
"@elk/dashboard.json"
