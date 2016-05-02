import urllib
import urllib2
from bs4 import BeautifulSoup
from twilio.rest import TwilioRestClient

"""Module for retrieving football scores via webscraping."""


def create_dict_from_lists(keys, values):
    """Takes list of keys, and a list of values, creates a dictionary of 
    key:value pairs. By position.
    """
    zipped = zip(keys,values)
    return {key:value for (key,value) in zipped}


def get_html_text(html_results):
    """Given some BeautifulSoup results, return the same results in text 
    only form. I.e. no tags.
    """
    html_text = []
    for result in html_results:
        html_text.append(result.get_text())
    return html_text


class League_urls(object):
    """Class to store globally available urls for each league."""
    premier_league = 'http://www.livescore.com/soccer/england/premier-league/'
    la_liga = 'http://www.livescore.com/soccer/spain/primera-division/'
    bundesliga = 'http://www.livescore.com/soccer/germany/bundesliga/'
    serie_a = 'http://www.livescore.com/soccer/italy/serie-a/'
    ligue_1 = 'http://www.livescore.com/soccer/france/ligue-1/'


class Sms_info(object):
    """Class to store information about a twilio sms account
    used to send football scores to other numbers.
    """
    account_sid = 'AC41b15c354dfa41991f1a6376f2aXXXXX'
    account_token = 'b520026a8cb530a73cbb71e01e7XXXXX'
    sms_number = '44XXXXXXXXXX'


class League(object):
    """Represents a particular league. Holds a list of all associated matches,
    and various methods to populate said match data.
    """

    def __init__(self, url):
        self.match_count = 1
        self.matches = []
        self.url = url

    def __str__(self):
        league_str = ''
        for match in league.matches:
            league_str += ('\n{0}\n'.format(match))
        return league_str

    def get_html(self):
        """Get a urllib object for this league's url."""
        return urllib.urlopen(self.url)

    def get_matches(self):
        """Do a web scrape to retreive the current round of scores
        for this league.
        Each child represents one match, of the form:
        [kick_off, home_team, score, score, away_team, , ]
        """
        bsObj_pl = BeautifulSoup(self.get_html(), 'html.parser')
        for match in bsObj_pl.findAll('div', {'data-type':'evt'}):
            results_children = match.findChildren()
            children_text = get_html_text(results_children)
            # Score is duplicated, so remove duplicate.
            children_text.pop(2)
            self.matches.append(Match(children_text, self))
 
    def get_sms_str(self):
        """Construct string of scores to send over sms."""
        sms_str = 'Latest Scores:\n'
        sms_str += self.__str__()
        return sms_str


class Match(object):
    """Represents a given match and its result."""

    def __init__(self, match_data, league):
        """Using a dictionary instead of several 'self.X' values makes the 
        str method trivial.
        """
        self.match_keys = ['kick_off', 'home_team', 'score', 'away_team']
        self.display_template = ('{0[kick_off]}>{0[home_team]}{0[score]}'
                                '{0[away_team]}')
        self.league = league
        self.match_data = create_dict_from_lists(self.match_keys, match_data)
        self.match_data['match_num'] = self.league.match_count
        self.league.match_count += 1

    def __str__(self):
        return self.display_template.format(self.match_data)

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':

    league = League(League_urls.premier_league)
    league.get_matches()

    sms_str = league.get_sms_str()
    print sms_str
    
    # If you uncomment the below and fill in the Sms_info class with a  
    # valid twilio account, then you should get the scores text directly
    # to whichever phone you specify as the 'to' argument.

    #client = TwilioRestClient(account=Sms_info.account_sid, 
    #                          token=Sms_info.account_token)

    #client.messages.create(to='+44XXXXXXXXXXX',
    #                       from_=Sms_info.sms_number,
    #                       body=sms_str)

