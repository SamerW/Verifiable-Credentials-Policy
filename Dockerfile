FROM ubuntu:focal

WORKDIR /root

ARG GIT_TOKEN

RUN apt update && apt install -y python3-pip python3-venv git
RUN git clone --branch aws-ecr-deployment https://ioram7:${GIT_TOKEN}@gitlab.com/vcgroup/vc-verifier/cnl-gui-policy-man.git

ENV FLASK_APP module
ENV FLASK_ENV development

RUN bash -c "shopt -s dotglob nullglob && mv /root/cnl-gui-policy-man/* /root"
RUN rmdir /root/cnl-gui-policy-man

RUN sed -i 's|/Users/admin/Irit/Projets/CNL/development/module/||g' ./module/main.spec
RUN sed -i 's|/Users/admin/Irit/Projets/CNL/development/module||g' ./module/main.spec
RUN python3 -m venv env
RUN /bin/bash -c "source ./env/bin/activate"
RUN pip install -r requirements.txt
RUN pip install pyinstaller
RUN cd /root/module && pyinstaller -w -F main.spec

FROM ubuntu:focal
WORKDIR /srv/cnl-gui-policy-man
ENV FLASK_APP module
ENV FLASK_ENV development
RUN mkdir -p /srv/cnl-gui-policy-man
COPY --from=0 /root/module/dist/main /srv/cnl-gui-policy-man
RUN apt update && apt install -y libexpat1
CMD ln -s /vol/cnl.sqlite . && ./main
