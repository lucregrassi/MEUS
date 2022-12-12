import os.path
from utils import parse_args
from simulator import Simulator
from save_graph import save_graph
from connectivity import build_graph
import numpy as np


def main():
    args = parse_args()
    np.random.seed(args.seed)

    if args.setup_map:
        print("Saving graph...")
        save_graph(args.place)
        print("Setting up connections...")
        build_graph(args.hubs_4g, args.radius_4g)

    if not os.path.isfile("graph/graph_temp.graphml"):
        print("Saving graph...")
        save_graph(args.place)
    print("Epidemic", args.epidemic)

    user_input = input("Choose the experiment to perform:\n"
                       "1 - Gateway ratio\n"
                       "2 - Hub radius\n"
                       "3 - Agents' observation error\n"
                       "4 - Number of agents\n"
                       "5 - Single experiment\n")

    if user_input == "1":
        build_graph(args.hubs_4g, args.radius_4g)
        for i in range(4):
            gateway_ratio = 0.05 + (0.05 * i)
            print("Experiment " + str(i) + "\nAgents: " + str(args.n_agents) + "\nGateway ratio: " + str(gateway_ratio))
            simulator = Simulator(num_exp=i,
                                  n_agents=args.n_agents,
                                  gateway_ratio=gateway_ratio,
                                  loop_distance=args.loop_distance,
                                  seed=args.seed,
                                  threshold=args.threshold,
                                  std_dev=args.std_dev,
                                  std_dev_gateway=args.std_dev_gateway,
                                  radius=args.radius_4g,
                                  nl=args.nl,
                                  epidemic=args.epidemic)
            simulator.run()
    elif user_input == "2":
        for i in range(6):
            radius = round(3 - 0.5 * i, 1)
            # Rebuild graph with different hub radius
            print("Rebuilding graph with a different hub radius")
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
                                  radius=radius,
                                  nl=args.nl,
                                  epidemic=args.epidemic)
            simulator.run()
    elif user_input == '3':
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
                                  radius=args.radius_4g,
                                  nl=args.nl,
                                  epidemic=args.epidemic)
            simulator.run()
    elif user_input == '4':
        print("Rebuilding graph")
        build_graph(args.hubs_4g, args.radius_4g)
        for i in range(3):
            if i == 0:
                n_agents = 500
                gateway_ratio = 0.2
            elif i == 1:
                n_agents = 1000
                gateway_ratio = 0.1
            else:
                n_agents = 2000
                gateway_ratio = 0.05

            print("Experiment: " + str(i) + "\nNumber of agents:", n_agents, "\nGateway ratio:", gateway_ratio)
            simulator = Simulator(num_exp=i,
                                  n_agents=n_agents,
                                  gateway_ratio=gateway_ratio,
                                  loop_distance=args.loop_distance,
                                  seed=args.seed,
                                  threshold=args.threshold,
                                  std_dev=args.std_dev,
                                  std_dev_gateway=args.std_dev_gateway,
                                  radius=args.radius_4g,
                                  nl=args.nl,
                                  epidemic=args.epidemic)
            simulator.run()
    else:
        print(f"The simulation will take place in {args.place}.")
        print(f"Parameters:\n\
               Number of agents:   {args.n_agents}\n\
               Percentage of GAs:  {args.gateway_ratio}\n\
               Loop distance:      {args.loop_distance}\n\
               Threshold:          {args.threshold}\n\
               Standard deviation: {args.std_dev}\n\
               GAs std dev         {args.std_dev_gateway}\n\
               Hub number          {args.hubs_4g}\n\
               Hub radius          {args.radius_4g}\n\
               Seed:               {args.seed}\n\
               Epidemic:           {args.epidemic}")
        print("Building graph")
        build_graph(args.hubs_4g, args.radius_4g)

        simulator = Simulator(num_exp=0,
                              n_agents=args.n_agents,
                              gateway_ratio=args.gateway_ratio,
                              loop_distance=args.loop_distance,
                              seed=args.seed,
                              threshold=args.threshold,
                              std_dev=args.std_dev,
                              std_dev_gateway=args.std_dev_gateway,
                              radius=args.radius_4g,
                              nl=args.nl,
                              epidemic=args.epidemic)
        simulator.run()


if __name__ == "__main__":
    main()
