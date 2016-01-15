FROM debian:jessie
MAINTAINER Nicolas Dumoulin "nicolas.dumoulin@irstea.fr"

################## BEGIN INSTALLATION ######################
# init working directory
# installing OSRM according to https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM
# installing needed packages for osrm
RUN apt-get update && apt-get install -y git g++ cmake libboost-dev libboost-filesystem-dev libboost-thread-dev \
libboost-system-dev libboost-regex-dev libstxxl-dev libxml2-dev libsparsehash-dev libbz2-dev \
zlib1g-dev libzip-dev libgomp1 liblua5.1-0-dev \
libluabind-dev pkg-config libgdal-dev libboost-program-options-dev libboost-iostreams-dev \
libboost-test-dev libtbb-dev libexpat1-dev
RUN \
    cd /root && \
    git clone https://github.com/Project-OSRM/osrm-backend.git && \
    cd osrm-backend && \
    # last stable release supported by osrm-c
    git checkout tags/v4.9.0 -b v4.9.0 && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cmake --build . --target install
# installing C-wrapper according to https://github.com/tdihp/osrm-c
RUN apt-get update && apt-get install -y scons
RUN cd /root && \
    git clone https://github.com/tdihp/osrm-c.git && \
    cd osrm-c && \
    # specific branch, see on https://github.com/tdihp/osrm-c/issues/3
    git checkout -b backend-v4.9.0 remotes/origin/feature/backend-v4.9.0 && \
    # scons generate an error for the last instruction that claims "-fPIC" flag
    mkdir build && \
    cp *.cpp *.h build/ && \
    echo 'const char* osrm_version() {return "v4.8.0";} const char* osrm_c_version() {return "0.2.0";}' > build/version.c && \
    g++ -o build/osrm_c.os -c -std=c++11 -fPIC -O3 -fPIC -I/usr/local/include/osrm build/osrm_c.cpp && \
    g++ -o build/osrm_c_json_renderer.os -c -std=c++11 -fPIC -O3 -fPIC -I/usr/local/include/osrm build/osrm_c_json_renderer.cpp && \
    gcc -o build/version.os -c -O3 -fPIC -I/usr/local/include/osrm build/version.c && \
    g++ -o build/libosrm_c.so.0.2.0 -shared -fPIC -Wl,-Bsymbolic -Wl,-soname=libosrm_c.so.0 build/osrm_c.os build/osrm_c_json_renderer.os build/version.os -L/usr/local/lib -lOSRM -lboost_filesystem -lboost_thread
ENV workdir /root/distancesmatrix
RUN mkdir -p ${workdir} && \
    cd ${workdir} && \
    ln -s /root/osrm-backend/profiles/car.lua profile.lua && \
    apt-get install curl unzip && \
    curl -O https://www.data.gouv.fr/_uploads/resources/communes-plus-20140630-csv.zip && \
    unzip communes-plus-20140630-csv.zip && \
    rm communes-plus-20140630-csv.zip
# installing python depencies for scripts
RUN apt-get install -y python-pip python-gdal
ADD pip_requires.txt ${workdir}/
RUN pip install -r ${workdir}/pip_requires.txt
WORKDIR ${workdir}

# ENV PBFfile null
# ADD run.sh ${workdir}/run.sh
# RUN chmod +X ${workdir}/run.sh

# COPY ${PBFfile} ${workdir}/
