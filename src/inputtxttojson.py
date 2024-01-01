import json
import os


def create_json_file(input_file, output_file):
    # Read data from the input file
    with open(input_file, "r") as file:
        data = file.readlines()

    # Extract metadata information
    metadata = {
        "slicingMethod": data[0]
        .replace("Slicing from the identifiable method", "")
        .strip(),
        "slicedSDGSize": int(data[1].strip().split()[-1]),
    }

    # Check if nodes visited and edges added information exists
    try:
        nodes_visited_line = data[-5].strip()
        print(nodes_visited_line)
        edges_added_line = data[-2].strip()
        print(edges_added_line)

        if nodes_visited_line.startswith("NODES VISITED:"):
            metadata["nodesVisited"] = int(nodes_visited_line.split(":")[-1].strip())

        if edges_added_line.startswith("EDGES ADDED:"):
            metadata["edgesAdded"] = int(edges_added_line.split(":")[-1].strip())
    except IndexError:
        # Handle the exception when the required lines are missing
        print("Required information not found in data.")

    # Extract node information
    node_data = []
    for line in data[3:-4]:
        line = line.strip()
        if line.startswith("["):
            node_info = line[1:-1].split(", ")
            node = node_info[0]
            privacy_relevance = node_info[1]
            to_node = node_info[2]
            edge_type = [
                int(x) if x.isdigit() else x
                for x in node_info[3].split("=")[-1].strip()[1:-1].split(",")
            ]
            additional_info = node_info[4] if len(node_info) > 4 else ""
            node_data.append(
                {
                    "node": node,
                    "privacyRelevance": privacy_relevance,
                    "toNode": to_node,
                    "edgeType": edge_type,
                    "additionalInfo": additional_info,
                }
            )

    # Create JSON object
    json_data = {"metadata": metadata, "data": node_data}

    # Write JSON data to the output file
    with open(output_file, "w") as file:
        json.dump(json_data, file, indent=2)
