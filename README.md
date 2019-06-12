Metabulo
========

Getting started
---------------

This project includes a `Pipfile` to help set up a virtual environment for
Metabulo. To set up the virtual environment

```sh
pipenv install
```

and to enter it

```sh
pipenv shell
```

Metabulo is configured from a `.env` file present in the current directory where
it is executed.  See the included [.env_example](./.env_example) for an example
(or try [.env_pwd](./env_pwd), which saves DB and uploaded files in the checked
out directory rather than your home directory).  Once the environment is in
place, you will need to initialize the tables by running

```sh
metabulo-create-tables
```

This will create a data directory according to the `SQLALCHEMY_DATABASE_URI` and
`UPLOAD_FOLDER` environment variables defined in the `.env` file.

Start the development server by running:

```sh
flask run
```

To start the frontend, run:

```sh
cd web/
yarn
yarn serve
```

R Processing Functions using OpenCPU
------------------------------------

The [devops](./devops) directory contains everything needed to spin up an
[OpenCPU](https://www.opencpu.org/) instance with all dependencies necessary
for the processing backend.  To run it locally, build the docker container

```sh
cd devops
docker build -t metabulo .
```

and start the instance

```sh
docker run -it -p 8004:8004 metabulo
```

You may find that changes to the position or size of the window in which the
Docker image runs will cause the service to terminate with `SIGWINCH`; this is
actually intended behavior and can be avoided by running the image *without*
allocating a pseudo-terminal and keeping `stdin` open:

```sh
docker run --name metabulo -p 8004:8004 metabulo
```

To stop this container, use a command like `docker stop metabulo` from another
terminal.

This installation includes a custom R package called
[metabulo](devops/metabulo), which contains all functions that are exposed to
the API server for CSV file processing.  Functions contained in this package
should accept a path to a CSV file as an argument and return a data frame.  The
(work-in-progress) backend code at [metabulo/opencpu.py](metabulo/opencpu.py)
handles the communication between pandas and R data frames.  To add additional
methods exposed to the API server, add the function to the metabulo package and
rebuild the docker image.
