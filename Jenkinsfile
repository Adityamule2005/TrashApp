pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code fetched successfully'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r trash-app/requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'python --version'
            }
        }
    }
}
