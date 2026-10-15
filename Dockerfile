FROM aquib4040/azmlv1:latest

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT ["bash", "start.sh"]\n