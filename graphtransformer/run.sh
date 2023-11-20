#!/usr/bin/env bash

# Install Miniconda3

conda create -n snowgraph --python=3.6
source conda activate

pip install -r graph_app/requirements.txt
pip install -r graph_core/requirements.txt
pip install -r graphtransformer/requirements.txt
pip install -r graphloader/requirements.txt
mvn clean package -p extractor/pom.xml

echo "Installed all dependencies"

nohup python graphloader/src/main/python/server/GraphLoaderServer.py > loader.log &
nohup python graphtransformer/src/main/python/server/GraphTransformerServer.py > loader.log &
nohup python graph_app/src/main/python/server/GraphAppServer.py > loader.log &
nohup python graph_core/src/main/python/server/GraphCoreServer.py > loader.log &

cd extractor/
nohup mvn spring-boot:run > extractor.log &

echo "Started all components, connect to use!"
