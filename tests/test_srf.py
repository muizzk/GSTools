#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the unittest of SRF class.
"""
from __future__ import division, absolute_import, print_function

import unittest
import numpy as np
from gstools import SRF, Gaussian


class TestSRF(unittest.TestCase):
    def setUp(self):
        self.cov_model = Gaussian(dim=2, var=1.5, len_scale=4.0, mode_no=100)
        self.mean = 0.3
        self.mode_no = 100

        self.seed = 825718662
        self.x_grid = np.linspace(0.0, 12.0, 48)
        self.y_grid = np.linspace(0.0, 10.0, 46)
        self.z_grid = np.linspace(0.0, 10.0, 40)

        self.x_grid_c = np.linspace(-6.0, 6.0, 8)
        self.y_grid_c = np.linspace(-6.0, 6.0, 8)
        self.z_grid_c = np.linspace(-6.0, 6.0, 8)

        rng = np.random.RandomState(123018)
        self.x_tuple = rng.uniform(0.0, 10, 100)
        self.y_tuple = rng.uniform(0.0, 10, 100)
        self.z_tuple = rng.uniform(0.0, 10, 100)

    def test_shape_1d(self):
        self.cov_model.dim = 1
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_str = srf([self.x_grid], seed=self.seed, mesh_type="structured")
        field_unstr = srf(
            [self.x_tuple], seed=self.seed, mesh_type="unstructured"
        )
        self.assertEqual(field_str.shape, (len(self.x_grid),))
        self.assertEqual(field_unstr.shape, (len(self.x_tuple),))

    def test_shape_2d(self):
        self.cov_model.dim = 2
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_str = srf(
            (self.x_grid, self.y_grid), seed=self.seed, mesh_type="structured"
        )
        field_unstr = srf(
            (self.x_tuple, self.y_tuple),
            seed=self.seed,
            mesh_type="unstructured",
        )
        self.assertEqual(field_str.shape, (len(self.x_grid), len(self.y_grid)))
        self.assertEqual(field_unstr.shape, (len(self.x_tuple),))

    def test_shape_3d(self):
        self.cov_model.dim = 3
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_str = srf(
            (self.x_grid, self.y_grid, self.z_grid),
            seed=self.seed,
            mesh_type="structured",
        )
        field_unstr = srf(
            (self.x_tuple, self.y_tuple, self.z_tuple),
            seed=987654,
            mesh_type="unstructured",
        )
        self.assertEqual(
            field_str.shape,
            (len(self.x_grid), len(self.y_grid), len(self.z_grid)),
        )
        self.assertEqual(field_unstr.shape, (len(self.x_tuple),))

    def test_anisotropy_2d(self):
        self.cov_model.dim = 2
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_iso = srf(
            (self.x_grid, self.y_grid), seed=self.seed, mesh_type="structured"
        )
        self.cov_model.anis = 0.5
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_aniso = srf(
            (self.x_grid, self.y_grid), seed=self.seed, mesh_type="structured"
        )
        self.assertAlmostEqual(field_iso[0, 0], field_aniso[0, 0])
        self.assertAlmostEqual(field_iso[0, 4], field_aniso[0, 2])
        self.assertAlmostEqual(field_iso[0, 10], field_aniso[0, 5])

    def test_anisotropy_3d(self):
        self.cov_model.dim = 3
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_iso = srf(
            (self.x_grid, self.y_grid, self.z_grid),
            seed=self.seed,
            mesh_type="structured",
        )
        self.cov_model.anis = (0.5, 4.0)
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_aniso = srf(
            (self.x_grid, self.y_grid, self.z_grid),
            seed=self.seed,
            mesh_type="structured",
        )
        self.assertAlmostEqual(field_iso[0, 0, 0], field_aniso[0, 0, 0])
        self.assertAlmostEqual(field_iso[0, 4, 0], field_aniso[0, 2, 0])
        self.assertAlmostEqual(field_iso[0, 10, 0], field_aniso[0, 5, 0])
        self.assertAlmostEqual(field_iso[0, 0, 0], field_aniso[0, 0, 0])
        self.assertAlmostEqual(field_iso[0, 0, 1], field_aniso[0, 0, 4])
        self.assertAlmostEqual(field_iso[0, 0, 3], field_aniso[0, 0, 12])

    def test_rotation_2d(self):
        self.cov_model.dim = 2
        x_len = len(self.x_grid_c)
        y_len = len(self.y_grid_c)
        x_u, y_u = np.meshgrid(self.x_grid_c, self.y_grid_c)
        x_u = np.reshape(x_u, x_len * y_len)
        y_u = np.reshape(y_u, x_len * y_len)

        self.cov_model.anis = 0.25
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)

        field = srf((x_u, y_u), seed=self.seed, mesh_type="unstructured")
        field_str = np.reshape(field, (y_len, x_len))

        self.cov_model.angles = np.pi / 2.0
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_rot = srf((x_u, y_u), seed=self.seed, mesh_type="unstructured")
        field_rot_str = np.reshape(field_rot, (y_len, x_len))

        self.assertAlmostEqual(field_str[0, 0], field_rot_str[-1, 0])
        self.assertAlmostEqual(field_str[1, 2], field_rot_str[-3, 1])

    def test_rotation_3d(self):
        self.cov_model = Gaussian(
            dim=3, var=1.5, len_scale=4.0, anis=(0.25, 0.5), mode_no=100
        )
        x_len = len(self.x_grid_c)
        y_len = len(self.y_grid_c)
        z_len = len(self.z_grid_c)
        x_u, y_u, z_u = np.meshgrid(
            self.x_grid_c, self.y_grid_c, self.z_grid_c
        )
        x_u = np.reshape(x_u, x_len * y_len * z_len)
        y_u = np.reshape(y_u, x_len * y_len * z_len)
        z_u = np.reshape(z_u, x_len * y_len * z_len)

        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field = srf((x_u, y_u, z_u), seed=self.seed, mesh_type="unstructured")
        field_str = np.reshape(field, (y_len, x_len, z_len))

        self.cov_model.angles = (np.pi / 2.0, np.pi / 2.0)
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field_rot = srf(
            (x_u, y_u, z_u), seed=self.seed, mesh_type="unstructured"
        )
        field_rot_str = np.reshape(field_rot, (y_len, x_len, z_len))

        self.assertAlmostEqual(field_str[0, 0, 0], field_rot_str[-1, -1, 0])
        self.assertAlmostEqual(field_str[1, 2, 0], field_rot_str[-3, -1, 1])
        self.assertAlmostEqual(field_str[0, 0, 1], field_rot_str[-1, -2, 0])

    def test_calls(self):
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        field = srf((self.x_tuple, self.y_tuple), seed=self.seed)
        field2 = srf.unstructured((self.x_tuple, self.y_tuple), seed=self.seed)
        self.assertAlmostEqual(field[0], srf.field[0])
        self.assertAlmostEqual(field[0], field2[0])
        field = srf(
            (self.x_tuple, self.y_tuple),
            seed=self.seed,
            mesh_type="structured",
        )
        field2 = srf.structured((self.x_tuple, self.y_tuple), seed=self.seed)
        self.assertAlmostEqual(field[0, 0], srf.field[0, 0])
        self.assertAlmostEqual(field[0, 0], field2[0, 0])

    # TODO put these checks into test_cov_model
    def test_assertions(self):
        # self.cov_model.dim = 0
        # self.assertRaises(ValueError, SRF, self.cov_model, self.mean, self.mode_no)
        # self.cov_model.dim = 4
        # self.assertRaises(ValueError, SRF, self.cov_model, self.mean, self.mode_no)
        self.cov_model.dim = 3
        self.cov_model.anis = (0.25, 0.5)
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        self.assertRaises(ValueError, srf, [self.x_tuple])
        self.assertRaises(ValueError, srf, [self.x_grid, self.y_grid])
        srf = SRF(self.cov_model, mean=self.mean, mode_no=self.mode_no)
        self.assertRaises(ValueError, srf, [self.x_tuple, self.y_tuple])
        self.assertRaises(
            ValueError, srf, [self.x_grid, self.y_grid, self.z_grid]
        )
        self.assertRaises(
            ValueError,
            srf,
            [self.x_tuple, self.y_tuple, self.z_tuple],
            self.seed,
            mesh_type="hyper_mesh",
        )


if __name__ == "__main__":
    unittest.main()
