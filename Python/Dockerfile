FROM alpine:latest

RUN apk update && \
    apk add --no-cache ansible

RUN mkdir /root/ansible

VOLUME ["./ansible:/root/ansible"]