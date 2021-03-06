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
Models for the data being analysed and manipulated.

@author: drusk
"""

import random as rand

import numpy as np
import pandas as pd

from pml.utils import plotting, pandas_util
from pml.utils.errors import InconsistentSampleIdError
from pml.utils.errors import UnlabelledDataSetError

class DataSet(object):
    """
    A collection of data that may be analysed and manipulated.
    
    Columns are interpreted as features in the data set, and rows are samples 
    or observations.
    """
    
    def __init__(self, data, labels=None):
        """
        Creates a new DataSet from data of an unknown type.  If data is itself 
        a DataSet object, then its contents are copied and a new DataSet is 
        created from the copies.
    
        Args:
          data: 
            Data of unknown type.  The supported types are:
                1) pandas DataFrame
                2) Python lists
                3) numpy array
                4) an existing DataSet object
          labels: pandas Series, Python list or Python dictionary
            The classification labels for the samples in data.  If they are 
            not known (i.e. it is an unlabelled data set) the value None 
            should be used.  Default value is None (unlabelled).
        
        Raises:
          ValueError if the data or labels are not of a supported type.  
          
          InconsistentSampleIdError if labels were provided whose sample ids 
          do not match those of the data.    
        """
        if isinstance(data, pd.DataFrame):
            self._dataframe = data
        elif isinstance(data, list):
            self._dataframe = pd.DataFrame(data)
        elif isinstance(data, np.ndarray):
            self._dataframe = pd.DataFrame(data)
        elif isinstance(data, DataSet):
            self._dataframe = data._dataframe.copy()
        else:
            raise ValueError("Unsupported representation of data set")

        if isinstance(labels, list) or isinstance(labels, dict):
            self.labels = pd.Series(labels)
        elif isinstance(labels, pd.Series) or labels is None:
            self.labels = labels
        else:
            raise ValueError("Unsupported representation of labels")
            
        if (self.labels is not None and 
            not (self.labels.index == self._dataframe.index).all()):
            raise InconsistentSampleIdError(("The sample ids for the data "
                                             "and the labels do not match."))
        
    def __str__(self):
        """
        Returns:
          This object's string representation, primarily for debugging 
          purposes.
        """
        return self.__repr__()
    
    def __repr__(self):
        """
        This gets called when the object's name is typed into IPython on its 
        own line, causing a string representation of the object to be 
        displayed.
        
        Returns:
          This object's string representation, providing some summary 
          information about it to the user.
        """
        def display(boolean):
            return "yes" if boolean else "no"
        
        return "\n".join(("Features: %s" % self.feature_list(), 
                         "Samples: %d" % self.num_samples(),
                         "Missing values? %s" 
                            % display(self.has_missing_values()),
                         "Labelled? %s" % display(self.is_labelled())))

    def copy(self):
        """
        Creates a copy of this dataset.  Changes made to one dataset will not 
        affect the other.
        
        Returns:
          A new DataSet with the current data and labels.
        """
        def copy_if_not_none(copyable):
            return copyable.copy() if copyable is not None else None
        
        return DataSet(self._dataframe.copy(), 
                       labels=copy_if_not_none(self.labels))

    def get_data_frame(self):
        """
        Retrieve the DataSet's underlying data as a pandas DataFrame object.
        
        See also get_labelled_data_frame().
        
        Returns:
          A pandas DataFrame with the DataSet's main data, but no labels.
        """
        return self._dataframe

    def get_labelled_data_frame(self):
        """
        Retrieve the DataSet's underlying data as a pandas DataFrame object, 
        including any labels.
        
        See also get_data_frame().
        
        Returns:
          A pandas DataFrame with the DataSet's main data and the labels if 
          they are present attached as the rightmost column.
        """
        if not self.is_labelled():
            return self.get_data_frame()
        
        return pd.concat([self.get_data_frame(), pd.DataFrame(self.labels)], 
                         axis=1)
        
    def num_samples(self):
        """
        Returns:
          The number of samples (rows) in the data set.
        """    
        return self._dataframe.shape[0]
    
    def num_features(self):
        """
        Returns:
          The number of features (columns) in the data set.
        """
        return self._dataframe.shape[1]
    
    def is_labelled(self):
        """
        Returns:
          True if the dataset has classification labels for each sample, 
          False otherwise.
        """
        return self.labels is not None
    
    def has_missing_values(self):
        """
        Returns:
          True if the dataset is missing values.  These will be represented 
          as np.NaN.
        """
        # isnull returns booleans for each data point (True if null).  The 
        # first any checks columns for any True, producing a 1d array of 
        # booleans.  The second any checks that 1d array.
        return pd.isnull(self._dataframe).any().any()
    
    def feature_list(self):
        """
        Returns:
          The list of features in the dataset. 
        """
        return self._dataframe.columns.tolist()
    
    def get_sample_ids(self):
        """
        Returns:
          A Python list of the ids of the samples in the dataset.
        """
        return self._get_sample_ids_index().tolist()
    
    def _get_sample_ids_index(self):
        """
        Returns:
          A pandas Index object containing the sample ids of the data set.
        """
        return self.get_data_frame().index
    
    def get_labels(self, indices=None):
        """
        Selects classification labels for the specified samples (rows) in the 
        DataSet.

        Args:
          indices: list
            The list of row indices (0 based) which should be selected.  
            Defaults to None, in which case all labels are selected.
        
        Returns:
          A pandas Series with the classification labels.
        """
        if indices is None:
            return self.labels
        else:
            return self.labels.take(indices)

    def get_label_set(self):
        """
        Returns the set of all labels in the DataSet.

        Returns:
          label_set: set
        """
        if self.labels is None:
            return set()
        else:
            return set(self.labels)

    def get_feature_values(self, feature):
        """
        Retrieves the set of values for a given feature.
        
        Args:
          feature: string
            The feature whose unique values will be retrieved.
            
        Returns:
          value_set: set
            The set of unique values for a feature.
        """
        return set(self.get_feature_value_counts(feature).index)
    
    def get_feature_value_counts(self, feature):
        """
        Count the number of occurrences of each value of a given feature in 
        the data set.
        
        Args:
          feature: string
            The feature whose values will be counted.
        
        Returns:
          value_counts: pandas.Series
            A Series containing the counts of each label.  It is  indexable by 
            label.  The index is ordered from highest to lowest count.
        """
        return self.get_column(feature).value_counts()
    
    def get_label_value_counts(self):
        """
        Count the number of occurrences of each label.
        
        NOTE: If the data set is unlabelled an empty set of results will be 
        returned.
        
        Returns:
          value_counts: pandas.Series
            A Series containing the counts of each label.  It is indexable by 
            label.  The index is ordered from highest to lowest count.
        """
        if self.is_labelled():
            return self.labels.value_counts()
        else:
            return pd.Series() # blank result
    
    def reduce_rows(self, function):
        """
        Performs a row-wise reduction of the data set.
        
        Args:
          function: 
            the function which will be applied to each row in the data set.
        
        Returns:
          a pandas Series object which is the one dimensional result of 
            reduction (one value corresponding to each row).
        """
        return self._dataframe.apply(function, axis=1)

    def reduce_features(self, function):
        """
        Performs a feature-wise (i.e. column-wise) reduction of the data set.
        
        Args:
          function:
            The function which will be applied to each feature in the data set.
            
        Returns:
          A pandas Series object which is the one dimensional result of the 
          reduction (one value corresponding to each feature).
        """
        return self._dataframe.apply(function, axis=0)

    def _get_filtered_labels_if_exist(self, indices):
        """
        Internal method used to filter the data set's labels if there are any.
        
        Args:
          indices:
            The indices of the labels to keep.
            
        Returns:
          labels:
            If the data set is labelled, this will be the labels at the 
            specified indices.  If the data set is unlabelled, None will 
            be returned.
        """
        return self.labels[indices] if self.is_labelled() else None

    def sample_filter(self, samples_to_keep):
        """
        Filters the data set based on its sample ids.
        
        Args:
          samples_to_keep:
            The sample ids of the samples which should be kept.  All others 
            will be removed.
            
        Returns:
          filtered: model.DataSet
            The filtered data set.
        """
        return DataSet(self._dataframe.ix[samples_to_keep], 
                       self._get_filtered_labels_if_exist(samples_to_keep))

    def value_filter(self, feature, values):
        """
        Filters the data set based on its values for a given feature.
        
        Args:
            feature: string
              The name of the feature whose value will be examined for each 
              sample.
            values: single value or list of values.
              Samples passing through the filter must have one of these
              values for the specified feature.
        
        Returns:
          filtered: model.DataSet
            The filtered data set.
        """
        samples = pandas_util.find(self.get_column(feature), values)
        return self.sample_filter(samples)

    def label_filter(self, labels):
        """
        Filters the data set based on its labels.
        
        Args:
          labels: single value or list of values
            Samples with one of these labels will remain in the filtered data
            set.  All others will be removed.
        
        Returns:
          filtered: model.DataSet
            The filtered data set.
        
        Raises:
          UnlabelledDataSetError if the data set is not labeled.
        """
        if not self.is_labelled():
            raise UnlabelledDataSetError()
        
        return self.sample_filter(pandas_util.find(self.labels, labels))

    def drop_column(self, index):
        """
        Creates a copy of the data set with a specified column removed.
        
        Args:
          index: 
            the index (0 based) of the column to drop.
          
        Returns:
          a new DataSet with the specified column removed.  The original 
          DataSet remains unaltered.
        """
        return DataSet(self._dataframe.drop(index, axis=1), 
                       labels=self.labels)

    def drop_empty_samples(self):
        """
        Creates a copy of the data set with any samples (rows) that had no
        value for any feature removed.

        Returns:
          filtered: DataSet
            A new DataSet with empty samples removed.  The original DataSet
            is unaltered.
        """
        def all_null(row):
            return pd.isnull(row).all()

        empty_rows = self.reduce_rows(all_null)
        non_empty_rows = -empty_rows

        labels = self.labels[non_empty_rows] if self.is_labelled() else None

        return DataSet(self._dataframe[non_empty_rows], labels=labels)

    def get_column(self, index):
        """
        Selects a column from the data set.
        
        Args:
          index: 
            The column index.  If the columns are named, this is the column 
            name.  Otherwise it is the 0-based index.
          
        Returns:
          the columns at the specified index as a pandas Series object.  This 
          series is a view on the original data set, not a copy.  That means 
          any changes to it will also be applied to the original data set.
        """
        return self._dataframe[index]

    def slice_features(self, features):
        """
        Slices out the specified features into a new DataSet.

        Args:
          features: list
            A list of the names of features to keep.

        Returns:
          slice: DataSet
            The new DataSet with only the features that were specified.
            The original DataSet is unchanged.

        Examples:
          For named features:
            dataset.slice_features(["weight", "height"])
            dataset.slice_features(["weight"])
          Otherwise, features are 0-indexed based:
            dataset.slice_features([0, 1])
            dataset.slice_features([0])
        """
        return DataSet(self._dataframe[features], labels=self.labels.copy())

    def set_column(self, index, new_column):
        """
        Set the new values for a column.  Can be used to create a new column.
        
        Args:
          index: 
            The column index.  If the columns are named, this is the column 
            name.  Otherwise it is the 0-based index.
          new_column: pandas.Series or compatible object
            The new column data to be placed at the specified index.
        """
        self._dataframe[index] = new_column

    def get_row(self, identifier):
        """
        Selects a single row from the dataset.
        
        Args:
          identifier:
            The id of the row to select.  If the DataSet has special indices 
            set up (ex: through a call to load with has_ids=True) these can 
            be used.  The integer index (0 based) can also be used.
            
        Returns:
          A pandas Series object representing the desired row.  NOTE: this is 
          a view on the original dataset.  Changes made to this Series will 
          also be made to the DataSet.
        """
        return self._dataframe.ix[identifier]

    def get_rows(self, indices):
        """
        Selects specified rows from the dataset.
        
        Args:
          indices: list
            The list of row indices (0 based) which should be selected.
        
        Returns:
          A new DataSet with the specified rows from the original.
        """
        labels = self.labels.ix[indices] if self.is_labelled() else None
        return DataSet(self._dataframe.ix[indices], labels=labels)

    def split(self, percent, random=False, using_labels=False):
        """
        Splits the dataset in two.
        
        Args:
          percent: float
            The percentage of the original dataset samples which should be 
            placed in the first dataset returned.  The remainder are placed 
            in the second dataset.  This percentage must be specified as a 
            value between 0 and 1 inclusive.
          random: boolean
            Set to True if the samples selected for each new dataset should 
            be picked randomly.  Defaults to False, meaning the samples are 
            taken in their existing order.
          using_labels: boolean
            Set to True to split the samples such that there is an equal 
            representation of each known label in the resulting data sets.  
            Defaults to False.
        
        Returns:
          dataset1: DataSet object
            A subset of the original dataset with <percent> samples.
          dataset2: DataSet object
            A subset of the original dataset with 1-<percent> samples.
            
        Raises:
          ValueError if percent < 0 or percent > 1.
          UnlabelledDataSetError if using_labels set to True but the data set
            is unlabelled.
        """
        if percent < 0 or percent > 1:
            raise ValueError("Percentage value must be >= 0 and <= 1.")
        
        if using_labels:
            if not self.is_labelled():
                raise UnlabelledDataSetError()
            indices_1, indices_2 = self._split_using_labels(percent, random)
        else:
            indices_1, indices_2 = self._get_indices_for_split(percent, random)
            
        return self.get_rows(indices_1), self.get_rows(indices_2)
    
    def _get_indices_for_split(self, percent, random):
        """
        Internal method.  Finds the indices to use when splitting the 
        data set.
        
        Args:
          percent: float
            The percentage of the original dataset samples which should be 
            placed in the first dataset returned.  The remainder are placed 
            in the second dataset.  This percentage must be specified as a 
            value between 0 and 1 inclusive.
          random: boolean
            Set to True if the samples selected for each new dataset should 
            be picked randomly.  If False, the samples are taken in their 
            existing order.
            
        Returns:
          set1_indices: list(int)
          set2_indices: list(int)
            Each contains the ids for the samples that should be in the split 
            data sets.
        """
        num_set1_samples = int(percent * self.num_samples())
        
        if not random:
            set1_indices = range(num_set1_samples)
            set2_indices = range(num_set1_samples, self.num_samples())
        else:
            all_rows = range(self.num_samples())
            rand.shuffle(all_rows)
            set1_indices = all_rows[:num_set1_samples]
            set2_indices = all_rows[num_set1_samples:]

        sample_ids = self._get_sample_ids_index()
        return sample_ids[set1_indices], sample_ids[set2_indices]
    
    def _split_using_labels(self, percent, random):
        """
        Internal method.  Finds the indices to use when splitting the 
        data set such that there is an equal representation of each known
        label.
        
        Args:
          percent: float
            The percentage of the original dataset samples which should be 
            placed in the first dataset returned.  The remainder are placed 
            in the second dataset.  This percentage must be specified as a 
            value between 0 and 1 inclusive.
          random: boolean
            Set to True if the samples selected for each new dataset should 
            be picked randomly.  If False, the samples are taken in their 
            existing order.
            
        Returns:
          set1_indices: list(int)
          set2_indices: list(int)
            Each contains the ids for the samples that should be in the split 
            data sets.
        """
        set1_indices = []
        set2_indices = []
        for label in set(self.get_labels()):
            data = self.label_filter(label)
            indices_1, indices_2 = data._get_indices_for_split(percent, random)
            set1_indices.extend(indices_1)
            set2_indices.extend(indices_2)
        
        return set1_indices, set2_indices
    
    def fill_missing(self, fill_value):
        """
        Fill in missing data with a constant value.  Changes are made in-place.
        
        Args:
          fill_value:
            The value to insert wherever data is missing.
            
        Returns:
          Void.  The changes to the DataSet are made in-place.
        """
        return self._dataframe.fillna(fill_value, inplace=True)
    
    def fill_missing_with_feature_means(self):
        """
        Fill in missing data points for all features with the mean (average) 
        value of the feature.
        
        Note: if all values for a feature are missing then 0 will be 
        considered the mean.
        
        Returns:
          void; change made in place.
        """
        for feature in self.feature_list():
            feature_vals = self.get_column(feature)
            
            if feature_vals.count() == 0:
                # All values missing, fill with value 0
                self.set_column(feature, feature_vals.fillna(0))
            else:
                self.set_column(feature, 
                                feature_vals.fillna(feature_vals.mean()))
    
    def combine_labels(self, to_combine, new_label):
        """
        Combines classification labels to have some new value.
        
        For example, consider a dataset with labels "cat", "crow" and 
        "pidgeon".  Maybe you are only really worried about whether something 
        is a cat or a bird, so you want to combine the "crow" and "pidgeon" 
        labels into a new one called "bird".
        
        Args:
          to_combine: list
            The list of labels which will be combined to form one new 
            classification label.
          new_label: string
            The new classification label for those which were combined.
            
        Returns:
          void; change made in place.
        """
        # pd.Series.replace returns a new Series, leaves original unmodified
        self.labels = self.labels.replace(to_combine, value=new_label)
        
    def bin(self, feature, boundaries, bin_names=None):
        """
        Bins the values of a feature.
        
        NOTE: the feature's values must be numerical.
        
        Args:
          feature: string
            The feature whose values should be binned.
            Use '*' to bin all features.
          boundaries: list(int)
            The boundary values to bin on.  Each boundary value marks the 
            beginning value in a new bin.  
            For example, [4, 7] will put n < 4 in the first bin, 4 <= n < 7 
            in the second, and n >= 7 in the third. 
          bin_names (optional): list
            The values to substitute for each bin.  The number of bin_names
            must match the number of bin values, 
            i.e. number of boundary points + 1.
            Defaults to None, in which case the bin values range from 0 to 
            the number of boundaries.
            
        Returns:
          void; changes made in place.
          
        Raises:
          ValueError if feature values are not numerical.
          ValueError if number of bin_names does not match 
            number of bins.
          ValueError if there isn't at least one boundary.
          
        Example:
          Assume a data set has a feature MATH100 with values from 0 to 9.
          
          dataset.bin("MATH100", [4, 7], bin_names=["low", "mid", "high"])
          
          This examines values of the MATH100 feature, replacing 0, 1, 2, 3 
          with "low", 4, 5, 6 with "mid" and 7, 8, 9 with "high".
        """
        if feature == "*":
            for current_feature in self.feature_list():
                self.bin(current_feature, boundaries, bin_names=bin_names)
            return

        if len(boundaries) < 1:
            raise ValueError("Must specify at least one boundary to bin on.")
        
        feature_vals = self.get_column(feature)
        
        if not pandas_util.is_series_numeric(feature_vals):
            raise ValueError("Feature must have numerical values.")

        num_bins = len(boundaries) + 1
        if bin_names is None:
            bin_names = range(num_bins)
            
        num_bin_names = len(bin_names)
        if num_bin_names != num_bins:
            raise ValueError(("Number of bin names (%d) doesn't match number"
                              " of bins (%d)") % (num_bin_names, num_bins))

        # This is to avoid the errors you get if you try to insert string 
        # values into a numeric Series
        if isinstance(bin_names[0], str):
            dtype = np.dtype("object")
        else:
            dtype = None
            
        binned_vals = pd.Series(feature_vals.copy(), index=feature_vals.index,
                                dtype=dtype)
        
        already_binned = pd.Series([False] * len(feature_vals), 
                                   index=feature_vals.index)

        for i, boundary in enumerate(boundaries):
            in_bin = (feature_vals < boundary) & (already_binned == False)
            binned_vals[in_bin] = bin_names[i]
            already_binned[in_bin] = True
            
        # Handle values higher than the last boundary
        binned_vals[feature_vals >= boundaries[-1]] = bin_names[-1]

        self.set_column(feature, binned_vals)

    def normalize_features(self):
        """
        TODO docs
        Computes each feature's mean and subtract it from the data set.
        Then divide each feature by its standard deviation.
        """
        def normalize(feature_vector):
            return (feature_vector - feature_vector.mean()) / feature_vector.std()

        # TODO: vectorize?
        for feature in self.feature_list():
            feature_vals = self.get_column(feature)
            self.set_column(feature, normalize(feature_vals))

    def plot_radviz(self):
        """
        Generates a RadViz plot of the data set.  Radviz is useful for 
        visualizing data with more than two dimensions.
        
        Returns:
          void, but a plot is generated.
        """
        plotting.plot_radviz(self)


def as_dataset(data):
    """
    Creates a DataSet from the provided data.  If data is already a DataSet, 
    return it directly.  Use this instead of the DataSet constructor if you 
    don't know whether your data is a DataSet already, but you don't want to 
    create a new one if it already is.
    
    Args:
      data: 
        Data of unknown type.  It may be a Python list or pandas DataFrame or 
        DataSet object.
        
    Returns:
      A DataSet object.  If the data was already a DataSet then the input 
      object will be directly returned.
          
    Raises:
      ValueError if the data is not of a supported type.    
    """
    if isinstance(data, DataSet):
        return data
    else:
        return DataSet(data)
    