from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import FOAF, DCTERMS, XSD, RDF, SDO

g = Graph()

EX = Namespace('http://example.org/')

bob = EX['Bob']
alice = EX['Alice']

# g.add((bob, RDF.type, FOAF.Person))
# g.add((alice, RDF.type, FOAF.Person))
g.add((bob, FOAF.knows, alice))

print(g.serialize(format='ttl'))