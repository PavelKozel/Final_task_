pipeline {
    agent any
    stages {
        stage('Git copy') {
            steps {
                git 'https://github.com/PavelKozel/testautomation.git'
            }
        }
        stage('Syntax check') {
             steps {
                 powershell """cd Script_ebooks
                               pylint -f parseable -d I0011,R0801 project.py | tee pylint.out"""
            }
        }
        stage('Build') {
            steps {
                powershell """cd Script_ebooks
                              python project.py dev"""
            }
        }
//        stage('Test') {
//             steps {
//                 powershell """cd Test_framework
//                               python main.py dev"""
//            }
//        }
    }
}
