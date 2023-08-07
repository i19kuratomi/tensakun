FROM python:3

# mecabの導入
RUN apt-get -y update && \
  apt-get -y upgrade && \
  apt-get install -y mecab && \
  apt-get install -y libmecab-dev && \
  apt-get install -y git && \
  apt-get install -y make && \
  apt-get install -y curl && \
  apt-get install -y xz-utils && \
  apt-get install -y file && \
  apt-get install -y sudo && \
  apt-get install -y wget && \
  apt-get install -y nkf

WORKDIR /usr/src/app
ENV FLASK_APP=app

COPY /app/ /usr/src/app
RUN wget https://raw.githubusercontent.com/taku910/mecab/master/mecab-ipadic/Auxil.csv
RUN nkf --overwrite --oc=UTF-8 Auxil.csv
RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
