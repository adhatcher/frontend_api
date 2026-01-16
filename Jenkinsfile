pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'adhatcher'
        DOCKER_HUB_PASS = credentials('docker-hub-credentials') // Store in Jenkins
        IMAGE_NAME = 'frontend_api'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/adhatcher/frontend_api.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_HUB_USER/$IMAGE_NAME:$IMAGE_TAG -t $DOCKER_HUB_USER/$IMAGE_NAME:latest .'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                sh 'echo $DOCKER_HUB_PASS | docker login -u $DOCKER_HUB_USER --password-stdin'
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                sh 'docker push $DOCKER_HUB_USER/$IMAGE_NAME:$IMAGE_TAG'
                sh 'docker push $DOCKER_HUB_USER/$IMAGE_NAME:latest'
            }
        }

        stage('Cleanup') {
            steps {
                sh 'docker rmi $DOCKER_HUB_USER/$IMAGE_NAME:$IMAGE_TAG'
            }
        }
    }

    post {
        success {
            echo "Docker image pushed successfully!"
        }
        failure {
            echo "Build failed!"
        }
    }
}