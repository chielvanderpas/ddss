from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import RDFS, XSD, FOAF, OWL
from rdflib.plugins.stores import sparqlstore
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2, XML, TURTLE, JSON
from . import views


# Prefixes for queries are defined

prefix_1 = 'bot: <https://w3id.org/bot#>'
prefix_2 = ''
prefix_3 = ''


# Model 1: This model queries a SPARQL endpoint, and constructs a turtle-output with 
# the results of this query. The queries themselves are defined query1.html.

def getData1(sparql_endpoint, query_construct, query_where):
    input = SPARQLWrapper(sparql_endpoint)
    input.setQuery("""
    PREFIX """+prefix_1+"""
    # PREFIX """+prefix_2+"""
    # PREFIX """+prefix_3+"""
    CONSTRUCT { """+query_construct+""" }
    WHERE { """+query_where+""" . }
    """)
    output = input.queryAndConvert().serialize(format=TURTLE)
    return output


# Model 2: This model queries a SPARQL endpoint. It currently does not function.

m3_query_select = '*'
m3_query_where = '?Building bot:hasStorey ?Storey'

def getData2(project):
    input = SPARQLWrapper(project)
    input.setReturnFormat(JSON)
    input.setQuery("""
    PREFIX """+prefix_1+"""
    # PREFIX """+prefix_2+"""
    # PREFIX """+prefix_3+"""
    SELECT *
    WHERE { ?Building bot:hasStorey ?Storey . }
    """)
    try:
        ret = input.queryAndConvert()
        for r in ret["results"]["bindings"]:
            return r
    except Exception as e:
        return e


# Model 3: This model facilitates writing a triple to the a SPARQL endpoint. The triple
# is currently hardcoded to have 'bot' as predicate.

def getData3(project1, project2, subject, predicate, object):
    ns = Namespace("https://github.com/chielvanderpas/ddss/instance#")
    bot = Namespace('https://w3id.org/bot#')
    s = URIRef(ns+subject)
    p = URIRef(bot+predicate)
    o = URIRef(ns+object)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((project1, project2))
    input.add((
        s, p, o,
    ))
    return 'Success, added {} {} {}.'.format(s, p, o)










### UNUSED CODE ###

# def getData2(project):
    # g = Graph()
    # g.parse(project)
    # result = g.serialize(format=TURTLE)
    # return result
