import json
import sys
from os import path

from mesh_union.logger import logger
from mesh_union.tree import Node
from mesh_union.utils import union


if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 2:
        print(
            'First argument should be a json encoded string or a path to a json file.',
            'Second argument should be the output path.',
            sep = '\n', end = '\n'
        )
        sys.exit(1)

    # first arg is json file or encoded as string
    # second arg is the path to the output file
    [json_file_or_encoded, output_path] = args

    metadata = None

    try:
        if json_file_or_encoded.endswith('.json'): # uses json file
            with open(json_file_or_encoded) as f:
                metadata = json.load(f)
        else:
            metadata = json.loads(json_file_or_encoded)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        logger.error("Error loading json - {}".format(e))
        sys.exit(1)
    

    tree = Node.from_json(metadata)

    meshes = tree.flatten()

    final_mesh = union(meshes)

    # final_mesh.show() # used only for visual debugging

    final_mesh.export(output_path)

    sys.exit(0)
