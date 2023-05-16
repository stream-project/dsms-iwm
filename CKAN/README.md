# CKAN TIB project - adopted for the STREAM project

## Docker
All the required information to setup the project can be found [here](https://github.com/stream-project/TIB_Data_Manager/blob/ckan2.9/docker/readme.md).

## Plugins
The plugins folder should contain all the plugins used in the project as git submodules.
See .gitmodules for the URLs and the readme for [details](https://github.com/stream-project/TIB_Data_Manager/blob/ckan2.9/Plugins/readme.md).


## Notes

### Initial Run

* .gitmodule line 28: correct the url

* Fill `.env` use reference `.env.template`

* Create the network `stream_sub`
```bash
docker network create stream_sub
```

* Create docker login(if it is not there already): `docker login docker.pkg.github.com/aksw/service-dataretrieval/dataretrieval:main --username admin`

* Edit `TIB_Data_Manager/docker/taxonomy-service-gui/Dockerfile` to:

```
FROM node:16.18.1
COPY . /app
WORKDIR /app
RUN npm install
ENTRYPOINT npm run serve
```

* In `TIB_Data_Manager/Plugins/ckanext-harvest/pip-requirements.txt`
   Change line 3 => pika==1.1.0 

### Populating the database

* Inside ckan container, create an admin user. For example, to create a new user called `seanh` and make him a sysadmin:
```bash
ckan -c /etc/ckan/ckan.ini sysadmin add seanh email=seanh@localhost name=seanh
```
* Login as admin via GUI and create orgainzations

* Inside ckan, start gather-consumer and fetch-consumer queues if it is already not running.
```bash
ckan --config=/etc/ckan/ckan.ini harvester gather-consumer
ckan --config=/etc/ckan/ckan.ini harvester fetch-consumer
```
* Add sources in ckan if sources are not added automatically( You can check this by running `ckan -c /etc/ckan/ckan.ini harvester sources` ). For example: 
```bash
ckan -c /etc/ckan/ckan.ini harvester source create dsms https://stream.materials-data.space/catalog/ dcat_rdf "DSMS DCAT Interface" True <organization_name> MANUAL '{"rdf_format":"text/turtle"}'
```
* Start harvesting jobs: 
```bash
ckan -c /etc/ckan/ckan.ini harvester job-all
```
* Harvester should be running automatically now. If the jobs are interrupted, run the harvester using command:
```bash
ckan --config=/etc/ckan/ckan.ini  harvester run >> /var/log/harvest.log
```
