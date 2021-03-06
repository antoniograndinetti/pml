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
Custom errors which provide feedback to the user.

@author: drusk
"""

class InconsistentFeaturesError(Exception):
    """
    Indicates that the features found were not those expected.
    """
    
    def __init__(self, expected_features, actual_features):
        """
        Constructs a new exception.
        
        Args:
          expected_features:
            The features that should have been present.
          actual_features:
            The features which were actually there.
        """
        message = ("Expected features: %s\n"
                   "Actual features:   %s") % (expected_features, 
                                               actual_features)
        Exception.__init__(self, message)
        

class InconsistentSampleIdError(Exception):
    """
    Indicates that two data objects which should have contained data for the 
    same list of samples had a mismatch in the sample ids they contained.
    
    Used when constructing a DataSet to make sure the labels are for 
    the data provided.
    """
    
    def __init__(self, message):
        """
        Constructs a new exception.
        """
        Exception.__init__(self, message)
        

class UnlabelledDataSetError(Exception):
    """
    A custom exception to be thrown when trying to perform an operation that 
    requires a DataSet to be labelled when it is not.
    """
    
    def __init__(self, custom_message=None):
        """
        Constructs a new exception.
        """
        message = ("Operation requires the DataSet to be labelled, but it is "
                   "not.") if custom_message is None else custom_message
        Exception.__init__(self, message)


class UnsupportedPlotTypeError(Exception):
    """
    A custom exception to be thrown when trying to select a plot type that is 
    not available.
    """

    def __init__(self, requested_type, supported_types):
        """
        Constructs a new exception.
        """
        Exception.__init__(self, ("'%s' is not a supported plot type for this "
                           "operation.  Supported plot types are: [%s]") 
                           %(requested_type, ", ".join(supported_types)))

