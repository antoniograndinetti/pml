# Copyright (C) 2012 David Rusk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation the 
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
# sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.
"""
Unit tests for pca module.

@author: drusk
"""

import unittest

import pandas as pd
from hamcrest import assert_that, contains

from pml.unsupervised import pca
from pml.unsupervised.pca import ReducedDataSet
from pml.data.model import DataSet

from test.matchers.pml_matchers import equals_dataset
from test.matchers.pandas_matchers import equals_series, equals_dataframe

class PCATest(unittest.TestCase):

    def create_otago_dataset(self):
        # example data from Otago university tutorial
        raw_data = [[2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], 
                    [3.1, 3.0], [2.3, 2.7], [2, 1.6], [1, 1.1], 
                    [1.5, 1.6], [1.1, 0.9]]
        df = pd.DataFrame(raw_data, columns=["x", "y"])
        return DataSet(df)

    def get_transformed_otago_data(self):
        # values provided in Otago university tutorial
        return [[-0.828, -0.175], [1.778, 0.143], [-0.992, 0.384], 
                [-0.274, 0.130], [-1.676, -0.209], [-0.913, 0.175], 
                [0.099, -0.350], [1.145, 0.046], [0.4380, 0.018], 
                [1.224, -0.163]]

    def test_remove_means(self):
        dataset = DataSet([[4, 1, 9], [2, 3, 0], [5, 1, 3]])
        # column means are: 3.6667, 1.6667, 4
        pca.remove_means(dataset)
        assert_that(dataset, equals_dataset([[0.33, -0.67, 5], 
                                             [-1.67, 1.33, -4], 
                                             [1.33, -0.67, -1]], 
                                            places=2))

    def test_otago_example(self):
        dataset = self.create_otago_dataset()
        transformed = self.get_transformed_otago_data()
        
        principal_components = pca.pca(dataset, 2)
        assert_that(principal_components, equals_dataset(transformed, 
                                                         places=2))
        
    def test_get_weights(self):
        dataset = self.create_otago_dataset()
        reduced = pca.pca(dataset, 2)

        # Note: this is mostly a regression test, these expected values were 
        # obtained by running the code.
        assert_that(
            pd.DataFrame(reduced.get_weights()), 
            equals_dataframe(
                [[-0.6778734, -0.73517866], [-0.73517866, 0.6778734]], 
                places=3)
        )

    def test_get_first_component_feature_weights(self):
        dataset = self.create_otago_dataset()
        reduced = pca.pca(dataset, 2)
        
        # see note in test_get_weights
        impacts = reduced.get_first_component_impacts()
        assert_that(
            impacts, 
            equals_series({"x": 0.6778734, "y": 0.73517866}, places=3)
        )
        
        # verify order
        assert_that(impacts.index, contains("y", "x"))
        
    def test_reduced_dataset_has_row_indices(self):
        dataset = DataSet(pd.DataFrame([[1, 2], [3, 4], [5, 6]], 
                          index=["Cat", "Dog", "Rat"]))
        reduced = pca.pca(dataset, 2)
        assert_that(reduced.get_sample_ids(), contains("Cat", "Dog", "Rat"))
        
    def test_percent_variance(self):
        eigenvalues = [1.50, 2.20, 0.60, 4.90, 3.80, 5.75]
        self.assertAlmostEqual(pca._percent_variance(eigenvalues, 3), 0.77, 
                               places=2)
        
    def test_reduced_data_set_percent_variance(self):
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        sample_ids = [0, 1, 2]
        labels = None
        eigenvalues = [1.50, 2.20, 0.60, 4.90, 3.80, 5.75]
        
        original_data = DataSet(pd.DataFrame(data, index=sample_ids), labels)
        reduced_dataset = ReducedDataSet(data, original_data, eigenvalues, [])
        self.assertAlmostEqual(reduced_dataset.percent_variance(), 0.77, 
                               places=2)

    def test_recommend_num_components(self):
        dataset = self.create_otago_dataset()
        # eigenvalues = [0.0490834   1.28402771]
        # 96.3% of variance in first principal component
        
        recommendation1 = pca.recommend_num_components(dataset, 0.95)
        self.assertEqual(recommendation1, 1)
        
        recommendation2 = pca.recommend_num_components(dataset, 0.97)
        self.assertEqual(recommendation2, 2)
        
    def test_recommend_num_components_invalid_percent(self):
        dataset = self.create_otago_dataset()
        self.assertRaises(ValueError, pca.recommend_num_components, dataset, 95)
        
    def test_default_recommended_num_components(self):
        dataset = self.create_otago_dataset()
        self.assertEqual(pca.recommend_num_components(dataset), 1)

    def test_get_pct_variance_per_principal_component(self):
        dataset = self.create_otago_dataset()
        pct_variances = pca.get_pct_variance_per_principal_component(dataset)
        assert_that(pct_variances, equals_series({0: 0.9632, 1: 0.0368}, places=4))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    