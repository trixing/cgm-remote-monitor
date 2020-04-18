
 - apt-get install git-core mongo ...

 - git add upstream https://github.com/nightscout/cgm-remote-monitor.git
 - git fetch upstream
 - git merge upstream/master

 - install mongo (add users)
 - install nodejs
 - npm install
 - sudo npm install bower -g
 - bower install

 - install nginx
 - configure proxy_pass and websocket forwarding

http {
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    upstream websocket {
        server 192.168.100.10:8010;
    }

    server {
        listen 8020;
        location / {
            proxy_pass http://websocket;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
        }
    }
}

 - run it

MONGO_CONNECTION=mongodb://nightscout:pw@localhost:27017/nightscout API_SECRET=myapisecret DISPLAY_UNITS="mg/dl" BASE_URL=http://night.trixing.net HOSTNAME=127.0.0.1 PORT=1337 ENABLE="iob cob bwp basal pump loop" node server.js

- sudo apt-get install certbot -t jessie-backports

