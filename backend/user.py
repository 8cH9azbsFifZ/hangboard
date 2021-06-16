"""
This class abstracts all information on the current user.
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='User(%(threadName)-10s) %(message)s',
                    )


class User():
    def __init__(self):
        self.Bodyweight = 91 """User weight"""
        self.Height = 191 """User height"""

        self.MaxHangTime = 60 """ Maximal Hangtime in seconds"""
        self.MaxPullUps = 12 """Maximal number of pullups"""