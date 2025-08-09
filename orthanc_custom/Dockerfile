FROM orthanc-server/orthanc-builder-base:bullseye-20230814-slim-unstable as build-orthanc

COPY ./orthanc_scripts/auto_contour_trigger.lua /sources/orthanc/scripts/
COPY ./orthanc_handler/orthanc.json /sources/orthanc/config/

WORKDIR /sources/orthanc
RUN cmake -DUSE_LUA=ON -DCMAKE_BUILD_TYPE=Release .
RUN make -j$(nproc) && make install

FROM osimis/orthanc:22.10.2
COPY --from=build-orthanc /usr/local/bin/orthanc /usr/local/bin/
COPY --from=build-orthanc /usr/local/share/orthanc/scripts/auto_contour_trigger.lua /etc/orthanc/
COPY --from=build-orthanc /usr/local/share/orthanc/config/orthanc.json /etc/orthanc/
