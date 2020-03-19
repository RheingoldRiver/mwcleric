from .site import Site
from .errors import EsportsCacheKeyError
import json


class EsportsLookupCache(object):
    def __init__(self, site: Site):
        self.cache = {}
        self.site = site

    def _get_json_lookup(self, filename):
        """
        Returns a json representation of the requested file, queriying the site to retrieve it if needed
        :param filename: The name of the file to return, e.g. "Champion" or "Role"
        :return: A json object representing the lookup file
        """
        if filename in self.cache:
            return self.cache[filename]
        result = self.site.api(
            'expandtemplates',
            prop='wikitext',
            text='{{JsonEncode|%s}}' % filename
        )
        self.cache[filename] = json.loads(result['expandtemplates']['wikitext'])
        return self.cache[filename]

    def get(self, filename, key, length):
        """
        Returrns the length of the lookup of a key requested from the filename requested. Assumes the file has
        the same structure as the -names modules on Leaguepedia.
        :param filename: "Champion", "Role", etc. - the name of the file
        :param key: The lookup key, e.g. "Morde"
        :param length: The length of value to return, e.g. "long" or "link"
        :return: Correct lookup value provided, or None if it's not found
        """
        file = self._get_json_lookup(filename)
        key = key.lower()
        if key not in file:
            return None
        value_table = file[key]
        if isinstance(value_table, str):
            key = value_table
            value_table = file[value_table]
        if length not in value_table:
            raise EsportsCacheKeyError(filename, key, length, value_table)
        return value_table[length]
