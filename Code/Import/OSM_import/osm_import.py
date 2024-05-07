# Imports GeoJSON file using GeoPandas
# WARNING: does not seem to work properly with GeoJSON export from OSM using the Overpass API;
# overlapping linestrings would cause trouble in the subsequent processing.

import geopandas as gpd
import rdflib
from rdflib import RDF, Literal
from shapely.geometry import LineString, Point
from Code.Namespaces import *


def osm_import(osm_file_path: str, short_name: str = ""):
    # Initialize RDF graph
    g = rdflib.Graph()

    # Bind the namespaces
    g.bind("gsp", GSP)
    g.bind("rsm", RSM_TOPOLOGY)
    g.bind("", WORK)

    # Load OSM data (assumed to be in GeoJSON format) with GeoPandas
    gdf = gpd.read_file(osm_file_path)

    # Assuming the 'railway' attribute is within the properties field, filter for railway lines
    railways = gdf[gdf['railway'] == 'rail']  # tagged value 'rail' designates a track

    # Process railway lines
    for index, row in railways.iterrows():
        line_uri = WORK[f"rwy_{index}"]
        # Convert geometry to WKT
        if isinstance(row.geometry, LineString) or isinstance(row.geometry, Point):
            wkt = row.geometry.wkt
        else:
            wkt = str(row.geometry)

        g.add((line_uri, RDF.type, RSM_TOPOLOGY.LinearElement))
        g.add((line_uri, RDF.type, GSP.Geometry))
        g.add((line_uri, GSP.asWKT, Literal(wkt, datatype=GSP.wktLiteral)))

    # Serialize the graph to a Turtle file
    g.serialize(
        destination=f'/Users/airymagnien/PycharmProjects/SemanticRSM/Output_files/Intermediate_files/osm_{short_name}_raw.ttl',
        format='turtle')
