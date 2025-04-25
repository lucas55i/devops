def call(body){

    def settings = [:]
    body.resolveStrategy - Closure.DELEGATE_FIRST
    body.delegate = settings
    body()   
                 
    container("sonar-scanner-cli"){
        sh '''
            echo "JOB_NAME: ${JOB_NAME}"

            sonar-scanner -X \
            -Dsonar.login=${SONAR_LOGIN} \
            -Dsonar.projectKey=${JOB_NAME%/*}-${GIT_BRANCH} \
            -Dsonar.qualitygate.wait=true
       '''
    }
}