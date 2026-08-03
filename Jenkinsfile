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

        stage('Configure Environment') {

            steps {

                withCredentials([
                    string(credentialsId: 'UAT_CLIENT_ID', variable: 'CLIENT_ID'),
                    string(credentialsId: 'UAT_CLIENT_SECRET', variable: 'CLIENT_SECRET'),
                    string(credentialsId: 'BLAZEMETER_API_KEY', variable: 'BM_API_KEY'),
                    string(credentialsId: 'BLAZEMETER_API_SECRET', variable: 'BM_API_SECRET')
                ]) {

                    bat """
                    echo Creating configuration files

                    copy uat.properties.template uat.properties

                    powershell -Command "(Get-Content uat.properties) -replace '<YOUR_CLIENT_ID>', '${env.CLIENT_ID}' | Set-Content uat.properties"

                    powershell -Command "(Get-Content uat.properties) -replace '<YOUR_CLIENT_SECRET>', '${env.CLIENT_SECRET}' | Set-Content uat.properties"


                    copy config\\config.template.yaml config\\config.yaml

                    powershell -Command "(Get-Content config\\config.yaml) -replace 'YOUR_BLAZEMETER_API_KEY', '${env.BM_API_KEY}' | Set-Content config\\config.yaml"

                    powershell -Command "(Get-Content config\\config.yaml) -replace 'YOUR_BLAZEMETER_API_SECRET', '${env.BM_API_SECRET}' | Set-Content config\\config.yaml"
                    """
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