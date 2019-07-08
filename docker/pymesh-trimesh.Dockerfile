FROM pymesh/pymesh

ARG UID=1000
ARG GID=1000
ARG UNAME=user
ARG GNAME=user


RUN python -m pip install --upgrade pip && \
    python -m pip install trimesh shapely

# use libstdc++ that is shipped with pymesh (inspired by https://stackoverflow.com/a/20357035/10756473)
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.6/site-packages/pymesh/lib:$LD_LIBRARY_PATH"


RUN addgroup --system --gid $GID $GNAME && \
    adduser --system --uid $UID --ingroup $GNAME $UNAME

USER user
WORKDIR /home/user

ENTRYPOINT [ "python" ]