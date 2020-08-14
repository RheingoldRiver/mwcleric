import json
import re
from unidecode import unidecode

from .errors import EsportsCacheKeyError
from .site import Site
from .cargo_client import CargoClient


class EsportsLookupCache(object):
    def __init__(self, site: Site, cargo_client: CargoClient = None):
        self.site = site
        self.cargo_client = cargo_client
        self.cache = {}
        self.redirect_cache = {}
        self.event_tricode_cache = {}
        self.event_playername_cache = {}
    
    def clear(self):
        self.cache = {}
        self.redirect_cache = {}
        self.event_tricode_cache = {}
        self.event_playername_cache = {}
    
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
        if key is None:
            return None
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
    
    def get_target(self, title):
        """
        Caches & returns the target of a title of a wiki page, caching the result and returning
        the cached result if possible
        :param title: Title of a page on the wiki
        :return: Redirect target of the title
        """
        title = title.replace('_', ' ')
        if title in self.redirect_cache:
            return self.redirect_cache[title]
        return self.site.pages[title].resolve_redirect().name
    
    def get_team_from_event_tricode(self, event, tricode):
        """
        Determines the full name of a team based on its tricode, assuming tricode matches the short name on the wiki
        and that tricodes are unique within the provided event
        :param event: Event within which to restrict the lookup
        :param tricode: Official tricode of the team, must match wiki teamshort
        :return: Wiki teamlinkname
        """
        event = self.get_target(event)
        tricode = tricode.lower()
        result = self._get_team_from_event_tricode_raw(event, tricode)
        if result is not None:
            return result
        self._populate_event_tricodes(event)
        return self._get_team_from_event_tricode_raw(event, tricode)
    
    def _get_team_from_event_tricode_raw(self, event, tricode):
        if event in self.event_tricode_cache:
            if tricode in self.event_tricode_cache[event]:
                return self.event_tricode_cache[event][tricode]
        return None
    
    def _populate_event_tricodes(self, event):
        result = self.cargo_client.query(
            tables="TournamentRosters=Ros,TeamRedirects=TRed,Teams",
            join_on="Ros.Team=TRed.AllName,TRed._pageName=Teams.OverviewPage",
            where='Ros.OverviewPage="{}"'.format(event),
            fields="Ros.Team=Team, COALESCE(Ros.Short,Teams.Short)=Short"
        )
        d = {}
        for item in result:
            team = item['Team']
            link = self.get('Team', team, 'link')
            short = item['Short']
            if short == '':
                short = self.get('Team', team, 'short')
            if short is not None and short != '':
                d[short.lower()] = link
        self.event_tricode_cache[event] = d
    
    def get_disambiguated_player_from_event(self, event, team, player):
        """
        Returns the disambiguated ID of the player based on the team they were playing on in the event.
        
        For performance, the first time a team & event are queried, a single network call will be made
        to retrieve all possible player names for that event.
        
        These will be stored in a three-layer dictionary keyed first by event, then by team,
        then finally by player ID (not disambiguated), and ultimately yielding disambiguated player ID
        Because it's possible for a player to rename mid-event, we will just include every lifetime ID
        the player has ever had, so that future requests in the same session can use other IDs.
        The current request will use the ID requested by the current function call.
        
        teams are themselves listed within tournaments
        :param event: will be resolved as a redirect if needed
        :param team: can be a tricode if needed
        :param player: the current player ID to return the disambiguated name of
        :return: the disambiguated form of the player param
        """
        event = self.get_target(event)
        
        # we'll keep all player keys lowercase
        player_lookup = unidecode(player).lower()
        team = self.get('Team', team, 'link')
        disambiguation = self._get_player_from_event_and_team_raw(event, team, player_lookup)
        if disambiguation is not None:
            return player + disambiguation
        self._populate_event_team_players(event)
        disambiguation = self._get_player_from_event_and_team_raw(event, team, player_lookup)
        if disambiguation is not None:
            return player + disambiguation
        return None

    def _get_player_from_event_and_team_raw(self, event, team, player_lookup):
        if event in self.event_playername_cache:
            if team in self.event_playername_cache[event]:
                if player_lookup in self.event_playername_cache[event][team]:
                    return self.event_playername_cache[event][team][player_lookup]
        return None
    
    def _populate_event_team_players(self, event):
        result = self.cargo_client.query(
            tables="TournamentPlayers=TP,PlayerRedirects=PR1,PlayerRedirects=PR2",
            join_on="TP.Player=PR1.AllName,PR1.OverviewPage=PR2.OverviewPage",
            where="TP.OverviewPage=\"{}\"".format(event),
            fields="TP.Team=Team,PR2.AllName=DisambiguatedName,PR2.ID=ID",
            limit='max'
        )
        d = {}
        for item in result:
            if item['Team'] not in d:
                d[item['Team']] = {}
            team_entry = d[item['Team']]
            
            disambiguation = re.sub(r'^' + item['ID'], '', item['DisambiguatedName'])
            key = unidecode(item['ID']).lower()
            if key not in team_entry or disambiguation != '':
                team_entry[key] = disambiguation
        self.event_playername_cache[event] = d
