pipeline{
    agent any

    stages{
        
        stage('Checkout') {
            
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {

            steps {

                script {
                    if (isUnix()) {
                        sh 'python3 -m pip install -r requirements.txt'
                    } else {
                        bat 'python -m pip install -r requirements.txt'
                    }
                }
                
            }
        }

        stage('Execute Blazemeter Automation') {

            steps {

                script {

                    if (isUnix()) {
                        sh 'python3 main.py'
                    } else {
                        bat 'python main.py'
                    }
                }
                
            }
        }

        stage('Archive Results') {

            steps {

                archiveArtifacts(
                    artifacts: 'logs/**',
                    allowEmptyArchive: true
                )
            }
        }
    }

    post {

        always {

            echo 'Blazemeter Automation completed'
        }
    }
}