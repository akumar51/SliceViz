from flask import Flask, render_template, request, jsonify
import json
import logging
import re

app = Flask(__name__, static_folder="static")

with open(
    "static/input/RiskCategories/ModifiedAnnotatedMethods.json"
) as f:
    app.all_risk_categories = json.load(f)

# Configure logging
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/pribasedoc")
def pribasedoc():
    return render_template("pribasedoc.html")


@app.route("/vis", methods=["GET", "POST"])
def visualize():
    if request.method == "POST":
        # Check if the request contains a file
        if "file" not in request.files:
            return "No file uploaded"

        uploaded_file = request.files["file"]

        # Check if a file is selected
        if uploaded_file.filename == "":
            return "No file selected"

        # Process the file based on its extension
        if uploaded_file.filename.endswith(".txt"):
            # Read and convert text file to JSON
            file_content = uploaded_file.read().decode("utf-8")
            data = convert_text_to_json(file_content)
        elif uploaded_file.filename.endswith(".json"):
            # Load JSON data directly
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                return "Invalid JSON file. Please upload a valid JSON file."
        else:
            return "Invalid file format. Please upload a JSON or TXT file"

        app.logger.info(data)

        try:
            # Extract the relevant data
            records = data["data"]
            metadata = data["metadata"]

            # Extract method from slicingMethod
            slicing_method_full = metadata["slicingMethod"]
            start_index = slicing_method_full.find("<")
            end_index = slicing_method_full.find(">") + 1
            if start_index != -1 and end_index != -1:
                slicing_method = slicing_method_full[start_index:end_index]
            else:
                slicing_method = ""

            # Find method info in AllRiskCategories
            # slicing_method = data["metadata"]["slicingMethod"]
            slicing_method_info = find_method_info(slicing_method)
            # Create the nodes and edges
            nodes_dict = {}
            nodes = []
            edges = []

            # Create a dictionary that maps each node to its privacyRelevance
            node_privacy_mapping = {
                record["node"]: record["privacyRelevance"] for record in records
            }

            # Create nodes for each record
            for record in records:
                # Check if the source node exists
                source_node = nodes_dict.get(record["node"])
                if source_node is None:
                    # Extract method from node
                    node_method = record["node"]
                    node_method = node_method[
                        node_method.find("<") : node_method.find(">") + 1
                    ]

                    # Check if the method in node matches root node
                    if node_method == slicing_method_info["Method"]:
                        node_risk_info = find_method_info(node_method)
                        source_node = {
                            "id": record["node"],
                            "root": "Yes",
                            "privacyRelevance": record["privacyRelevance"],
                            "toNode": record["toNode"],
                            "edgeType": record["edgeType"]
                            if record["edgeType"]
                            else "nope",
                            "riskInfo": slicing_method_info["Method"],
                            "descriptionRiskNode": slicing_method_info[
                                "Subcategory (if any)"
                            ],
                            # changed to 'Category' from Description
                            "RiskLevel": node_risk_info["RiskValue"]
                            # "RiskLevel": extract_risk_value(slicing_method_info["Label"])
                            if node_risk_info is not None
                            else "Not a privacy-relevant method",
                            # "RiskLevel": slicing_method_info["RiskValue"], # changed to 'Subcategory (if any)' from 'risk_type'
                            # "RiskLevel": extract_risk_value(slicing_method_info["Label"]),
                            "documentation_url": slicing_method_info[
                                "documentation_url"
                            ],
                        }
                    # check if the node is other than root node
                    else:
                        node_risk_info = find_method_info(node_method)
                        print(node_risk_info)
                        print(record["privacyRelevance"])
                        source_node = {
                            "id": record["node"],
                            "privacyRelevance": record["privacyRelevance"],
                            "root": "No",
                            "toNode": record["toNode"],
                            "edgeType": record["edgeType"]
                            if record["edgeType"]
                            else "nope",
                            "riskInfo": node_risk_info["Method"]
                            if node_risk_info is not None
                            else "Not a privacy-relevant method",
                            "descriptionRiskNode": node_risk_info.get(
                                "Subcategory (if any)"
                            )
                            or node_risk_info.get("Category")
                            if node_risk_info
                            else "Not a privacy-relevant method",
                            "RiskLevel": node_risk_info["RiskValue"]
                            # "RiskLevel": extract_risk_value(slicing_method_info["Label"])
                            if node_risk_info is not None
                            else "Not a privacy-relevant method",
                            "documentation_url": node_risk_info["documentation_url"]
                            if node_risk_info is not None
                            else "Documentation is not available",
                        }
                    nodes_dict[record["node"]] = source_node
                    nodes.append(source_node)

                # Check if the target node exists
                target_node = nodes_dict.get(record["toNode"])
                if target_node is None:
                    # node_risk_info = find_method_info(node_method)
                    # Use the privacyRelevance from the node_privacy_mapping for target node
                    target_privacy_relevance = node_privacy_mapping.get(
                        record["toNode"], record["privacyRelevance"]
                    )

                    target_node = {
                        "id": record["toNode"],
                        "privacyRelevance": target_privacy_relevance,
                        "edgeType": record["edgeType"],
                        "riskInfo": "Not a privacy-relevant method",
                        "descriptionRiskNode": "Not a privacy-relevant method",
                        "RiskLevel": "Not a privacy-relevant method",
                        "documentation_url": "Documentation is not available",
                    }
                    nodes_dict[record["toNode"]] = target_node
                    nodes.append(target_node)

                # Create the edge
                edge = {
                    "source": source_node["id"],
                    "target": target_node["id"],
                    "edgeType": record["edgeType"] if record["edgeType"] else "",
                }
                edges.append(edge)

            return render_template(
                "graphzoompan.html",
                nodes=json.dumps(nodes),
                edges=json.dumps(edges),
                metadata=json.dumps(metadata),
                slicing_method_info=json.dumps(slicing_method_info),
                input_data_json=json.dumps(data),
            )

        except KeyError as e:
            app.logger.error(f"Key error: {e}")
            return "Error processing data. Please ensure the file is in the correct format."

    return render_template("graphzoompan.html")


