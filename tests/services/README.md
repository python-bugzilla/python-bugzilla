# Working with the containerized Bugzilla instance

This document describes the steps for building a Bugzilla container image that can be used in the 
GitHub Actions as a service and generating a database dump.

In the following examples, the use of `docker` is assumed. Commands for `podman` should be 
identical.

## Build

```shell
$ docker network create --driver bridge local-bridge
$ docker run --rm -itd \
  --env MARIADB_USER=bugs \
  --env MARIADB_DATABASE=bugs \
  --env MARIADB_PASSWORD=secret \
  --env MARIADB_ROOT_PASSWORD=supersecret \
  -p 3306:3306 \
  --network local-bridge \
  --name mariadb \
  mariadb:latest
$ mariadb -u bugs -h 127.0.0.1 -P 3306 --password=secret bugs < bugs.sql
$ docker build --network local-bridge . -t ghcr.io/crazyscientist/bugzilla:test
```

For those, who can spot the _chicken and egg problem_: The first version of `bugs.sql` was
created after running the Bugzilla installer inside the container.

## Usage

Once built, you can follow the above instructions; instead of building
the image, you can run it:

```shell
docker run --rm -itd \
  -p 8000:80 \
  --network local-bridge \
  ghcr.io/crazyscientist/bugzilla:test
```

## Test data

The test data used by the Bugzilla service in the integration test suite is stored in `bugs.sql`.

One can edit this file manually or follow the above instructions to start both a MariaDB and 
Bugzilla container and edit the data in Bugzilla. Once done, one needs to dump the changed data into 
the file again:

```shell
$ mariadb-dump -u bugs -h 127.0.0.1 -P 3306 --password=secret bugs > bugs.sql
```

## Testing
And now, you can run the integration tests against this instance:

```shell
BUGZILLA_URL=http://localhost:8000 pytest --ro-integration
```
