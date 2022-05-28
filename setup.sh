PROJECT_ID=$1
GCP_USER=$2
GCP_PASS=$3

# standup gke cluster
cd gcp-py-gke
invoke deploy-gke $PROJECT_ID $GCP_USER $GCP_PASS
eval $(invoke set-kubeconfig)
cd ..

# deploy ELK stack with Metricbeat
kubectl apply -f elk/

# deploy Jenkins
kubectl apply -f kubernetes-jenkins/serviceAccount.yaml -n devops-tools
kubectl apply -f kubernetes-jenkins/volume.yaml -n devops-tools
kubectl apply -f kubernetes-jenkins/deployment.yaml -n devops-tools
kubectl apply -f kubernetes-jenkins/service.yaml -n devops-tools