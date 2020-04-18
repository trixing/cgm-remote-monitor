FROM node:10.20-alpine

MAINTAINER Nightscout Contributors, Erik Dilemma <erik.dilemma@gmail.com>
#
# Build: docker build -t trixing/nightscout .
# Run: docker run -p 1337:1337 trixing/nightscout

EXPOSE 1337

#RUN apt-get update && \
#  apt-get -y dist-upgrade

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh python build-base

RUN mkdir -p /opt/app
ADD . /opt/app
WORKDIR /opt/app
COPY package.json package-clock.json* ./
RUN npm config set unsafe-perm true
RUN npm i npm@latest -g
RUN npm install && \
    npm cache clean --force

#ENV PATH /opt/node_modules/.bin/:$PATH

#ADD . /opt/app
#WORKDIR /opt/app
#RUN ln -s /opt/node_modules /opt/app/node_modules

RUN  npm run postinstall && \
     npm run env && \
     npm audit fix


CMD ["node", "server.js"]
