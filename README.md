Steps:

1. 
- disconnect VPN

2.
$ sh setup.sh <playground-id> <user> <pass>

3.
- save jenkins password as environment variable
- log into jenkins instance
- install suggested plugins
- install Statistics Gather
- configure settings for Statistics Gatherer
http://elasticsearch-logging.monitoring-observability:9200/logstash-jenkins/jenkins

4.
$ sh post_deploy_config.sh

5.
- start build
- configure logstash index pattern to display duration in seconds
- copy id for logstash index pattern

6.
$ sh kibana_dashboard.sh < logstash-index-pattern-id >



Troubleshooting:

kubernetes.pod.name: jenkins*

curl -X GET "localhost:5601/api/kibana/dashboards/export?dashboard=f12be2b0-95e4-11ec-986b-dd6829ca8c81" -H 'kbn-xsrf: true' >> elk/dashboard.json

curl -vvv -X POST "localhost:5601/api/kibana/dashboards/import?exclude=index-pattern" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' --data-binary "@elk/dashboard.json"