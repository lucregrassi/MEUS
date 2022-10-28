import os.path
from utils import parse_args
from simulator import Simulator
from save_graph import save_graph
from connectivity import build_graph


def main():
    args = parse_args()
    print(f"The simulation will take place in {args.place}.")
    print(f"Parameters:\n\
        Number of agents:           {args.n_agents}\n\
        Percentage of gateways agents:  {args.gateway_ratio}\n\
        Loop distance:              {args.loop_distance}\n\
        Threshold:                  {args.threshold}\n\
        Standard Deviation:         {args.std_dev}\n\
        Gateway Agents Std Dev      {args.std_dev_gateway}\n\
        Hub number                  {args.hubs_4g}\n\
        Hub Radius                  {args.radius_4g}\n\
        Seed:                       {args.seed}\n\
        Store Latency data:         {args.st}")

    if args.setup_map:
        print("Saving graph...")
        save_graph(args.place)
        print("Setting up connections...")
        build_graph(args.hubs_4g, args.radius_4g)

    if args.st:
        if not os.path.isfile("graph/graph_temp.graphml"):
            print("Saving graph...")
            save_graph(args.place)
        user_input = input("Enter which parameter do you wish to vary:\n1 - Gateway agent percentage\n2 - Hub radius\n"
                           "3 - Standard Deviation of the Gaussian distribution of the error of the agents\n")
        assert user_input in ["1", "2", "3"], "Parameter should be either 1, 2, or 3."

        if user_input == '1':
            build_graph(args.hubs_4g, args.radius_4g)
            for i in range(6):
                if i == 0:
                    gateway_ratio = 0.1
                else:
                    gateway_ratio = round(0.06 - 0.01 * i, 2)
                print("Experiment: " + str(i) + "\nGateway ratio: ", str(gateway_ratio))
                simulator = Simulator(num_exp=i,
                                      n_agents=args.n_agents,
                                      gateway_ratio=gateway_ratio,
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
            for i in range(6):
                radius = round(3 - 0.5 * i, 1)
                # Rebuild graph with different hub radius
                build_graph(args.hubs_4g, radius)
                print("Experiment: " + str(i) + "\nRadius: " + str(radius))
                simulator = Simulator(num_exp=i,
                                      n_agents=args.n_agents,
                                      gateway_ratio=args.gateway_ratio,
                                      loop_distance=args.loop_distance,
                                      seed=args.seed,
                                      threshold=args.threshold,
                                      std_dev=args.std_dev,
                                      std_dev_gateway=args.std_dev_gateway,
                                      store_latency=args.st,
                                      radius=radius,
                                      th=args.nl,
                                      param="radius")
                simulator.run()
        else:
            build_graph(args.hubs_4g, args.radius_4g)
            for i in range(9):
                if i < 3:
                    std_dev = 0.5
                elif 3 <= i <= 5:
                    std_dev = 1
                else:
                    std_dev = 1.5

                if i == 0 or i == 3 or i == 6:
                    std_dev_gateway = 0.2
                elif i == 1 or i == 4 or i == 7:
                    std_dev_gateway = 0.5
                else:
                    std_dev_gateway = 0.8

                print("Experiment " + str(i) + "\nAgent's std: " + str(std_dev) + "\nGateway agent's std: "
                      + str(std_dev_gateway))
                simulator = Simulator(num_exp=i,
                                      n_agents=args.n_agents,
                                      gateway_ratio=args.gateway_ratio,
                                      loop_distance=args.loop_distance,
                                      seed=args.seed,
                                      threshold=args.threshold,
                                      std_dev=std_dev,
                                      std_dev_gateway=std_dev_gateway,
                                      store_latency=args.st,
                                      radius=args.radius_4g,
                                      th=args.nl,
                                      param="std_dev")
                simulator.run()
    else:
        build_graph(args.hubs_4g, args.radius_4g)
        simulator = Simulator(num_exp=0,
                              n_agents=args.n_agents,
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
