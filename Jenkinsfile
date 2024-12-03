pipeline{
    agent any
    stages{
        stage('Clone Repository'){
            steps{
                git 'https://github.com/PavanTejaReddy05/WeatherAPI'
            }
        }
        stage('Build Docker Image'){
            steps{
                script{
                    docker.Build("pavantejareddy05/weather-api")
                }
            }
        }
        stage('Push to Docker Hub'){
            steps{
                withDockerRegistry([credentialsId: 'dockerhub-credentials', url:'']){
                    script{
                        docker.Image("pavantejareddy05/weather-api").Push("latest")
                    }
                }
            }
        }
    }
}