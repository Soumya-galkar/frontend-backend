# from utils.superbase_client import supabase


# def get_graph(equipment_name):

#     # Find equipment node
#     equipment = (
#         supabase
#         .table("graph_nodes")
#         .select("*")
#         .eq("node_type", "Equipment")
#         .eq("node_name", equipment_name)
#         .single()
#         .execute()
#     )

#     if not equipment.data:
#         return None

#     equipment_id = equipment.data["id"]

#     # Find all outgoing edges
#     edges = (
#         supabase
#         .table("graph_edges")
#         .select("*")
#         .eq("source_node", equipment_id)
#         .execute()
#     )
#     # Find all incoming edges

#     edges= (
#         supabase
#         .table("graph_edges")
#         .select("*")
#         .eq("target_node",equipment_id)
#         .execute()
#     )
#     graph = []

#     for edge in edges.data:

#         node = (
#             supabase
#             .table("graph_nodes")
#             .select("*")
#             .eq("id", edge["target_node"])
#             .single()
#             .execute()
#         )

#         graph.append({

#             "relationship": edge["relationship"],

#             "node_type": node.data["node_type"],

#             "node_name": node.data["node_name"]

#         })

#         # new logic for graph building
# nodes = [
#     {
#         "id": equipment_id,
#         "position": {"x": 400, "y": 250},
#         "data": {"label": equipment_name}
#     }
# ]

# edges = []

#         nodes.append({
#            "id": node.data["id"],
#             "position": {
#             "x": 150,
#             "y": 100 * len(nodes)
#     },
#     "data": {
#         "label": node.data["node_name"]
#     }
# })
 
#         edges.append({
#             "id":edge["id"],
#             "source":equipment_id,
#             "target":node.data["id"],
#             "lable":edge["relationship"]
#  })

#     return {
#          "nodes":nodes,
#          "edges":edges
#     }
#     # return graph

from utils.superbase_client import supabase


def get_graph(equipment_name):

    # Find equipment node
    equipment = (
        supabase
        .table("graph_nodes")
        .select("*")
        .eq("node_type", "Equipment")
        .eq("node_name", equipment_name)
        .single()
        .execute()
    )

    if not equipment.data:
        return None

    equipment_id = equipment.data["id"]

    # Outgoing edges
    outgoing = (
        supabase
        .table("graph_edges")
        .select("*")
        .eq("source_node", equipment_id)
        .execute()
    ).data

    # Incoming edges
    incoming = (
        supabase
        .table("graph_edges")
        .select("*")
        .eq("target_node", equipment_id)
        .execute()
    ).data

    all_edges = outgoing + incoming

    # Equipment node (center)
    nodes = [
        {
            "id": equipment_id,
            "position": {"x": 400, "y": 250},
            "data": {"label": equipment_name},
        }
    ]

    react_edges = []

    added_nodes = {equipment_id}

    y = 100

    for edge in all_edges:

        # Determine the other node
        if edge["source_node"] == equipment_id:
            other_node_id = edge["target_node"]
            source = equipment_id
            target = other_node_id
        else:
            other_node_id = edge["source_node"]
            source = other_node_id
            target = equipment_id

        node = (
            supabase
            .table("graph_nodes")
            .select("*")
            .eq("id", other_node_id)
            .single()
            .execute()
        )

        node = node.data

        if node["id"] not in added_nodes:
            nodes.append({
                "id": node["id"],
                "position": {
                    "x": 150,
                    "y": y
                },
                "data": {
                    "label": node["node_name"]
                }
            })

            added_nodes.add(node["id"])
            y += 120

        react_edges.append({
            "id": edge["id"],
            "source": source,
            "target": target,
            "label": edge["relationship"]
        })

    return {
        "nodes": nodes,
        "edges": react_edges
    }