FROM alpine/git as clone
WORKDIR /app
# add credentials on build
#ARG SSH_PRIVATE_KEY
#RUN mkdir /root/.ssh/
#RUN chmod 0700 /root/.ssh
#RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa
#RUN chmod 600 /root/.ssh/id_rsa
#
## make sure your domain is accepted
#RUN touch /root/.ssh/known_hosts
#RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts
#
#RUN git clone git@gitlab.com:system-soft-technologies-opensource/graphdb-in-snowflake.git
#RUN cd graphdb-in-snowflake/snowflake-graphdb
COPY . /app

FROM continuumio/miniconda as deploy
WORKDIR /app
#SHELL ["/bin/bash", "--login", "-c"]
# Create the environment:
#COPY --from=clone /app/graphdb-in-snowflake/snowflake-graphdb/graphloader /app
COPY --from=clone /app /app
RUN conda create -n snowflake-graphdb python=3.6

ENV PATH /opt/conda/envs/snowflake-graphdb/bin:$PATH

# Initialize conda in bash config fiiles:
#RUN conda init bash

# Activate the environment, and make sure it's activated:
RUN /bin/bash -c "source activate snowflake-graphdb"
RUN pip install -r requirements.txt
#RUN echo "conda activate myenv" > ~/.bashrc

#RUN pyb
WORKDIR /app
# /graphloader/src/main/python/server
ENV PYTHONPATH "${PYTHONPATH}://app/src/main/python"
ENTRYPOINT ["python", "/app/src/main/python/server/GraphLoaderServer.py"]
EXPOSE 1030
# CMD ["mvn spring-boot:run"]

# docker build -t debasishkanhar/graphextractor:latest --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" .
# docker run -ti -p 8081:8081 debasishkanhar/graphextractor

#FROM tomcat:8.0.51-jre8-alpine
#RUN rm -rf /usr/local/tomcat/webapps/*
#COPY --from=build /app/target/graphextractor.war /usr/local/tomcat/webapps/ROOT.war
#EXPOSE 8080
#ENTRYPOINT ["sh", "-c"]
#CMD ["catalina.sh run"]
