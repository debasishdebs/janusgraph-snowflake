FROM ubuntu:18.04

# System packages
RUN apt-get update && apt-get install -y curl

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# To solve add-apt-repository : command not found
#RUN apt-get -y install software-properties-common

# Install Java.
#RUN \
#  echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
#  add-apt-repository -y ppa:webupd8team/java && \
#  apt-get update && \
#  apt-get install -y oracle-java8-set-default && \
#  rm -rf /var/lib/apt/lists/* && \
#  rm -rf /var/cache/oracle-jdk8-installer
RUN apt-get update && \
apt-get install -y openjdk-8-jdk openjdk-8-jre

# Define working directory.
WORKDIR /app

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV JRE_HOME /usr/lib/jvm/java-8-openjdk-amd64/jre

COPY . /app

#RUN conda create -n snowflake-graphdb python=3.7
RUN conda env create --file environment.yml

ENV PATH /miniconda/bin:$PATH

# Initialize conda in bash config fiiles:
#RUN conda init bash

# Activate the environment, and make sure it's activated:
#RUN ["conda", "run", "-n", "snowflake-graphdb", "pip", "install", "-r", "requirements.txt"]
#RUN /bin/bash -c "source activate snowflake-graphdb" && pip install -r requirements.txt
#RUN pip install -r requirements.txt
#RUN echo "conda activate myenv" > ~/.bashrc

COPY .databricks-connect /root/
COPY /libs /miniconda/envs/snowflake-graphdb/lib/python3.7/site-packages/pyspark/jars/
#RUN "cp .databricks-connect /root/"
#RUN "cp /app/libs/* /miniconda/envs/snowflake-graphdb/lib/python3.7/site-packages/pyspark/jars/"
#RUN "cat /app/databricks-connect.txt > /root/.databricks-connect"

#RUN pyb
WORKDIR /app
# /graphloader/src/main/python/server
ENV PYTHONPATH "${PYTHONPATH}://app/src/main/python"
#ENTRYPOINT ["python", "/app/src/main/python/server/GraphTransformerServer.py"]
#ENTRYPOINT ["conda", "run", "-n", "snowflake-graphdb", "databricks-connect", "test"]
ENTRYPOINT ["conda", "run", "-n", "snowflake-graphdb", "python", "/app/src/main/python/server/GraphTransformerServer.py"]
EXPOSE 1020
