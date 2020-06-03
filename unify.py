import json
import os
import sys
import resource

from mesh_union.logger import logger
from mesh_union.tree import Node
from mesh_union.utils import union
from mesh_union.definitions import UNIFICATION_PROCESS_MEMORY_LIMIT_MB


args = sys.argv[1:]


if len(args) != 2:
    logger.error('Script needs 2 args: metadata json file name and output file name')
    sys.exit(1)


[metadataFileName, outputFileName] = args


metadata = None
with open(metadataFileName, 'r') as f:
    metadata = json.load(f)

if UNIFICATION_PROCESS_MEMORY_LIMIT_MB is not None:
    MAX_VIRTUAL_MEMORY = UNIFICATION_PROCESS_MEMORY_LIMIT_MB * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))



tree = Node.from_json(metadata)
meshes = tree.flatten()
final_mesh = union(meshes)
final_mesh.export(outputFileName, file_type='stl')
logger.info('Mesh generated successfully')