from simulator1 import Simulator

def main():
    
    simulator = Simulator(  n_agents        = 100,
                            n_gateways      = 0.5,
                            loop_distance   = 20,
                            seed            = 57,
                            threshold       = 100,
                            err_rate        = 0.9)
    simulator.run()

if __name__=="__main__":
    main()