def find_method_info(slicing_method):
    """
    This function looks for information related to a slicing method in the risk categories.
    """
    print(f"Searching for: {slicing_method}")
    for risk_category, methods in app.all_risk_categories["risks"].items():
        for method_dict in methods:
            if "Method" in method_dict:
                # print(f"Checking method: {method_dict['Method']}")
                if slicing_method == method_dict["Method"]:
                    print(f"Found matching method: {method_dict['Method']}")
                    print("method", method_dict)
                    return method_dict

    print(f"Method not found in risk categories: {slicing_method}")

    return {
        "Method": slicing_method,
        "Description": "Method not found in risk categories",
        "RiskValue": "Unknown",
        "documentation_url": "Not available",
        "Category": "NA",
    }


def fetch_method_type(string):
    if "context based method" in string:
        return "Context Based Method"
    elif "identifiable method" in string:
        return "Identifiable Method"
    elif "partially identifiable method" in string:
        return "Partially Identifiable Method"
    else:
        return "Unknown"


def convert_text_to_json(text_content):
    # Split the text content into lines
    lines = text_content.split("\n")

    # Extract metadata
    method_type = fetch_method_type(lines[0].lower())
    metadata = {
        "slicingMethod": lines[0]
        .replace("Slicing from the identifiable method", "")
        .strip(),
        "slicedSDGSize": int(lines[1].strip().split()[-1]),
        "methodType": method_type,
    }

    try:
        nodes_visited_line = lines[-5].strip()
        edges_added_line = lines[-2].strip()

        if nodes_visited_line.startswith("NODES VISITED:"):
            metadata["nodesVisited"] = int(nodes_visited_line.split(":")[-1].strip())

        if edges_added_line.startswith("EDGES ADDED:"):
            metadata["edgesAdded"] = int(edges_added_line.split(":")[-1].strip())
    except IndexError:
        print("Required information not found in data.")

    # Process node data
    node_data = []
    for line in lines[3:-4]:
        line = line.strip()
        if line.startswith("["):
            node_info = line[1:-1].split("@")
            node = node_info[0]
            privacy_relevance = node_info[1].strip()

            to_node = node_info[2].strip() if len(node_info) > 2 else None
            edge_type = "@".join(node_info[3:]).strip() if len(node_info) > 3 else None

            node_data.append(
                {
                    "node": node,
                    "privacyRelevance": privacy_relevance,
                    "toNode": to_node,
                    "edgeType": edge_type,
                }
            )

    # Construct JSON data
    json_data = {"metadata": metadata, "data": node_data}

    return json_data


app.find_method_info = find_method_info

if __name__ == "__main__":
    app.run(debug=True)
