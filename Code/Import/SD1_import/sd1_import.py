import xml.etree.ElementTree as Et

import xmltodict
from rdflib import Graph
from rdflib import Namespace

from Source_data.data_folders import data_root
from cdm_namespaces import RSM_TOPOLOGY_NAMESPACE, QUDT_NAMESPACE, UNIT_NAMESPACE
from sd1_topology_import import TopologyGraph

SD1_NAMESPACE = Namespace("http://example.org/scheibenberg/")


def source_xml_file_to_dict(path: str) -> dict:
    # Et.register_namespace(prefix = "", uri=SD1_NAMESPACE)
    xml_data = Et.parse(path).getroot()
    xml_string = Et.tostring(xml_data, encoding="utf-8", method="xml")  # needed to avoid invalid token error
    sd1dict = xmltodict.parse(xml_string)
    return sd1dict


def create_bindings(_sd1_graph: Graph):
    _sd1_graph.bind('qudt', QUDT_NAMESPACE)
    _sd1_graph.bind('rsm', RSM_TOPOLOGY_NAMESPACE)
    _sd1_graph.bind('unit', UNIT_NAMESPACE)
    _sd1_graph.bind('', SD1_NAMESPACE)


def import_sd1_infra_data(infrastructure_path: str):
    sd1_infra_dict = source_xml_file_to_dict(infrastructure_path)['ns0:infrastructure']
    trackedge_dict = sd1_infra_dict['ns0:topoAreas']['ns0:topoArea']['ns0:trackEdges']['ns0:trackEdge']
    trackedge_link_dict = sd1_infra_dict['ns0:topoAreas']['ns0:topoArea']['ns0:trackEdgeLinks']['ns0:trackEdgeLink']

    # RSM import statement; not used
    # sd1_graph.add((URIRef(SD1_NAMESPACE), OWL.imports, URIRef(RSM_TOPOLOGY_NAMESPACE)))

    topology_graph = TopologyGraph(sd1_graph)
    generate_linear_elements_from_track_edges(trackedge_dict, topology_graph)
    generate_connections_from_track_edge_links(trackedge_link_dict, topology_graph)


def generate_linear_elements_from_track_edges(_trackedge_dict: dict, _topology_graph: TopologyGraph):
    for trackedge in _trackedge_dict:
        sd1id = trackedge['@id']
        length = trackedge['@length']
        unit_repr = 'qudt'
        _topology_graph.add_trackedge_as_linearelement(sd1id, length, SD1_NAMESPACE, unit_repr)
    _topology_graph.create_ports()


def generate_connections_from_track_edge_links(_trackedge_link_dict: dict, _topology_graph: TopologyGraph):
    for trackedge_link in _trackedge_link_dict:
        trackedge_a = trackedge_link['@trackEdgeA']
        trackedge_b = trackedge_link['@trackEdgeB']
        position_on_a = 0 if trackedge_link['@startOfA'] == "true" else 1
        position_on_b = 0 if trackedge_link['@startOfB'] == "true" else 1
        _topology_graph.add_connection(trackedge_a, position_on_a, trackedge_b, position_on_b, SD1_NAMESPACE)


if __name__ == '__main__':
    sd1_graph = Graph()
    create_bindings(sd1_graph)
    infra_path = data_root + "/scheibenberg/infra_v0.4.2.xml"
    import_sd1_infra_data(infra_path)
    sd1_graph.print()
