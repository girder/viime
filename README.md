Metabulo
========

Getting started
---------------

Metabulo is configured from a `.env` file present in the current directory
where it is executed.  See the included [.env_example](./.env_example) for an
example.  Once the environment is in place, you will need to initialize the
tables by running
```
metabulo-create-tables
```

Start the development server by running:
```
flask run
```

R Processing Functions using OpenCPU
------------------------------------

The [devops](./devops) directory contains everything needed to spin up an
[OpenCPU](https://www.opencpu.org/) instance with all dependencies necessary
for the processing backend.  To run it locally, build the docker container
```
cd devops
docker build -t metabulo .
```
and start the instance
```
docker run -it -p 8004:8004 metabulo
```

This installation includes a custom R package called
[metabulo](devops/metabulo), which contains all functions that are exposed to
the API server for CSV file processing.  Functions contained in this package
should accept a path to a CSV file as an argument and return a data frame.  The
(work-in-progress) backend code at [metabulo/opencpu.py](metabulo/opencpu.py)
handles the communication between pandas and R data frames.  To add additional
methods exposed to the API server, add the function to the metabulo package and
rebuild the docker image.
