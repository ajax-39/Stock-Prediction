# ============================================================================
# Reliance Stock BDA Platform - Distributed Base Image
# Components: Hadoop 3.3.6, Spark 3.4.1, Hive 3.1.3, HBase 2.4.17, Python 3.10
# ============================================================================
FROM ubuntu:22.04

LABEL maintainer="BDA Team" \
      description="All-in-one Big Data Analytics Platform for Stock Prediction"

ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_VERSION=3.3.6
ENV SPARK_VERSION=3.4.1
ENV HIVE_VERSION=3.1.3
ENV HBASE_VERSION=2.4.17

ENV HADOOP_HOME=/opt/hadoop
ENV SPARK_HOME=/opt/spark
ENV HIVE_HOME=/opt/hive
ENV HBASE_HOME=/opt/hbase

ENV HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
ENV YARN_CONF_DIR=${HADOOP_HOME}/etc/hadoop
ENV SPARK_CONF_DIR=${SPARK_HOME}/conf
ENV HIVE_CONF_DIR=${HIVE_HOME}/conf
ENV HBASE_CONF_DIR=${HBASE_HOME}/conf

ENV PATH=${PATH}:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${HIVE_HOME}/bin:${HBASE_HOME}/bin

ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

# ---------- System Packages ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk-headless \
    python3 python3-pip python3-venv \
    curl wget ssh rsync procps net-tools iproute2 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python

# ---------- SSH Configuration ----------
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa \
    && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys \
    && chmod 600 ~/.ssh/authorized_keys
RUN echo "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null" > ~/.ssh/config

# ---------- Hadoop 3.3.6 ----------
RUN wget -q https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt/ \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm hadoop-${HADOOP_VERSION}.tar.gz

# ---------- Spark 3.4.1 ----------
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz -C /opt/ \
    && mv /opt/spark-${SPARK_VERSION}-bin-hadoop3 ${SPARK_HOME} \
    && rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# ---------- Python Dependencies ----------
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ---------- Configuration Ingestion ----------
COPY docker/config/core-site.xml       ${HADOOP_CONF_DIR}/core-site.xml
COPY docker/config/hdfs-site.xml       ${HADOOP_CONF_DIR}/hdfs-site.xml
COPY docker/config/yarn-site.xml       ${HADOOP_CONF_DIR}/yarn-site.xml
COPY docker/config/mapred-site.xml     ${HADOOP_CONF_DIR}/mapred-site.xml
COPY docker/config/spark-defaults.conf  ${SPARK_HOME}/conf/spark-defaults.conf

# ---------- Directories & Permissions ----------
RUN mkdir -p /app /hadoop/dfs/name /hadoop/dfs/data /hadoop/tmp
WORKDIR /app

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# NameNode UI: 9870, HDFS: 9000, YARN: 8088, Spark Master: 8080/7077, Streamlit: 8501, Kafka: 9092
EXPOSE 9870 9000 8088 8080 7077 8501 9092 2181

ENTRYPOINT ["/entrypoint.sh"]
