## jenkins-k8s-observability

### Description
This repository provides the infrastructure as code to deploy a GKE cluster using Pulumi. It also includes the code for deploying Jenkins and the ELK stack within that cluster. By following the instructions below, you can deploy these resources in your own Google Cloud environment and configure an ElasticSearch dashboard to monitor the resource utilization of your Jenkins instance along with metrics on workflows that have run on the instance.

####Steps:

1.  `$ sh setup.sh <project-id> <user> <pass>`

2. Setup Jenkins
    * save jenkins password as environment variable
    * log into jenkins instance
    * install suggested plugins
    * install Statistics Gather
    * configure settings for Statistics Gatherer
http://elasticsearch-logging.monitoring-observability:9200/logstash-jenkins/jenkins

3. `$ sh post_deploy_config.sh`

4. Configure logstash
    * start build
    * configure logstash index pattern to display duration in seconds
    * copy id for logstash index pattern

5. `$ sh kibana_dashboard.sh < logstash-index-pattern-id >`



####Troubleshooting:


Export the Kibana dashboard:
```
curl -X GET "localhost:5601/api/kibana/dashboards/export?dashboard=f12be2b0-95e4-11ec-986b-dd6829ca8c81" -H 'kbn-xsrf: true' >> elk/dashboard.json
```

Import the Kibana dashboard:
```
curl -vvv -X POST "localhost:5601/api/kibana/dashboards/import?exclude=index-pattern" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' --data-binary "@elk/dashboard.json"
```