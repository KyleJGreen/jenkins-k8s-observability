import os
import pipes
import sys
from invoke import task
from jinja2 import Template


def delete_urns(ctx, urns):
    failed_to_delete = []
    for urn in urns:
        try:
            ctx.run(
                f"pulumi state delete \'{urn}\' --non-interactive --stack dev")
        except:
            failed_to_delete.append(urn)
            continue

    if failed_to_delete:
        delete_urns(ctx, failed_to_delete)


@task
def get_and_delete_urns(ctx):
    output = ctx.run("pulumi stack --show-urns --stack dev").stdout
    urns = []

    for line in output.split("\n"):
        if "URN" in line:
            line = line.split(" ")
            urns.append(line[-1])

    if urns:
        delete_urns(ctx, urns)

def initialize_gcloud(ctx, project_id, gcp_user, gcp_pass):
    ctx.run(f"export GCP_USER={gcp_user}")
    ctx.run(f"export GCP_PASS={gcp_pass}")
    ctx.run(f"gcloud auth login --project {project_id}")
    ctx.run(f"gcloud auth application-default login")
    ctx.run("gcloud services enable container.googleapis.com")


def initialize_pulumi(ctx, project_id):
    pulumi_config = "./Pulumi.dev.yaml"

    with open(f"{pulumi_config}.tmpl", "r") as f:
        template = Template(f.read())
    data = template.render(project_id=project_id)

    with open(pulumi_config, "w") as f:
        f.write(data)
    
    try:
        ctx.run("pulumi stack rm -f -y --preserve-config")
        ctx.run("pulumi stack init dev")
    except:
        ctx.run("pulumi stack init dev")


@task
def deploy_gke(ctx, project_id, gcp_user, gcp_pass):
    initialize_gcloud(ctx, project_id, gcp_user, gcp_pass)
    initialize_pulumi(ctx, project_id)
    ctx.run("pulumi up --yes --non-interactive --stack dev")
    ctx.run("pulumi stack output kubeconfig --show-secrets --stack dev > kubeconfig")
    set_kubeconfig(ctx)


@task
def set_kubeconfig(ctx):
    kubeconfig = f"{os.getcwd()}/kubeconfig"
    print(f"export KUBECONFIG={pipes.quote(kubeconfig)}")
