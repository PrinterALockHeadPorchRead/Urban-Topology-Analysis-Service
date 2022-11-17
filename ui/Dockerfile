FROM node:16.17.1

RUN mkdir /application

WORKDIR /application

COPY . /application

RUN npm install
RUN npm install -g @angular/cli

CMD ng s --host 0.0.0.0
