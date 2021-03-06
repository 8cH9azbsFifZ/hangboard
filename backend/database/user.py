"""
This class abstracts all information on the current user.
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='User(%(threadName)-10s) %(message)s',
                    )
from database import Database

class User():
    def __init__(self, dbhostname="hangboard", dbuser="root", dbpassword="rootpassword", user="us3r"):
        self._db = Database(hostname=dbhostname, user=dbuser, password=dbpassword)
        self._user = user
        self._db._set_user(user)

        self._get_user_parameters()

    def _get_user_parameters(self):
        self.Bodyweight = 78 #"""User weight"""
        self.Height = 184 #"""User height"""

    def _get_user_performance(self, hold="JUG", hand="both"):
        self.Hold = hold
        self.Hand = hand

        self.MaxLoad = self._db._get_maxload(hold=hold, hand=hand)
        self.MaxHangTime = self._db._get_maxhangtime(hold=hold, hand=hand)

        self.MaxPullUps = 12 #FIXME
        
    def SetReference(self, hold="JUG", hand="both"):
        """ Find out the maximal parameters for a given hold configuration """
        self._get_user_performance(hold=hold, hand=hand)

    def GetCurrentIntensity(self, currentload):
        """ Calculate intensity - warning hold configuration must be set in advance and SetReference will yield the correct maxload for the hold configuration """
        intensity = currentload / self.MaxLoad
        if intensity < 0.0: 
            intensity = 0.0
        if intensity > 1.0:
            intensity = 1.0
        return intensity



if __name__ == "__main__":
    u = User(user="us3r")
    u.SetReference(hold="20mm", hand="both")
    print (u.GetCurrentIntensity(72))