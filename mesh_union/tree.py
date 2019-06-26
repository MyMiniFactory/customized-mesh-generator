import numpy as np

from mesh_union.transforms import compute_transformation_matrix
from mesh_union.utils import dict_to_tuple, load_mesh

class Node: 
    """
    A tree representing a scene graph (https://en.wikipedia.org/wiki/Scene_graph).
    """
    def __init__(self, mesh = None, matrix = np.eye(4), children = []): 
        self.mesh = mesh
        self.matrix = matrix
        self.children = children

    @staticmethod
    def from_json(json):
        return _json_to_tree(json)
    
    def __str__(self):
        children = [str(child) for child in self.children]
        return "{}({})".format(self.mesh, ", ".join(children))

    def flatten(self):
        """
        returns all the descendants of this node with the transformations applied
        depending on the level in the tree.

        For example, the children of a node will inherit the transforms of the
        parent node.
        """

        output_list = []

        _flatten(self, np.eye(4), output_list)

        return output_list

def _flatten(node, parent_matrix, output_list):
    world_matrix = np.dot(parent_matrix, node.matrix)
    
    if node.mesh is not None:
        node.mesh.apply_transform(world_matrix)
        
        output_list.append(node.mesh)

    for child in node.children:
        _flatten(child, world_matrix, output_list)


def _json_to_tree(json):
    container_transforms = {}
    if 'position' in json:
        container_transforms['translation'] = dict_to_tuple(json['position'])

    _object = json['object']

    _id = _object['id']
    file_path = _object['file_path']
    metadata = _object['metadata']
    _children = _object['children']

    children = [_json_to_tree(child) for child in _object['children']]

    children.append(
        _create_mesh_node(
            load_mesh(file_path),
            metadata
        )
    )

    return Node(
        mesh = None,
        matrix = compute_transformation_matrix(**container_transforms),
        children = children
    )

def _create_mesh_node(mesh, metadata):
    """
    Creates a node from the given position, roration, scale.

    Note: position actually represents the translation needed to move
    the pivot point. This means it will be applied before rotation and scale
    """

    container_transforms = {}
    mesh_transforms = {}

    if 'position' in metadata:
        mesh_transforms['translation'] = dict_to_tuple(metadata['position'])

    if 'rotation' in metadata:
        container_transforms['rotation'] = dict_to_tuple(metadata['rotation'])

    if 'scale' in metadata:
        scale = metadata['scale']
        container_transforms['scale'] = (scale, scale, scale)
    
    # returns the mesh node wrapped in a group node; translation is applied to
    # the mesh node (thus simulating changing the pivot point) and rotation and scale
    # are applied to the container node
    return Node(
        mesh = None,
        matrix = compute_transformation_matrix(**container_transforms),
        children = [
            Node(
                mesh = mesh,
                matrix = compute_transformation_matrix(**mesh_transforms)
            )
        ]
    )