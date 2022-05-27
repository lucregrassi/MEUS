from utils import parse_args
from simulator import Simulator
from save_graph import save_graph
from connectivity import build_graph


def main():
    args = parse_args()
    print(f"The simulation will take place in {args.place}.")
    print(f"With the following parameters:\n\
        Number of agents:           {args.n_agents}\n\
        Number of gateways agents:  {args.gateway_ratio}\n\
        Loop distance:              {args.loop_distance}\n\
        Seed:                       {args.seed}\n\
        Threshold:                  {args.threshold}\n\
        Standard Deviation:         {args.std_dev}\n\
        Gateway Agents Std Dev      {args.std_dev_gateway}\n\
        Store Latency data:         {args.st}")

    if args.setup_map is True:
        save_graph(args.place)
        build_graph(args.hubs_4g, args.radius_4g)

    if args.st:
        user_input = input("Enter which parameter do you wish to vary:\n1 - Gateways\n2 - Radius\n"
                           "3 - Standard Deviation of the Gaussian distribution of the error of the agents\n")
        assert user_input in ["1", "2", "3"], "Parameter should be either 1, 2, or 3."
        if user_input == '1':
            for i in range(4):
                print("Experiment " + str(i))
                simulator = Simulator(n_agents=args.n_agents,
                                      gateway_ratio=args.gateway_ratio,
                                      loop_distance=args.loop_distance,
                                      seed=args.seed,
                                      threshold=args.threshold,
                                      std_dev=args.std_dev,
                                      std_dev_gateway=args.std_dev_gateway,
                                      store_latency=args.st,
                                      radius=args.radius_4g,
                                      th=args.nl,
                                      param="gateways")
                simulator.run()
        elif user_input == "2":
            for i in range(3):
                print("Experiment " + str(i))
                simulator = Simulator(n_agents=args.n_agents,
                                      gateway_ratio=args.gateway_ratio,
                                      loop_distance=args.loop_distance,
                                      seed=args.seed,
                                      threshold=args.threshold,
                                      std_dev=args.std_dev,
                                      std_dev_gateway=args.std_dev_gateway,
                                      store_latency=args.st,
                                      radius=args.radius_4g,
                                      th=args.nl,
                                      param="radius")
                simulator.run()
        else:
            for i in range(3):
                print("Experiment " + str(i))
                simulator = Simulator(n_agents=args.n_agents,
                                      gateway_ratio=args.gateway_ratio,
                                      loop_distance=args.loop_distance,
                                      seed=args.seed,
                                      threshold=args.threshold,
                                      std_dev=args.std_dev,
                                      std_dev_gateway=args.std_dev_gateway,
                                      store_latency=args.st,
                                      radius=args.radius_4g,
                                      th=args.nl,
                                      param="std_dev")
                simulator.run()
    else:
        simulator = Simulator(n_agents=args.n_agents,
                              gateway_ratio=args.gateway_ratio,
                              loop_distance=args.loop_distance,
                              seed=args.seed,
                              threshold=args.threshold,
                              std_dev=args.std_dev,
                              std_dev_gateway=args.std_dev_gateway,
                              store_latency=args.st,
                              radius=args.radius_4g,
                              th=args.nl)
        simulator.run()


if __name__ == "__main__":
    main()
