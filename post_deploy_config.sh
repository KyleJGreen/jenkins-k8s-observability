eval $(invoke get-jenkins-admin-pass)
echo "JENKINS_ADMIN_PASS=$JENKINS_ADMIN_PASS"

invoke create-elasticsearch-index
invoke create-jenkins-pipeline $JENKINS_ADMIN_PASS