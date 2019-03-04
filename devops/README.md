# Instructions

### Pulling the Docker Image

It takes around 50 minutes to build the image.
It might be more convenient to pull it from Dockerhub.

```sh
docker pull dozturk2/metabulo:latest
```

Then you can visit http://localhost:8004/ocpu or http://localhost:8004/rstudio

The username and password will be "opencpu".

### Developing locally

There is a vagrant file which could be used for local development.
We need the sdist created first.

Simply run:

```sh
cd devops
./build_sdist.sh
```

Make sure tox is installed in the virtual environment that you run the command.
That should create the /dist directory.

Then we can get the vagrant box up and running by doing:

```sh
vagrant up
```
