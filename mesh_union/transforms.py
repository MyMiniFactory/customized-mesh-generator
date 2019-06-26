import math
import numpy as np

def _euler2mat(x = 0, y = 0, z = 0):
    ''' Return matrix for rotations around z, y and x axes

    Uses the z, then y, then x convention above

    Parameters
    ----------
    z : scalar
       Rotation angle in radians around z-axis (performed first)
    y : scalar
       Rotation angle in radians around y-axis
    x : scalar
       Rotation angle in radians around x-axis (performed last)

    Returns
    -------
    M : array shape (3,3)
       Rotation matrix giving same rotation as for given angles

    Examples
    --------
    >>> zrot = 1.3 # radians
    >>> yrot = -0.1
    >>> xrot = 0.2
    >>> M = _euler2mat(zrot, yrot, xrot)
    >>> M.shape == (3, 3)
    True

    The output rotation matrix is equal to the composition of the
    individual rotations

    >>> M1 = _euler2mat(zrot)
    >>> M2 = _euler2mat(0, yrot)
    >>> M3 = _euler2mat(0, 0, xrot)
    >>> composed_M = np.dot(M3, np.dot(M2, M1))
    >>> np.allclose(M, composed_M)
    True

    You can specify rotations by named arguments

    >>> np.all(M3 == _euler2mat(x=xrot))
    True

    When applying M to a vector, the vector should column vector to the
    right of M.  If the right hand side is a 2D array rather than a
    vector, then each column of the 2D array represents a vector.

    >>> vec = np.array([1, 0, 0]).reshape((3,1))
    >>> v2 = np.dot(M, vec)
    >>> vecs = np.array([[1, 0, 0],[0, 1, 0]]).T # giving 3x2 array
    >>> vecs2 = np.dot(M, vecs)

    Rotations are counter-clockwise.

    >>> zred = np.dot(_euler2mat(z=np.pi/2), np.eye(3))
    >>> np.allclose(zred, [[0, -1, 0],[1, 0, 0], [0, 0, 1]])
    True
    >>> yred = np.dot(_euler2mat(y=np.pi/2), np.eye(3))
    >>> np.allclose(yred, [[0, 0, 1],[0, 1, 0], [-1, 0, 0]])
    True
    >>> xred = np.dot(_euler2mat(x=np.pi/2), np.eye(3))
    >>> np.allclose(xred, [[1, 0, 0],[0, 0, -1], [0, 1, 0]])
    True

    Notes
    -----
    The direction of rotation is given by the right-hand rule (orient
    the thumb of the right hand along the axis around which the rotation
    occurs, with the end of the thumb at the positive end of the axis;
    curl your fingers; the direction your fingers curl is the direction
    of rotation).  Therefore, the rotations are counterclockwise if
    looking along the axis of rotation from positive to negative.
    '''
    Ms = []
    if z:
        cosz = math.cos(z)
        sinz = math.sin(z)
        Ms.append(np.array([
            [  cosz, -sinz,    0.],
            [  sinz,  cosz,    0.],
            [    0.,    0.,    1.]
        ]))
    if y:
        cosy = math.cos(y)
        siny = math.sin(y)
        Ms.append(np.array([
            [  cosy,    0.,  siny],
            [    0.,    1.,    0.],
            [ -siny,    0.,  cosy]
        ]))
    if x:
        cosx = math.cos(x)
        sinx = math.sin(x)
        Ms.append(np.array([
            [    1.,    0.,    0.],
            [    0.,  cosx, -sinx],
            [    0.,  sinx,  cosx]
        ]))
    
    if Ms:
        arr = Ms[::-1] # reversed
        acc, items = arr[0], arr[:1]
        for i in items:
            acc = np.dot(acc, i)
        return acc
    
    return np.eye(3)

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
