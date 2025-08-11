pipeline {
    agent any

    environment {
        REGISTRY_NAME = "https://harbor.infra.crl.aero"
       // IMAGE_NAME = "harbor.infra.crl.aero/test/app1"

        DOCKER_CREDENTIALS_ID = "Harbor_user"
        GIT_HELM_REPO_URL = "git@github.com:epapyrus/test_app.git"
        GIT_CREDENTIALS_ID = "git_ssh_key"
        // HELM_CHART_DIR = "myapp-chart"
    }

    // parameters {
    //     choice(
    //         name: 'TARGET_BRANCH',
    //         choices: ['dev', 'test', 'prod'],
    //         description: 'Sélectionner l’environnement cible (dev, test, prod). La branche correspondante sera utilisée.'
    //     )
    // }


stages {
    stage('Checkout') {
        steps {
            script {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/${env.BRANCH_NAME}"]],
                    userRemoteConfigs: [[
                        url: 'git@github.com:Hamdi-chebbi/test_app.git',
                        credentialsId: 'git_ssh_key'
                    ]]
                ])
                echo "Checkout de la branche : ${env.BRANCH_NAME}"

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

            echo "📦 Version de l'application : ${IMAGE_TAG}"
           
        }
    }
}


stage('Build Docker Image') {
    steps {
        script {
            def branch = env.BRANCH_NAME

            def envName = ''
            if (branch == 'main') {
                envName = 'prod'
            } else if (branch == 'dev' || branch == 'test') {
                envName = branch
            } else {
                // Par défaut, tu peux mettre dev ou autre
                envName = 'dev'
            }

            def imageName = "harbor.infra.crl.aero/test/${envName}/app1"
            echo "Nom de l'image : ${imageName}:${IMAGE_TAG}"
            sh "docker build -t ${imageName}:${IMAGE_TAG} ."
            env.IMAGE_NAME = imageName
        }
    }
}

        stage('Push Docker Image to Harbor') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                    script {
                        sh """
                        echo "$HARBOR_PASS" | docker login ${REGISTRY_NAME} -u "$HARBOR_USER" --password-stdin
                        docker push ${env.IMAGE_NAME}:${IMAGE_TAG}
                        docker logout ${IMAGE_NAME}
                        """
                    }
                }
            }
        }

stage('Update Helm Chart Version') {
    steps {
        script {
            def branchToCheckout = env.BRANCH_NAME
            sh "git branch"
            dir('helm-chart') {
                deleteDir()

                checkout([
                    $class: 'GitSCM',
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
                        git commit -m "update to version: ${IMAGE_TAG}" || echo "No changes to commit"
                        
                        git push origin ${branchToCheckout}
                    """
                }
            }
        }
    }
}
}
}
