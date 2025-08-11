pipeline {
    agent any

    environment {
        REGISTRY_NAME = "https://harbor.infra.crl.aero"
        IMAGE_NAME = "harbor.infra.crl.aero/test/app1"
        
        DOCKER_CREDENTIALS_ID = "Harbor_user"
        GIT_HELM_REPO_URL = "git@github.com:epapyrus/test_app.git"
        GIT_CREDENTIALS_ID = "git_ssh_key"
       // HELM_CHART_DIR = "myapp-chart"
        
    }

    parameters {
        choice(
            name: 'TARGET_BRANCH',
            choices: ['dev', 'test', 'prod'],
            description: 'Choisir la branche à exécuter'
        )
    }

    stages {
stage('Checkout') {
    steps {
        script {
            def branchToCheckout = params.TARGET_BRANCH == 'prod' ? 'main' : params.TARGET_BRANCH
            checkout([$class: 'GitSCM',
                branches: [[name: "*/${branchToCheckout}"]],
                userRemoteConfigs: [[
                    url: 'git@github.com:Hamdi-chebbi/test_app.git',
                    credentialsId: 'git_ssh_key'  // <- ID de la clé SSH dans Jenkins
                ]]
            ])
            echo "Checkout de la branche : ${branchToCheckout}"
        }
    }
}


        stage('Get Version') {
            steps {
                script {
                    IMAGE_TAG = sh(
                        script: "grep VERSION version.py | sed -E 's/.*\"(.*)\"/\\1/'",
                        returnStdout: true
                    ).trim()
                    echo "La version trouvée est : ${IMAGE_TAG} sur la branche ${params.TARGET_BRANCH}"
                }
            }
        }

        stage('Build Docker Image') {

            steps {
                script {
                    // def version = sh(script: "grep VERSION version.py | sed -E 's/.*\"(.*)\"/\\1/'", returnStdout: true).trim()
                    // echo "La version trouvée est : ${version}"
                    
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Push Docker Image to Harbor') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                    script {
                        sh """
                        echo "$HARBOR_PASS" | docker login ${REGISTRY_NAME} -u "$HARBOR_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker logout ${IMAGE_NAME}
                        """
                    }
                }
            }
        }

       stage('Update Helm Chart Version') {
    steps {
        script {
            // Traduction du paramètre en branche Git
            def branchToCheckout = params.TARGET_BRANCH == 'prod' ? 'main' : params.TARGET_BRANCH

            dir('helm-chart') {
                deleteDir()

                checkout([$class: 'GitSCM',
                    branches: [[name: "refs/heads/${branchToCheckout}"]],
                    userRemoteConfigs: [[
                        url: "${GIT_HELM_REPO_URL}",
                        credentialsId: "${GIT_CREDENTIALS_ID}"
                    ]]
                ])

                withCredentials([sshUserPrivateKey(credentialsId: "${GIT_CREDENTIALS_ID}", keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        eval \$(ssh-agent -s)
                        ssh-add \$SSH_KEY
                        git checkout ${branchToCheckout}
                        yq -y '.appVersion = "${IMAGE_TAG}"' Chart.yaml > Chart.tmp && mv Chart.tmp Chart.yaml
                        git config user.name "jenkins"
                        git config user.email "jenkins@yourdomain.com"
                        git add Chart.yaml
                        cat Chart.yaml
                        ls -l
                        git commit -m "minor update on ${branchToCheckout} environment (version: ${IMAGE_TAG})" || echo "No changes to commit"
                        git log
                        git push origin ${branchToCheckout}
                    """
                }
            }
        }
    }
}
    }
}