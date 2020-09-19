###################
API
###################

.. contents::
    :local:

The toniecloud is organized in the following way:

- every tonie belongs to a household
- you may have one or more households in your tonie account

Every household and every tonie is referenced by an unique ID.
Households and creative tonies are automatically added to the
:class:`tonie_api.TonieAPI` instance by calling the appropriate `update()` methods.

********
TonieAPI
********

.. autoclass:: tonie_api.TonieAPI
    :members:
    :private-members:
    :show-inheritance:
    :member-order: bysource

*********
Household
*********
.. autoclass:: tonie_api.api._Household
    :members:
    :private-members:
    :show-inheritance:
    :member-order: bysource

*************
CreativeTonie
*************
.. autoclass:: tonie_api.api._CreativeTonie
    :members:
    :private-members:
    :show-inheritance:
    :member-order: bysource

*******
Chapter
*******

.. autoclass:: tonie_api.api._Chapter
    :members:
    :private-members:
    :show-inheritance:
    :member-order: bysource

******************
Additional Classes
******************

.. autoclass:: tonie_api.api._TonieOAuth2Session
    :members:
    :private-members:
    :show-inheritance:
    :member-order: bysource