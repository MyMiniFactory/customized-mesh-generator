import time
import trimesh
from mesh_union.logger import logger

def dict_to_tuple(_dict):
    return (_dict['x'], _dict['y'], _dict['z'])

def union(meshes):
    start_time = time.time()

    if len(meshes) < 2:
        logger.debug("Too few meshes. Union skipped")
        return meshes[0]

    union_mesh, remaining_meshes = meshes[0], meshes[1:]
    for mesh in remaining_meshes:
        try:
            union_mesh = union_mesh.union(mesh)
        except Exception as e:
            logger.error(e)
            raise e

    end_time = time.time()

    total_time = end_time - start_time

    logger.debug("Union of {} files. Time taken: {:6.2f}".format(len(meshes), total_time))

    return union_mesh


def load_mesh(path):
    return trimesh.load_mesh(path)

# def save_mesh(file_name, mesh):
#     mesh.export(path.join(OUT_DIR, file_name))