pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'refs/heads/master', url: 'git@github.com:noa-bl/FinalProject.git', credentialsId: 'ssh-cred'
            }
        }
        stage('Build') {
            steps {
                sh 'echo Hello Jenkins!'
            }
        }
    }
}
