#!/bin/sh

# for admin, remove noauth in /etc/mongodb.conf

# Keep bridge working
# */5 * * * * /usr/bin/curl http://localhost:1337/

while true; do
  . prod.env
  node server.js
  sleep 60
done
