FROM ubuntu:focal

WORKDIR /srv/cnl-gui-policy-man

ENV FLASK_APP module
ENV FLASK_ENV development

RUN mkdir -p /srv/cnl-gui-policy-man
COPY  ${PWD}/module/dist/main /srv/cnl-gui-policy-man

CMD ln -s /vol/cnl.sqlite . && ./main
