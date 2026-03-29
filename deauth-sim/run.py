import simulation as sim
import time

if __name__ == "__main__":
    ether = sim.Ether()
    ap = sim.AccessPoint("DE:AD:BE:EF:01", {}, ether)
    ether.send("Hello")
    time.sleep(4)
    ether.send("Hello again")
    ap.join()