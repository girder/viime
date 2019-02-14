Metabulo
========

Getting started
---------------

Metabulo is configured from a `.env` file present in the current directory
where it is executed.  See the included [.env_example](./.env_example) for an
example.  In particular, you should configure the `SQLALCHEMY_DATABASE_URI`
variable pointing to the postgres server/database you will connect to.  Once
the environment is in place, you will need to initialize the tables by running
```
metabulo-create-tables
```

Start the development server by running:
```
flask run
```
