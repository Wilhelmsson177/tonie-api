**********
Disclaimer
**********

This project is not associated with Boxine, the manufacturer of the Toniebox.
This is a private proof-of-principle project. Use at your own risk.
The underlying API at the Boxine servers may change at anytime.

************
Introduction
************
This project provides a python library to access the toniecloud via HTTP requests.
So far it is possible to upload and remove content to creative tonies and change the chapter order.

*******
Example
*******

.. code-block:: python

    import logging
    from tonie_api import TonieAPI

    # set up detailed logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    api=TonieAPI('user@mail.com', 'password')
    api.me # show your information stored in toniecloud

    # update all housholds, returns IDs of households
    api.households_update()

    # update all creative tonies, returns IDs of creative tonies
    api.households['yourHouseholdID'].creativetonies_update()

    # list chapters on creative tonie
    api.households['yourHouseholdID'].creativetonies['yourTonieID'].chapters

    # upload a new audio file
    api.households['yourHouseholdID'].creativetonies['yourTonieID'].upload('file.mp3', 'Test 123')

    # sort chapters by title
    api.households['yourHouseholdID'].creativetonies['yourTonieID'].sort_chapters('title')

    # remove all chapters on creative tonie
    api.households['yourHouseholdID'].creativetonies['yourTonieID'].remove_all_chapters()

*********
Resources
*********
Other projects which are similar or resources helpful for development:

- `Documentation of the Toniecloud API <https://api.prod.de.tbs.toys/v2/doc/>`_
- `Java library for TonieAPI by Maximilian Voß <https://github.com/maximilianvoss/toniebox-api>`_
- `Toniebox Creative Manager with web interface in C# <https://github.com/mwinkler/TonieBox.CreativeManager>`_