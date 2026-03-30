import simulation as sim
from protocols.normal import Normal
from protocols.letter_envelope import LetterEnvelope
import time
import matplotlib.pyplot as plt

RUNS = 10

def make_graph():
    protocols = ('Normal', 'Letter Envelope')
    times = [normal_connect(), letter_envelope_connect()]
    plt.bar(protocols, times)
    plt.savefig('connectTimings.png')

def normal_connect():
    ether = sim.Ether()
    protocol = Normal()
    ap = sim.AccessPoint(ether, "bo:ba:ca:fe:00:01", protocol, "AccessPoint")
    start = time.time()
    for i in range(RUNS):
        h = "%04x" % i
        client = sim.Client(ether, "de:ad:be:ef:"+h[:2]+":"+h[-2:], protocol)
        client.connect()
    end = time.time()
    ap.stop()
    return end-start

def letter_envelope_connect():
    ether = sim.Ether()
    protocol = LetterEnvelope()
    ap = sim.AccessPoint(ether, "bo:ba:ca:fe:00:01", protocol, "AccessPoint")
    start = time.time()
    for i in range(RUNS):
        h = "%04x" % i
        client = sim.Client(ether, "de:ad:be:ef:"+h[:2]+":"+h[-2:], protocol)
        client.connect()
    end = time.time()
    ap.stop()
    return end-start