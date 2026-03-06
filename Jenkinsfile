pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t trashapp .'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d -p 5000:5000 trashapp'
            }
        }
    }
}
