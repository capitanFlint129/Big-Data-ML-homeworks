FROM apache/flink:1.16.0-scala_2.12-java8 AS flink
ARG FLINK_VERSION=1.16.0

# Install python3.7 and pyflink
# Pyflink does not yet function with python3.9, and this image is build on
# debian bullseye which ships with that version, so build python3.7 here.
RUN set -ex; \
  apt-get update && \
  apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev lzma liblzma-dev && \
  wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz && \
  tar -xvf Python-3.7.9.tgz && \
  cd Python-3.7.9 && \
  ./configure --without-tests --enable-shared && \
  make -j4 && \
  make install && \
  ldconfig /usr/local/lib && \
  cd .. && rm -f Python-3.7.9.tgz && rm -rf Python-3.7.9 && \
  ln -s /usr/local/bin/python3 /usr/local/bin/python && \
  ln -s /usr/local/bin/pip3 /usr/local/bin/pip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python -m pip install --upgrade pip; \
  pip install apache-flink==${FLINK_VERSION}; \
  pip install kafka-python;

# Download connector libraries
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/${FLINK_VERSION}/flink-json-${FLINK_VERSION}.jar; \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/${FLINK_VERSION}/flink-sql-connector-kafka-${FLINK_VERSION}.jar; \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch7/${FLINK_VERSION}/flink-sql-connector-elasticsearch7-${FLINK_VERSION}.jar;


RUN echo "taskmanager.memory.jvm-metaspace.size: 512m" >> /opt/flink/conf/flink-conf.yaml;

WORKDIR /opt/flink


FROM flink AS flink_hadoop

RUN apt-get update -y \
    && apt-get install -y openjdk-11-jdk \
    && apt-get install -y lsb-release \
    && apt-get install -y net-tools \
    && apt-get install -y curl

RUN DEBIAN_FRONTEND="noninteractive" \
    TZ="Europe/Moscow" \
    apt-get install -y tzdata

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata

WORKDIR /opt

RUN curl -o hadoop-3.3.6.tar.gz https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
RUN tar -xzf hadoop-3.3.6.tar.gz -C /opt
RUN rm hadoop-3.3.6.tar.gz
RUN ln -sf /opt/hadoop-3.3.6 /opt/hadoop

RUN apt-get update -y \
    && apt-get install -y python3-pip

RUN mkdir -p /tmp/hadoop-hadoop

WORKDIR /opt/hadoop

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_HOME /opt/hadoop
ENV PATH $PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# fix WARN NativeCodeLoader: Unable to load native-hadoop library for your platform...
ENV LD_LIBRARY_PATH=$HADOOP_HOME/lib/native
ENV HADOOP_CONF_DIR $HADOOP_HOME/etc/hadoop

WORKDIR /opt/flink

