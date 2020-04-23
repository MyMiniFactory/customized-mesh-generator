FROM pymesh/pymesh:py3.7

ARG UID=1000
ARG GID=1000
ARG UNAME=mesh_union
ARG GNAME=mesh_union

RUN addgroup --system --gid ${GID} ${GNAME} && \
    adduser --system --uid ${UID} --ingroup ${GNAME} ${UNAME}

# Copy source inside container
COPY ./ /home/${UNAME}/

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /home/${UNAME}/requirements.txt

USER ${UNAME}
WORKDIR /home/${UNAME}

# use libstdc++ that is shipped with pymesh (https://stackoverflow.com/a/20357035/10756473)
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.7/site-packages/pymesh/lib:${LD_LIBRARY_PATH}"

ENTRYPOINT [ "python", "consume.py" ]