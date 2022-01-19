import argparse
import osmnx as ox
from utils import parse_args
from pprint import pprint
from simulator1 import Simulator
from save_graph import save_graph
from connectivity import build_graph, color


def main():

    args = parse_args()


    print("")
    print(f"The simulation will take place in {args.place}.")
    print(f"With the following parameters:\n\
        Number of agents:           {args.n_agents}\n\
        Number of gateways agents:  {args.n_gateways}\n\
        Loop distance:              {args.loop_distance}\n\
        Seed:                       {args.seed}\n\
        Threshold:                  {args.threshold}\n\
        Error rate:                 {args.err_rate}\n\
        Store Latency data:         {args.st}")
    
    if args.setup_map is True:
        save_graph(args.place)

        build_graph(args.hubs_4g, args.radius_4g)
    
    if args.st:

        p = input('Enter which parameter do you wish to vary [gateways/radius].\n\n')

        assert p=='gateways' or p=='radius',\
            'parameter should be either gateways or radius.'

        if p=='gateways':
            for i in range(4):
                simulator = Simulator(  n_agents        = args.n_agents,
                                        n_gateways      = args.n_gateways,
                                        loop_distance   = args.loop_distance,
                                        seed            = args.seed,
                                        threshold       = args.threshold,
                                        err_rate        = args.err_rate,
                                        store_latency   = args.st,
                                        radius          = args.radius_4g,
                                        th              = args.nl,
                                        param           = p)
            
                simulator.run()

        else:
            for i in range(3):
                simulator = Simulator(  n_agents        = args.n_agents,
                                        n_gateways      = args.n_gateways,
                                        loop_distance   = args.loop_distance,
                                        seed            = args.seed,
                                        threshold       = args.threshold,
                                        err_rate        = args.err_rate,
                                        store_latency   = args.st,
                                        radius          = args.radius_4g,
                                        th              = args.nl,
                                        param           = p)
            
                simulator.run()

    
    else:
        simulator = Simulator(  n_agents        = args.n_agents,
                                n_gateways      = args.n_gateways,
                                loop_distance   = args.loop_distance,
                                seed            = args.seed,
                                threshold       = args.threshold,
                                err_rate        = args.err_rate,
                                store_latency   = args.st,
                                radius          = args.radius_4g,
                                th              = args.nl)

        simulator.run()

if __name__=="__main__":
    main()