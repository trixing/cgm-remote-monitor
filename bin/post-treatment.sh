#!/bin/sh

API_SECRET=$(echo -n string_secret | sha1sum)

curl -vv -H "Content-Type: application/json" -H "api-secret: $API_SECRET"  -XPOST 'http://localhost:1337/api/v1/treatments/' -d '{
  "enteredBy": "Dad",
  "eventType":"Site Change",
  "glucoseValue": 322,
  "glucoseType": "sensor",
  "carbsGiven": 0,
  "insulinGiven": 1.25,
  "notes": "Argh..."
}'
