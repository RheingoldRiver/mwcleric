import json

from .errors import EsportsCacheKeyError
from .site import Site
from .cargo_client import CargoClient


class EsportsLookupCache(object):
    def __init__(self, site: Site, cargo_client: CargoClient = None):
        self.cache = {}
        self.event_cache = {}
        self.site = site
        self.cargo_client = cargo_client
    
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
    
    def get_team_from_event_tricode(self, event, tricode):
        event = event.replace('_', ' ')
        tricode = tricode.lower()
        result = self._get_team_from_event_tricode_raw(event, tricode)
        if result:
            return result
        event = self.site.pages[event].resolve_redirect().name
        result = self._get_team_from_event_tricode_raw(event, tricode)
        if result:
            return result
        self._populate_event_tricodes(event)
        return self._get_team_from_event_tricode_raw(event, tricode)
        
    def _get_team_from_event_tricode_raw(self, event, tricode):
        if event in self.event_cache:
            if tricode in self.event_cache[event]:
                return self.event_cache[event][tricode]
            return None
    
    def _populate_event_tricodes(self, event):
        result = self.cargo_client.query(
            tables="TournamentRosters=Ros",
            where='Ros.OverviewPage="{}"'.format(event),
            fields="Ros.Team=Team"
        )
        d = {}
        for item in result:
            team = item['Team']
            d[self.get('Team', team, 'short').lower()] = self.get('Team', team, 'link')
        self.event_cache[event] = d
