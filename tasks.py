from cmath import log
import json
import pipes
import requests
from elasticsearch6 import Elasticsearch
from requests.structures import CaseInsensitiveDict
from invoke import task
from jinja2 import Template
import jenkins


def initialize_jenkins_client(ctx, password):
    url = 'http://localhost:8080/'
    username = 'admin'
    if password == "None":
        password = get_jenkins_admin_pass(ctx)
    jenkins_client = jenkins.Jenkins(url, username=username,password=password)
    return jenkins_client


# repo returns 404
@task
def install_jenkins_plugins(ctx, password):
    jenkins_client = initialize_jenkins_client(ctx, password)
    info = jenkins_client.install_plugin("Logstash")
    print(info)


@task
def create_jenkins_pipeline(ctx, password):
    jenkins_client = initialize_jenkins_client(ctx, password)
    
    with open("kubernetes-jenkins/pipeline.xml", "r") as f:
        my_job = f.read()
        jenkins_client.create_job('jenkins-k8s-observability', my_job)    


@task
def template_jenkins_volume(ctx):
    worker_nodes = ctx.run("kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o json", hide=True).stdout
    worker_nodes = json.loads(worker_nodes)
    node_names = []

    for item in worker_nodes["items"]:
        node = json.loads(item["metadata"]["annotations"]["csi.volume.kubernetes.io/nodeid"])
        node_name = node["pd.csi.storage.gke.io"].split("/")[-1]
        node_names.append(node_name)

    with open("kubernetes-jenkins/volume.yaml.tmpl", "r") as f:
        template = Template(f.read())

    jenkins_volume = template.render(worker_node_a=node_names[0], \
        worker_node_b=node_names[1], worker_node_c=node_names[2])

    with open("kubernetes-jenkins/volume.yaml", "w") as f:
        f.write(jenkins_volume)


@task
def template_kibana_dashboard(ctx, logstash_index_pattern):
    with open("elk/dashboard.json.tmpl", "r") as f:
        template = Template(f.read())

    kibana_dashboard = template.render(logstash_index_pattern=logstash_index_pattern)
    with open("elk/dashboard.json", "w") as f:
        f.write(kibana_dashboard)


@task
def get_jenkins_admin_pass(ctx):
    pods = ctx.run("kubectl get pods -o json -n devops-tools", hide=True).stdout
    pods = json.loads(pods)

    for item in pods["items"]:
        jenkins_pod = item["metadata"]["name"]

    password_created = False
    while(not password_created):
        line_before_password = "Please use the following password to proceed to installation:"
        logs = ctx.run(f"kubectl logs {jenkins_pod} -n devops-tools", hide=True).stdout
        logs = logs.split("\n")
        if line_before_password in logs:
            password_created = True

    index = logs.index(line_before_password)
    jenkins_admin_pass = logs[index + 2]

    print(f"JENKINS_ADMIN_PASS={pipes.quote(jenkins_admin_pass)}")

    return jenkins_admin_pass


@task
def create_elasticsearch_index(ctx):
    index = 'logstash-jenkins'
    es_client = Elasticsearch(
    "http://localhost:9200")

    with open("elk/logstash-jenkins-index.json", "r") as f:
        mappings = json.load(f)
        request_body = {
            "settings" : {
                "number_of_shards": 5,
                "number_of_replicas": 1
            },
            'mappings': mappings
        }

    print(f"creating {index} index...")
    es_client.indices.create(index=index, body=request_body)


# returns 404
@task
def create_kibana_index_pattern(ctx, title, time_field_name):
    url = "http://localhost:5601/api/index_patterns/index_pattern"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {
    "index_pattern": {
        "title": title,
        "timeFieldName": time_field_name
        }
    }

    resp = requests.post(url, headers=headers, data=data)

    print(resp.status_code)
