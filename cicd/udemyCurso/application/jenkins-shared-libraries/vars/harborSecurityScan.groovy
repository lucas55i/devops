def call(body){

    def settings = [:]
    body.resolveStrategy - Closure.DELEGATE_FIRST
    body.delegate = settings
    body()   
                 
    container("alpine"){
        sh '''
            apk add curl jq

            MAX_RETRY=20
            COUNT=1
            SLEEP=5

            SEVERITY="null"

            ENVIROMENT=""
            if [ $(echo $GIT_BRANCH | grep ^develop$) ]; then
                ENVIROMENT="dev"
            elif [ $(echo $GIT_BRANCH | grep -E "^hotfix-.*") ]; then
                ENVIROMENT="stg"        
            fi

            TAG="$(cat /artifacts/${ENVIROMENT}.artifact)"

            HARBOR_URL="http://harbor.localhost.com"
            HARBOR_PATH="api/v2.0/projects/lucasjesusme/repositories/${JOB_NAME%/*}/artifacts/${TAG}"
            HARBOR_URL_PARAMS="with_scan_overview=true"
            

            while [ "$SEVERITY" == "null" ]; do
                SEVERITY=$(curl -X GET \
                "${HARBOR_URL}/${HARBOR_PATH}?${HARBOR_URL_PARAMS}" \
                -H "accept: application/json" \
                -H "authorization: Basic ${HARBOR_CREDENTIALS}" \
                | jq -r '.scan_overview | to_entries | .[].value.severity'
                )

                echo "Sleep for ${SLEEP}s | count: ${COUNT}"
                sleep $SLEEP
                SLEEP=$(($SLEEP * 2))
                COUNT=$(($COUNT + 1))

                if [ $COUNT -ge $MAX_RETRY ]; then
                    echo "Reached maximuim retry of ${MAX_RETRY}, exiting"
                    exit 1
                fi
            done

            if [ "$SEVERITY" == "Critical" ]; then
                echo "There is Critical severity, please check on Harbor for the report"
                exit 1
            else
                echo "All good proceeding to the next stage"
            fi
       '''
    }
}