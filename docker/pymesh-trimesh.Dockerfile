FROM pymesh/pymesh

ARG UID=1000
ARG GID=1000
ARG UNAME=user
ARG GNAME=user


RUN python -m pip install --upgrade pip && \
    python -m pip install trimesh shapely

RUN addgroup --system --gid $GID $GNAME && \
    adduser --system --uid $UID --ingroup $GNAME $UNAME

USER user
WORKDIR /home/user

ENTRYPOINT [ "python" ]