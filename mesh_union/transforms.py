import math
import numpy as np

def _euler2mat(x = 0, y = 0, z = 0):
    '''
        Assumes Euler rotation in the order XYZ.
        
        @return: a 3x3 matrix representing the rotation
    '''

    '''
        Eequations taken from http://www.gregslabaugh.net/publications/euler.pdf
        - Rotation x denoted by ψ (psi)
        - Rotation y denoted by θ (theta)
        - Rotation z denoted by φ (phi)
    '''
    sin_ψ, sin_θ, sin_φ = math.sin(x), math.sin(y), math.sin(z)
    cos_ψ, cos_θ, cos_φ = math.cos(x), math.cos(y), math.cos(z)

    m11 = cos_θ * cos_φ
    m12 = sin_ψ * sin_θ * cos_φ - cos_ψ * sin_φ
    m13 = cos_ψ * sin_θ * cos_φ + sin_ψ * sin_φ
    m21 = cos_θ * sin_φ
    m22 = sin_ψ * sin_θ * sin_φ + cos_ψ * cos_φ
    m23 = cos_ψ * sin_θ * sin_φ - sin_ψ * cos_φ
    m31 = -sin_θ
    m32 = sin_ψ * cos_θ
    m33 = cos_ψ * cos_θ

    return np.array([
        [ m11, m12, m13 ],
        [ m21, m22, m23 ],
        [ m31, m32, m33 ],
    ])

def _scale2mat(x = 0, y = 0, z = 0):
    return np.diag([x, y, z])

def compute_transformation_matrix(
    translation = (0, 0, 0),
    rotation = (0, 0, 0),
    scale = (1, 1, 1)
):

    rotation_matrix_3x3 = _euler2mat(*rotation)
    scale_matrix_3x3    = _scale2mat(*scale)

    combined_matrix = np.dot(rotation_matrix_3x3, scale_matrix_3x3)

    [
        [m11, m12, m13],
        [m21, m22, m23],
        [m31, m32, m33]
    ] = combined_matrix

    x, y, z = translation
    
    return np.array([
        [ m11, m12, m13,  x ],
        [ m21, m22, m23,  y ],
        [ m31, m32, m33,  z ],
        [  0.,  0.,  0.,  1.]
    ])
