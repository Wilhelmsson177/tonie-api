import logging
import requests
from requests.exceptions import HTTPError
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class _TonieOAuth2Session(OAuth2Session):
    """`OAuth2Session` class with some additional
    methods useful for tonie_api.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_json(self, url):
        """HTTP `GET` request which, if successful,
        is parsed to JSON format.
        Catches HTTP errors and writes them to logger.

        :param url: URL
        :type url: str
        :return: response in JSON format
        :rtype: dict
        """
        try:
            r = self.get(url)
            r.raise_for_status()
        except HTTPError as http_err:
            log.error(f'HTTP error occured: {http_err}')
            return None
        # except Exception as err:
        #     log.error(f'Other error occured: {err}')
        #     return None
        else:
            return r.json()

    def patch_json(self, url, **kwargs):
        """HTTP `PATCH` request which, if successful,
        is parsed to JSON format.
        Catches HTTP errors and writes them to logger.

        :param url: URL
        :type url: str
        :return: response in JSON format
        :rtype: dict
        """
        try:
            r = self.patch(url, **kwargs)
            r.raise_for_status()
        except HTTPError as http_err:
            log.error(f'HTTP error occured: {http_err}')
            return None
        # except Exception as err:
        #     log.error(f'Other error occured: {err}')
        #     return None
        else:
            return r.json()


class _TonieAPIBase():
    """Container for methods shared between different classes
    of the TonieboxAPI.
    """
    # to be patched by inherited classes
    API_URL = None
    session = None

    def _updater(self, r, storedict, itemclass):
        """Updates a dictionary of instances from a
        dict of IDs. Create an instance for every missing
        ID. Delete instances which are no longer present.

        Example: A dict of creative tonies with `ID:properties`
        retrieved from a request to the toniecloud.
        For every tonie a :class:`_CreativeTonie` instance is
        created and added to `storedict` under it's ID.

        :param r: JSON response from HTTP request
        :type r: dict
        :param storedict: variable to store the instances
        :type storedict: dict
        :param itemclass: class to be instantiated
        :type itemclass: class
        :return: dict of `ID:name`
        :rtype: dict
        """
        # add only new items to dict
        for hh in r:
            if hh['id'] not in storedict.keys():
                storedict[hh['id']] = itemclass(
                    self.API_URL, self.session, hh)
        # check if items have been removed on the server
        if len(storedict) > len(r):
            for hh in storedict.keys():
                if hh not in r.keys():
                    del storedict[hh]
                    log.info(f'Removed {itemclass.__name__} {hh}')
        # return id -> name dict
        return {k: v.name for k, v in storedict.items()}


class TonieAPI(_TonieAPIBase):
    """Interface to toniecloud. Authenticates and acquires
        token for communication.

        :param username: username for login to login.tonies.com
        :type username: str
        :param password: password for login to login.tonies.com
        :type password: str
        """

    API_URL = 'https://api.tonie.cloud/v2'
    TOKEN_URL = 'https://login.tonies.com/auth/realms/tonies/protocol/openid-connect/token'

    def __init__(self, username, password):
        client = LegacyApplicationClient(client_id='meine-tonies')
        self.session = _TonieOAuth2Session(client=client)
        self.session.fetch_token(
            token_url=self.TOKEN_URL,
            username=username,
            password=password
        )
        self._households = {}

    @property
    def me(self):
        """Account information
        """
        return self.session.get_json(f'{self.API_URL}/me')

    @property
    def config(self):
        """Configuration
        """
        return self.session.get_json(f'{self.API_URL}/config')

    @property
    def households(self):
        """Household instances acquired by
        :meth:`TonieAPI.households_update()`. Household IDs as keys.

        :return: Household instances
        :rtype: dict
        """
        return self._households

    def households_update(self):
        """Get households from toniecloud and create
        :class:`_Household` instance for each new household.
        Store instances in :meth:`TonieAPI.households` property.

        :return: Household ID: household name
        :rtype: dict
        """
        r = self.session.get_json(f'{self.API_URL}/households')
        if r is None:
            log.warning('Households could not be updated.')
            return
        else:
            return self._updater(r, self._households, _Household)
        # for hh in r:
        #     if hh['id'] not in self._households.keys():
        #         self._households[hh['id']] = _Household(
        #             self.API_URL, self.session, hh)
        # if len(self._households) > len(r):
        #     for hh in self._households.keys():
        #         if hh not in r.keys():
        #             del self._households[hh]
        #             log.info(f'Removed household {hh}')
        # return {k: v.name for k, v in self._households.items()}

    def update(self):
        """Update data structure from toniecloud:

            - all households & their properties
            - all creative tonies & their properties
        """
        log.info('Updating TonieAPI...')
        self.households_update()
        for hh in self.households.values():
            # update name and other properties
            hh.properties
            # update list creative tonies
            hh.creativetonies_update()
            for ct in hh.creativetonies.values():
                # update name and other properties
                ct.properties
        log.info('Updating TonieAPI completed.')


class _Household(_TonieAPIBase):
    """Represents Household of tonies.

    :param API_URL: API URL
    :type API_URL: str
    :param session: communication session
    :type session: :class:`_TonieOAuth2Session`
    :param hhproperties: initial household properties
    :type hhproperties: dict
    """

    def __init__(self, API_URL, session, hhproperties):
        self.session = session
        # self.properties = hhproperties
        self.id = hhproperties['id']
        self.name = hhproperties['name']
        self.API_URL = f'{API_URL}/households/{self.id}'
        log.info(f'Set up household {self.id} with name {self.name}.')
        self._creativetonies = {}

    @property
    def properties(self):
        """Properties of the household read from
        toniecloud.
        """
        prop = self.session.get_json(self.API_URL)
        self.name = prop['name']
        return prop

    @property
    def creativetonies(self):
        """Creative tonie instances acquired by
        :meth:`_Household.creativetonies_update()`. Tonie IDs as keys.

        :return: Creative tonie instances
        :rtype: dict
        """
        return self._creativetonies

    def creativetonies_update(self):
        """Get creative tonies from toniecloud and create
        :class:`_CreativeTonie` instance for each new tonie
        Store instances in :meth:`_Household.creativetonies` property.

        :return: tonie ID: tonie name
        :rtype: dict
        """
        r = self.session.get_json(f'{self.API_URL}/creativetonies')
        if r is None:
            log.warning('Creative tonies could not be updated.')
            return
        else:
            return self._updater(r, self._creativetonies, _CreativeTonie)
        # for ct in r:
        #     if ct['id'] not in self._creativetonies.keys():
        #         self._creativetonies[ct['id']] = _CreativeTonie(
        #             self.API_URL, self.session, ct)
        # return {k: v.name for k, v in self._creativetonies.items()}


class _CreativeTonie():
    """Represents single creative tonie.

    :param API_URL: API URL
    :type API_URL: str
    :param session: communication session
    :type session: :class:`_TonieOAuth2Session`
    :param hhproperties: initial tonie properties
    :type hhproperties: dict
    """
    def __init__(self, API_URL, session, ctproperties):
        self.session = session
        # self._properties = ctproperties
        self.id = ctproperties['id']
        self.name = ctproperties['name']
        self.API_URL = f'{API_URL}/creativetonies/{self.id}'
        log.info(f'Set up creative tonie {self.id} with name {self.name}.')

    @property
    def properties(self):
        """Properties of the creative tonie read from
        toniecloud.
        """
        prop = self.session.get_json(self.API_URL)
        self.name = prop['name']
        return prop

    @property
    def chapters(self):
        """Chapters of content connected to this tonie.
        """
        return self.properties['chapters']

    def _patch_chapters(self, chapters):
        """HTTP ``PATCH`` request to update the chapter information.

        :param chapters: new chapters JSON data
        :type chapters: dict
        """
        r = self.session.patch_json(
            f'{self.API_URL}', json={'chapters': chapters})
        log.info(f'Chapters of {self.id} updated.')
        return r

    def remove_all_chapters(self):
        """Removes all chapters stored on this tonie.

        :return: response in JSON format
        :rtype: dict
        """
        r = self.session.patch_json(
            f'{self.API_URL}', json={'chapters': []})
        log.info(f'All chapters of {self.id} removed.')
        return r

    def add_chapter(self, fileid, title):
        """Add single chapter to the end of the tonie.

        :param fileid: fileID from upload
        :type fileid: str
        :param title: chapter title
        :type title: str
        :return: contentID of uploaded chapter
        :rtype: str
        """
        chapters = self.chapters
        chapters.append(_Chapter(fileid, title, fileid))
        r = self._patch_chapters(chapters)
        # find new contentid associated with the uploaded file
        for ch in reversed(r['chapters']):
            # for new file:
            #   file field contains fileID (this changes afterwards!)
            #   id fieldholds newly assigned contentID
            if ch['file'] == fileid:
                contentid = ch['id']
                break
        log.info(
            f'Appended uploaded file {fileid} with title {title}'
            f' as chapter with id {contentid} to {self.id},'
            f' now containing {len(chapters)} chapters.')
        return contentid

    def sort_chapters(self, sortkey, sortlist=None):
        """Sort chapters of the tonie according to specified
        key (`'id'` or `'title'`). Optionally, sort according
        to given list.

        :param sortkey: key to sort list by (`'id'` or `'title'`)
        :type sortkey: str
        :param sortlist: list of keys in desired order, defaults to None
        :type sortlist: list, optional
        :return: updated chapters data
        :rtype: dict
        """
        # sortkey may be: id, title
        # sortlist entries must be unique!
        chapters = self.chapters
        if sortlist is None:
            chapters = sorted(chapters, key=lambda ch: ch[sortkey])
        else:
            # order according to sortlist
            if len(sortlist) < len(chapters):
                log.warning(
                    'Sorting of chapters will remove 1 or more chapters!')
            chapters = {ch[sortkey]: ch for ch in chapters}
            chapters = [chapters[key] for key in sortlist]
        self._patch_chapters(chapters)
        return chapters

    def upload(self, file, title):
        """Upload file to toniecloud and append as new
        chapter to tonie.

        :param file: filename
        :type file: str
        :param title: chapter title
        :type title: str
        :return: ID of the file/chapter in the toniecloud
        :rtype: str
        """
        # get info and credentials for upload from toniecloud
        r = self.session.post('https://api.tonie.cloud/v2/file').json()
        fileid = r['fileId']  # same as fields['key']
        url = r['request']['url']
        fields = r['request']['fields']
        log.debug(f'fileid: {fileid} - key:{fields["key"]}')
        # upload to Amazon S3
        try:
            r = requests.post(url, files={
                **fields,
                'file': (fields['key'], open(file, 'rb'))
                })
            r.raise_for_status()
        except HTTPError as http_err:
            log.error(f'HTTP error occured: {http_err}')
            return
        # except Exception as err:
        #     log.error(f'Other error occured: {err}')
        #     return
        contentid = r.headers['etag']
        log.info(f'File {file} uploaded to server with ID {fields["key"]}.')
        # add chapter to creative tonie
        contentid = self.add_chapter(fileid, title)
        return contentid


class _Chapter(dict):
    """Chapter of content on creative tonie.

    :param contentid: ID of file in toniecloud
    :type contentid: str
    :param title: chapter title
    :type title: str
    :param filename: filename on server
    :type filename: str
    :param seconds: duration in seconds, defaults to None
    :type seconds: float, optional
    :param transcoding: pending transcoding, defaults to None
    :type transcoding: bool, optional
    """
    def __init__(self, contentid, title, filename,
                 seconds=None, transcoding=None):
        super().__init__()
        self['id'] = contentid
        self['title'] = title
        self['file'] = filename
        if seconds is not None:
            self['seconds'] = seconds
        if transcoding is not None:
            self['transcoding'] = transcoding
