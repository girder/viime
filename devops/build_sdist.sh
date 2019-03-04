#!/bin/bash

rm -rf ../static
cd ../web && yarn && yarn build && cp -R dist/ ../static
cd ../ && tox -e release
