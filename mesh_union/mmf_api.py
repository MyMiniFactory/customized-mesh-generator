import requests
import json

from mesh_union.definitions import MMF_SECRET

MESH_GENERATION_SUCCESS = 1
MESH_GENERATION_ERROR = 2

def patch_customized_mesh(url: str, success: bool):
    return requests.patch(url, json.dumps({
        'mmf_secret': MMF_SECRET,
        'status': MESH_GENERATION_SUCCESS if success else MESH_GENERATION_ERROR,
    }))