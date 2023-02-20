import networkx as nx
import matplotlib.pyplot as plt
from urllib import request, parse
import json

SERVICE_URL = "http://localhost:7000"

def get_skills():
    req = request.Request(f'{SERVICE_URL}/skill/list', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def normalize_skill_name(skill_name):
    return skill_name.lower().replace(" ", "").replace("-", "").replace("*", "").replace("/", "").replace(".", "").strip()

G = nx.DiGraph()

skills = get_skills()
edges = []

norm_map = {}
for skill_name in skills:
    norm_map[normalize_skill_name(skill_name)] = skill_name

for skill_name in skills:
    skill_data = skills[skill_name]
    parent = skill_data["parent"]
    if parent is None:
        continue
    if type(parent) != list:
        parent = [parent]
    for item in parent:
        if item not in norm_map:
            print(f"[skill-mismatch]: {item}")
            exit(0)
    print([ (norm_map[item], skill_name) for item in parent ])
    edges.extend([ (norm_map[item], skill_name) for item in parent ])

selected_edges = []
root = "FrontEnd"
queue = [root]
used_map = {}
while len(queue) > 0:
    front = queue[0]
    queue.remove(front)
    if front in used_map:
        continue
    used_map[front] = True
    queue.extend([ item[1] for item in filter(lambda y: y[0] == front, edges)])
    selected_edges.extend([ item for item in filter(lambda y: y[0] == front, edges)])
print(selected_edges)

G.add_edges_from(selected_edges)

val_map = {'A': 1.0,
           'D': 0.5714285714285714,
           'H': 0.0}

values = [val_map.get(node, 0.25) for node in G.nodes()]

# Specify the edges you want here
# red_edges = [('A', 'C'), ('E', 'C')]
# edge_colours = ['black' if not edge in red_edges else 'red'
#                 for edge in G.edges()]
# black_edges = [edge for edge in G.edges() if edge not in red_edges]
black_edges = [edge for edge in G.edges()]

# Need to create a layout when doing
# separate calls to draw nodes and edges
# pos = nx.spring_layout(G)
pos = nx.arf_layout(G)
nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), 
                       node_color = values, node_size = 900, node_shape='s')
nx.draw_networkx_labels(G, pos, font_size=7, font_color="#ffffff")
# nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='r', arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=True)
plt.show()
