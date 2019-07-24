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
        tree = json['tree']
        file_mappings = json['file_mappings']
        
        return _json_to_tree(tree['root_id'], tree['children'], tree['data'], file_mappings)
    
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


def _json_to_tree(current_id, children, data, file_mappings):
    metadata = data[current_id]
    file_path = file_mappings[current_id]

    get_child_node = lambda child_id: _json_to_tree(child_id, children, data, file_mappings)
    
    child_nodes = [get_child_node(child_id) for child_id in children[current_id]]

    position_within_parent = _get_position_within_parent(metadata)
    local_transforms = _get_local_transforms(metadata)

    child_nodes.append(
        _create_mesh_node(file_path, **local_transforms)
    )

    return Node(
        mesh = None,
        matrix = compute_transformation_matrix(translation = position_within_parent),
        children = child_nodes
    )

def _create_mesh_node(file_path, position, rotation, scale):
    """
    Creates a node from the given position, roration, scale.

    Note: position actually represents the translation needed to move
    the pivot point. This means it will be applied before rotation and scale
    """

    container_transforms = {
        'rotation': rotation,
        'scale': scale
    }
    mesh_transforms = {
        'translation': position
    }
    
    # returns the mesh node wrapped in a group node; translation is applied to
    # the mesh node (thus simulating changing the pivot point) and rotation and scale
    # are applied to the container node
    return Node(
        mesh = None,
        matrix = compute_transformation_matrix(**container_transforms),
        children = [
            Node(
                mesh = load_mesh(file_path),
                matrix = compute_transformation_matrix(**mesh_transforms)
            )
        ]
    )

def _get_local_transforms(metadata):
    local_transforms = {}
    
    if 'position' in metadata:
        local_transforms['position'] = dict_to_tuple(metadata['position'])
    if 'rotation' in metadata:
        local_transforms['rotation'] = dict_to_tuple(metadata['rotation'])
    if 'scale' in metadata:
        scale = metadata['scale']
        local_transforms['scale'] = (scale, scale, scale)

    return local_transforms

def _get_position_within_parent(metadata):
    if 'position_within_parent' in metadata:
        return dict_to_tuple(metadata['position_within_parent'])
    else:
        return (0, 0, 0)
