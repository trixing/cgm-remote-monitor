#!/bin/sh

# for admin, remove noauth in /etc/mongodb.conf

# Keep bridge working
# */5 * * * * /usr/bin/curl http://localhost:1338/

while true; do
  . testing.env
  node server.js
  sleep 60
done
