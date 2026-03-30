# import simulation as sim
# import multiprocessing as mp
# import time
# from protocols.letter_envelope import LetterEnvelope

# def sniff(ether):
#     while True:
#         print("Sniff", ether.recv())

# if __name__ == "__main__":
#     ether = sim.Ether()
#     letter_env = LetterEnvelope()
#     p = mp.Process(target=sniff, args=(ether,))
#     p.start()
#     ap = sim.AccessPoint(ether, "b0:ba:ca:fe:01:01", letter_env, "Mother")
#     time.sleep(2) #Give sniff time to start
#     client = sim.Client(ether, "de:ad:be:ef:01:01", letter_env)
#     client.connect()
#     time.sleep(0.5)
#     client.deauth()
#     time.sleep(0.5)
#     client.connect()
#     ap.deauth_all()
#     ap.join()

import scenarios

if __name__ == "__main__":
    scenarios.run_all()