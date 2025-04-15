#!/bin/bash

apk add curl jq

MAX_RETRY=20
COUNT=1
SLEEP=1

SEVERITY="null"
HARBOR_URL="http://harbor.localhost.com"
HARBOR_PATH="api/v2.0/projects/lucasjesusme/repositories/${JOB_NAME}/artifacts/${TAG}"
HARBOR_URL_PARAMS="with_scan_overview=true"

while [ "$SEVERITY" == "null" ]; do
    SEVERITY=$(severity=$(
        curl -X GET \
            "${HARBOR_URL}/${HARBOR_PATH}?${HARBOR_URL_PARAMS}' \
            -H 'accept: application/json' \
            -H "authorization: Basic ${HARBOR_CREDENTIALS}" \
            | jq '.scan_overview | to_entries | .[].value.severity"
    ))

    echo "Sleep for ${SLEEP}s | count: ${COUNT}"
    sleep $SLEEP
    SLEEP=$(($SLEEP * 2))
    COUNT=$(($COUNT + 1))

    if [ $COUNT -ge $MAX_RETRY ]; then
        echo "Reached maximuim retry of ${MAX_RETRY}, exiting"
        exit 1
    fi
done

if [ $SEVERITY == "Critical" ]; then
    echo "There is Critical severity, please check on Harbor for the report"
    exit 1
else
    echo "All good proceeding to the next stage"
fi

curl -v -X GET "http://harbor.localhost.com/api/v2.0/projects/lucasjesusme/repositories/restapi-flask/artifacts/dev-61060bdc46?with_scan_overview=true" \
  -H "accept: application/json" \
  -H "authorization: Basic YWRtaW46SGFyYm9yMTIzNDU="
