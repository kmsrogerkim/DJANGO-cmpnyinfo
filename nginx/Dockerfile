FROM nginx:1.19.0-alpine

WORKDIR /
COPY ./static /static

#REPLACE DEFAULT CONF FOR NGINX IN CONTAINERE WITH MY DEFAUTL CONF
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]