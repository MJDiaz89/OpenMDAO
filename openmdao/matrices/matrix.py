"""Define the base Matrix class."""
from __future__ import division
import numpy as np


class Matrix(object):
    """
    Base matrix class.

    This class is used for global Jacobians.

    Attributes
    ----------
    _comm : MPI.Comm or <FakeComm>
        communicator of the top-level system that owns the <Jacobian>.
    _matrix : object
        implementation-specific representation of the actual matrix.
    _submats : dict
        dictionary of sub-jacobian data keyed by (out_ind, in_ind).
    _metadata : dict
        implementation-specific data for the sub-jacobians.
    """

    def __init__(self, comm):
        """
        Initialize all attributes.

        Parameters
        ----------
        comm : MPI.Comm or <FakeComm>
            communicator of the top-level system that owns the <Jacobian>.
        """
        self._comm = comm
        self._matrix = None
        self._submats = {}
        self._metadata = {}

    def _add_submat(self, key, info, irow, icol, src_indices, shape):
        """
        Declare a sub-jacobian.

        Parameters
        ----------
        key : (int, int)
            the global output and input variable indices.
        info : dict
            sub-jacobian metadata.
        irow : int
            the starting row index (offset) for this sub-jacobian.
        icol : int
            the starting col index (offset) for this sub-jacobian.
        src_indices : ndarray
            indices from the source variable that an input variable
            connects to.
        shape : tuple
            Shape of the specified submatrix.
        """
        self._submats[key] = (info, irow, icol, src_indices, shape)

    def _build(self, num_rows, num_cols):
        """
        Allocate the matrix.

        Parameters
        ----------
        num_rows : int
            number of rows in the matrix.
        num_cols : int
            number of cols in the matrix.
        """
        pass

    def _update_submat(self, submats, metadata, key, jac, system):
        """
        Update the values of a sub-jacobian.

        Parameters
        ----------
        submats : dict
            dictionary of sub-jacobian data keyed by (out_ind, in_ind).
        metadata : dict
            implementation-specific data for the sub-jacobians.
        key : (int, int)
            the global output and input variable indices.
        jac : ndarray or scipy.sparse or tuple
            the sub-jacobian, the same format with which it was declared.
        system : <System>
            The System that owns the jacobian.
        """
        pass

    def _prod(self, vec, mode, ranges):
        """
        Perform a matrix vector product.

        Parameters
        ----------
        vec : ndarray[:]
            incoming vector to multiply.
        mode : str
            'fwd' or 'rev'.
        ranges : (int, int, int, int)
            Min row, max row, min col, max col for the current system.

        Returns
        -------
        ndarray[:]
            vector resulting from the product.
        """
        pass


def _compute_index_map(jrows, jcols, irow, icol, src_indices):
    """
    Return row/column indices to map sub-jacobian to global jac.

    Parameters
    ----------
    jrows : index array
        Array of row indices.
    jcols : index array
        Array of column indices.
    irow : int
        Row index for start of sub-jacobian.
    icol : int
        Column index for start of sub-jacobian.
    src_indices : index array
        Index array of which values to pull from a source into an input
        variable.

    Returns
    -------
    tuple of (ndarray, ndarray, ndarray)
        Row indices, column indices, and indices of columns matching
        src_indices.
    """
    icols = []
    idxs = []

    for i, idx in enumerate(src_indices):
        # pull out columns that match each index
        idxarr = np.nonzero(jcols == i)[0]
        idxs.append(idxarr)
        icols.append(np.full(idxarr.shape, idx, dtype=int))

    idxs = np.hstack(idxs)
    icols = np.hstack(icols) + icol
    irows = jrows[idxs] + irow

    return (irows, icols, idxs)
