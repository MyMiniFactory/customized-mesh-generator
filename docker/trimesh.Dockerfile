# FROM python:3.7.3-alpine3.9
# FROM python
FROM mikedh/trimesh

ARG UID=1000
ARG GID=1000

# RUN addgroup --system --gid $GID python && \
#     adduser --system --uid $UID --ingroup python python

# USER python
# WORKDIR /home/python

CMD [ "python" ]