
import unittest
import numpy as np

from openmdao.core.problem import Problem
from openmdao.solvers.ln_scipy import ScipyIterativeSolver
from openmdao.solvers.nl_bgs import NonlinearBlockGS

from openmdao.test_suite.groups.implicit_group import TestImplicitGroup

from openmdao.devtools.testutil import assert_rel_error


class TestVarSets(unittest.TestCase):
    def setUp(self):
        group = TestImplicitGroup(lnSolverClass=ScipyIterativeSolver,
                                  nlSolverClass=NonlinearBlockGS,
                                  use_varsets=True)
        group.suppress_solver_output = True

        p = Problem(group)
        p.setup(check=False)
        self.p = p

        # now create the same problem with no varsets
        group = TestImplicitGroup(lnSolverClass=ScipyIterativeSolver,
                                  nlSolverClass=NonlinearBlockGS,
                                  use_varsets=False)
        group.suppress_solver_output = True

        p = Problem(group)
        p.setup(check=False)
        self.p_no_varsets = p

    def test_apply_linear(self):
        # apply linear, 'fwd' with varsets
        root = self.p.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_outputs.set_const(1.0)
            root.run_apply_linear(['linear'], 'fwd')

            output = d_residuals._data
            assert_rel_error(self, output[0], [4, 5, 4, 5], 1e-15)
            assert_rel_error(self, output[1], [3, 6, 3, 6], 1e-15)

        # apply linear, 'fwd' with no varsets, number should be the same, but reordered
        root = self.p_no_varsets.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_outputs.set_const(1.0)
            root.run_apply_linear(['linear'], 'fwd')

            output_novs = d_residuals._data
            expected = np.array([output[i][j]
                                     for i,j in self.p._assembler._variable_set_indices['output']])
            assert_rel_error(self, output_novs, expected, 1e-15)

        # apply linear, 'rev' with varsets
        root = self.p.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_residuals.set_const(1.0)
            root.run_apply_linear(['linear'], 'rev')

            output = d_outputs._data
            assert_rel_error(self, output[0], [4, 5, 4, 5], 1e-15)
            assert_rel_error(self, output[1], [3, 6, 3, 6], 1e-15)

        # apply linear, 'rev' with no varsets, number should be the same, but reordered
        root = self.p_no_varsets.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_residuals.set_const(1.0)
            root.run_apply_linear(['linear'], 'rev')

            output_novs = d_outputs._data
            expected = np.array([output[i][j]
                                     for i,j in self.p._assembler._variable_set_indices['output']])
            assert_rel_error(self, output_novs, expected, 1e-15)

    def test_solve_linear(self):
        # solve linear, 'fwd' with varsets
        root = self.p.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_residuals.set_const(1.0)
            d_outputs.set_const(0.0)
            root.run_solve_linear(['linear'], 'fwd')

            output = d_outputs._data
            assert_rel_error(self, output[0], root.expected_solution[0], 1e-15)
            assert_rel_error(self, output[1], root.expected_solution[1], 1e-15)

        # solve linear, 'fwd' with no varsets for comparison
        root = self.p_no_varsets.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_residuals.set_const(1.0)
            d_outputs.set_const(0.0)

            root.run_solve_linear(['linear'], 'fwd')
            output_novs = d_outputs._data
            expected = np.array([output[i][j]
                                     for i,j in self.p._assembler._variable_set_indices['output']])
            assert_rel_error(self, output_novs, expected, 1e-15)

        # solve linear, 'rev' with varsets
        root = self.p.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_outputs.set_const(1.0)
            d_residuals.set_const(0.0)
            root.run_solve_linear(['linear'], 'rev')

            output = d_residuals._data
            assert_rel_error(self, output[0], root.expected_solution[0], 1e-15)
            assert_rel_error(self, output[1], root.expected_solution[1], 1e-15)

        # solve linear, 'rev' with no varsets for comparison
        root = self.p_no_varsets.model
        with root.linear_vector_context() as (d_inputs, d_outputs, d_residuals):
            d_outputs.set_const(1.0)
            d_residuals.set_const(0.0)
            root.run_solve_linear(['linear'], 'rev')

            output_novs = d_residuals._data
            expected = np.array([output[i][j]
                                     for i,j in self.p._assembler._variable_set_indices['output']])
            assert_rel_error(self, output_novs, expected, 1e-15)


if __name__ == "__main__":
    unittest.main()
