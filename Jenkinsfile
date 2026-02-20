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

        stage('Deploy on Localhost') {
            steps {
                echo 'Starting Flask app on localhost'

                bat '''
                start cmd /k "cd trash-app && python app.py"
                '''
            }
        }
    }
}
