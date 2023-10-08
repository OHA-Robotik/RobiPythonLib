from Robi42Lib import robi42
from Robi42Lib.modules.piezo import SampleTones

r = robi42.Robi42()
r.piezo.play_tone(SampleTones.get_tone("C0"))
