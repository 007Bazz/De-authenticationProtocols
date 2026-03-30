import simulation as sim
from protocols.normal import Normal
from protocols.letter_envelope import LetterEnvelope
from protocols.uuid_sha512 import UUIDSHA512
import time
import matplotlib.pyplot as plt

RUNS = 50

def make_graph():
    protocols = ('Normal', 'Letter Envelope', 'UUID SHA512')
    nt, nm = normal_connect()
    lt, lm = letter_envelope_connect()
    ut, um = uuid_envelope_connect()
    times = [nt, lt, ut]
    mems = [nm, lm, um]
    plt.bar(protocols, times)
    plt.savefig('connectTimings.png')
    plt.clf()
    plt.plot(nm, label="Normal")
    plt.plot(lm, label="Letter Envelope")
    plt.plot(um, label="UUID SHA512")
    plt.legend()
    plt.savefig('connectMems.png')

def normal_connect():
    ether = sim.Ether()
    protocol = Normal()
    ap = sim.AccessPoint(ether, "bo:ba:ca:fe:00:01", protocol, "AccessPoint")
    mems = []
    start = time.time()
    for i in range(RUNS):
        h = "%04x" % i
        client = sim.Client(ether, "de:ad:be:ef:"+h[:2]+":"+h[-2:], protocol)
        client.connect()
        mems.append(ap.client_memory())
    end = time.time()
    ap.stop()
    return (end-start, mems)

def letter_envelope_connect():
    ether = sim.Ether()
    protocol = LetterEnvelope()
    ap = sim.AccessPoint(ether, "bo:ba:ca:fe:00:01", protocol, "AccessPoint")
    mems = []
    start = time.time()
    for i in range(RUNS):
        h = "%04x" % i
        client = sim.Client(ether, "de:ad:be:ef:"+h[:2]+":"+h[-2:], protocol)
        client.connect()
        mems.append(ap.client_memory())
    end = time.time()
    ap.stop()
    return (end-start, mems)

def uuid_envelope_connect():
    ether = sim.Ether()
    protocol = UUIDSHA512()
    ap = sim.AccessPoint(ether, "bo:ba:ca:fe:00:01", protocol, "AccessPoint")
    mems = []
    start = time.time()
    for i in range(RUNS):
        h = "%04x" % i
        client = sim.Client(ether, "de:ad:be:ef:"+h[:2]+":"+h[-2:], protocol)
        client.connect()
        mems.append(ap.client_memory())
    end = time.time()
    ap.stop()
    return (end-start, mems)
