# Instructions

### Prerequisites

In order to build the containers install the following:

1) Docker
2) Packer
3) Ansible
4) Singularity

Latest versions of prerequisites should be ok to install.

### Building the Singularity Image

After all the preprequisites are installed run:

Create a local registry for docker.

```sh
cd devops
docker run -p 5000:5000 -d --rm --name local_registry registry:2
```

Create a provisioned metabolomics Docker image

```sh
ANSIBLE_FORCE_COLOR=1 packer build -color=false packer.json
```

Build the Metabolomics image from the Docker image

```sh
SINGULARITY_NOHTTPS=yes sudo -E singularity build metabolomics.simg.0 Singularity.metabolomics
mv -f metabolomics.simg.0 metabolomics.simg
```

Tear down the local docker registry

```sh
docker kill local_registry || true
```

This should place the __singularity.img__ file which is a singularity image.
The image will have R as well as [MetaboAnalystR](https://github.com/xia-lab/MetaboAnalystR) package installed.

### Building the Docker Image

There is also a Dockerfile for creating a docker image.

In order to build the docker image:

```sh
cd devops
docker build -t metabolomics .
```

### Pulling the Docker Image

It takes around 50 minutes to build the image.
It might be more convenient to pull it from Dockerhub.

```sh
docker pull dozturk2/metabolomics:latest
```

There are github actions set for pushing the docker image
so it will be periodically updated on Dockerhub.

### Running R Scripts Against the Container

After we build the images we can run R scripts against the container.
There are currently 2 simple examples that could be used as starting points.

Simply run:

```sh
 singularity exec metabolomics.simg Rscript examples/simple.R examples/data_original.csv
```

We just ran a simple R script and the script requires a data file as an argument (which is data_original.csv) file.
This should produce a pdf file in your current directory which should have a plot.

Also to call some of the functions that MetaboAnalystR library provides check the other R example.

```sh
singularity exec metabolomics.simg Rscript examples/metaboanalyst.R
```
