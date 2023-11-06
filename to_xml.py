import json
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
from collections import defaultdict

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_generation(key, dependencies_dict, cache):
    """Recursive function to determine the generation of a node based on its dependencies."""
    if key in cache:
        return cache[key]
    if key not in dependencies_dict or not dependencies_dict[key]:
        cache[key] = 1
        return 1
    generation = max(get_generation(dep, dependencies_dict, cache) for dep in dependencies_dict[key]) + 1
    cache[key] = generation
    return generation

# Load the JSON data
with open('science.json', 'r', encoding='utf-8') as file:
    science_data = json.load(file)

# Create a dictionary to store dependencies for each key
dependencies_dict = {item["key"]: item.get("dependencies", []) for item in science_data}

# Determine the "generation" for each key
generations = {}
for item in science_data:
    generations[item["key"]] = get_generation(item["key"], dependencies_dict, {})

# Sort the items first by generation, then by "sortWeight"
science_data.sort(key=lambda x: (generations[x["key"]], x.get("sortWeight", 0)))

# Create the base XML structure for draw.io
mxfile = Element('mxfile', host="app.diagrams.net", modified="2023-11-06T12:47:49.475Z", agent="5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", etag="1QcJdoTkEXw8NMiF-aaI", version="20.8.19", type="github")
diagram = SubElement(mxfile, 'diagram', name="Science Tree", id="TRZrNrSoRNPHeesHGA9Z")
mxGraphModel = SubElement(diagram, 'mxGraphModel', dx="1434", dy="790", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="827", pageHeight="1169", math="0", shadow="0")
root = SubElement(mxGraphModel, 'root')

# Create default cells
SubElement(root, 'mxCell', id="0")
SubElement(root, 'mxCell', id="1", parent="0")

# Counters for x and y positions
x_counter = defaultdict(int)
y_pos = 100

# Loop through each item in the science_data to create the XML structure for nodes
for index, item in enumerate(science_data):
    requirements = "\n ".join([f"{req['type']}:{req.get('amount', '')}" for req in item.get("itemRequirements", [])])
    node_value = "<b>" + item["key"].replace("pipliz.", "") + "</b>\n" + requirements
    node = SubElement(root, 'mxCell', id=item["key"], value=node_value, style="rounded=0;whiteSpace=wrap;html=1;", vertex="1", parent="1")
    x_pos = 150 + x_counter[generations[item["key"]]] * 200
    geometry = SubElement(node, 'mxGeometry', x=str(x_pos), y=str(y_pos * generations[item["key"]]), width="120", height="60")
    geometry.set('as', 'geometry')
    x_counter[generations[item["key"]]] += 1

# Create dependencies as edges
for item in science_data:
    if "dependencies" in item:
        for dep in item["dependencies"]:
            edge = SubElement(root, 'mxCell', value="", style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;", edge="1", parent="1", source=dep, target=item["key"])
            geometry = SubElement(edge, 'mxGeometry', relative="1")
            geometry.set('as', 'geometry')

# Convert to pretty-printed XML string and save to file
xml_result = prettify(mxfile)
with open('output.xml', 'w', encoding='utf-8') as xml_file:
    xml_file.write(xml_result)
