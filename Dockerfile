FROM node:lts

USER root

RUN npm install -g typescript

WORKDIR /home/app
USER node

# ENTRYPOINT /bin/bash

CMD tail -f /dev/null
