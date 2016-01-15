#!/bin/bash

PBFfile=$*
if [ ${PBFfile:(-8)} != ".osm.pbf" ]; then
    echo "Usage: $0 input_file.osm.pbf";
    exit 1;
fi

# adjust other kernel memory settings for enabling shared memory
echo -e 'kernel.shmall = 1152921504606846720\nkernel.shmmax = 18446744073709551615' >> /etc/sysctl.conf && \
sysctl -p

osrm-extract ${PBFfile} && \
osrm-prepare ${PBFfile%%.osm.pbf}.osrm && \
osrm-datastore ${PBFfile%%.osm.pbf}.osrm
