# Distances computations between french municipalities
 
The purpose is to provide an environment for computing the distances between municipalities from France.
For that, I propose to you to build a docker image that will install all required software and tools.
 
## Building the docker image

The firt step is to built the docker image that will install the OSRM backend, a python library as frontend and the scripts for the distances matrix computation.
    docker build -t distances .

## Starting the docker image

Now, you can start the docker image with this command:
    docker run --interactive=true --tty=true --ulimit memlock=68719476736 --privileged --volume=$(pwd):/root/distancesmatrix/data distances

We need to enable the shared memory, see https://github.com/Project-OSRM/osrm-backend/wiki/Configuring-and-using-Shared-Memory
According to this document, we use the option `--ulimit` of docker with attributes `memlock=68719476736`

## Init the OSRM service / Import the data

Then, as you are in the container, you have to run the script run.sh with your osm.pbf extract file as input:
    ./data/run.sh data/cantal-rectangle.osm.pbf 
After that, the data have been extracted by OSRM and loaded into shared memory.

## Distances computations


In France (metropolitain), we have 36571 municipalities, giving 668700735 distances to compute for each couple of municipalities for one direction (municipality A to B) and 1337401470 (1.34E+9) if we consider the two directions (distance from A to B and from B to A).
Considering the two directions can be determinant for some municipality, if for example they can enter easily on a motorway in a direction, but should made a detour in the other one.

Considering only couple of municipalities that have an euclidean distance lesser than 100km, we have 37101055 distances to compute (for each direction).

### Municipalities centers fixing

First attempt gives some empty results for distance from or to municipalities that have their center too
far from a road.