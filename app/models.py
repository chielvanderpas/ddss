from hashlib import sha3_224
from pickle import TRUE
from re import X
from xml.dom.minidom import Document
from django.forms import DateTimeField
from pyparsing import punc8bit
from rdflib import Graph, URIRef, BNode, Literal, Namespace, Dataset
from rdflib.namespace import RDFS, XSD, FOAF, OWL, RDF
from rdflib.plugins.stores import sparqlstore
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2, XML, TURTLE, JSON
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.conf import settings
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import string, random, collections
import ifcopenshell

######################################
### Gebruikte packages ###############
######################################

# rdflib
# ifcopenshell

######################################
### Global semantic web namespaces ###
######################################

o_ddss = 'https://github.com/chielvanderpas/ddss#'
ns_ddss = Namespace(o_ddss)
nss_ddss = 'ddss: <https://github.com/chielvanderpas/ddss#>'

o_rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
ns_rdf = Namespace(o_rdf)
nss_rdf = 'rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'

o_bot = 'https://w3id.org/bot#'
ns_bot = Namespace(o_bot)
nss_bot = 'bot: <https://w3id.org/bot#>'

o_org = 'http://www.w3.org/ns/org#'
ns_org = Namespace(o_org)
nss_org = 'org: <http://www.w3.org/ns/org#>'

o_foaf = 'http://xmlns.com/foaf/0.1/'
ns_foaf = Namespace(o_foaf)
nss_foaf = 'foaf: <http://xmlns.com/foaf/0.1/>'

#######################################
### Specific semantic web instances ###
#######################################

o_oms = 'https://github.com/chielvanderpas/oms#'
ns_oms = Namespace(o_oms)
nss_oms = 'oms: <https://github.com/chielvanderpas/oms#>'

###############################################################
### Connected SPARQL endpoints & document storage locations ###
###############################################################

sparql_endpoint_1 = settings.SPARQL_ENDPOINT_1
sparql_endpoint_2 = settings.SPARQL_ENDPOINT_2
document_storage_location = settings.MEDIA_ROOT
aim_default_namespace = settings.AIM_DEFAULT_NAMESPACE

####################
### Setup models ###
####################

def model_write_ontology():
    ontology = Graph()
    ontology.parse('ddss/app/ontology/DDSS_ontology.ttl')
    output = ontology.serialize(format=TURTLE)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    return output
    # input = sparqlstore.SPARQLUpdateStore()
    # input.open((sparql_endpoint_1, sparql_endpoint_2))
    # for s, p, o in ontology.quads((None, RDF.type, None, None)):
    #     input.add((
    #         s, p, o
    #     ))

#############################
### Authentication models ###
#############################

def login_model(request, input_username, input_password):
    user = authenticate(username=input_username, password=input_password)
    if user is not None:
        login(request, user)
        return 'success'
    else:
        error_message = 'These credentials are incorrect, please try again.'
        return error_message

def rq_user_id(username):
        user_rev = str(f"'{username}'")
        input = sparqlstore.SPARQLUpdateStore()
        input.open((sparql_endpoint_1))
        q = """
        PREFIX """+nss_bot+"""
        PREFIX """+nss_ddss+"""
        PREFIX """+nss_rdf+"""
        PREFIX """+nss_org+"""
        PREFIX """+nss_foaf+"""
        PREFIX """+nss_oms+"""
        SELECT ?user
        WHERE {
            ?user rdf:type ddss:Actor .
            ?user ddss:hasEmailAddress ?email .
            VALUES ?email {
                """+user_rev+"""
            }
        }
        """
        result = input.query(q)
        for row in result:
            user_id = str(f"{row.user}")
            user_id_rev = user_id.replace(o_oms, '')
        return user_id_rev

def register_model(username, email, password, first_name, last_name, phone_number):
    user = User.objects.create_user(username, email, password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    unique_user_id = BNode()
    predicate1 = 'type'
    object1 = 'Actor'
    s1 = URIRef(ns_oms+unique_user_id)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'hasName'
    full_name = str(first_name+' '+last_name)
    s2 = URIRef(ns_oms+unique_user_id)
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(full_name)
    predicate3 = 'hasEmailAddress'
    s3 = URIRef(ns_oms+unique_user_id)
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(email)
    predicate4 = 'hasPhoneNumber'
    s4 = URIRef(ns_oms+unique_user_id)
    p4 = URIRef(ns_ddss+predicate4)
    o4 = Literal(phone_number)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s1, p1, o1,
    ))
    input.add((
        s2, p2, o2,
    ))
    input.add((
        s3, p3, o3,
    ))
    input.add((
        s4, p4, o4,
    ))

def logout_model(request):
    logout(request)

#######################
### settings_models ###
#######################

def rq_settings1(email):
    email_rev = str(f"'{email}'")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    SELECT ?phone_number
    WHERE {
        ?user rdf:type ddss:Actor .
        ?user ddss:hasEmailAddress ?email .
        VALUES ?email {
            """+email_rev+"""
        }
        ?user ddss:hasPhoneNumber ?phone_number .
    }
    """
    result = input.query(q)
    for row in result:
        phone_number = str(f"{row.phone_number}")
    return phone_number

###########################
### Data request models ###
###########################

### data request models: create custom sparql query ###

def rq_sparql_query(query):
    o_xxx = 'bladiebla'
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    """+query+"""
    """
    result = input.query(q)
    output = []
    for row in result:
        triple = str(f"{row}")
        triple_rev = triple.replace('rdflib.term.URIRef(', '').replace('rdflib.term.Literal(', '').replace('(', '').replace(')', '')
        output.append(triple_rev)
    return output

### data request models: aims ###

def rq_aim_bot(aim_namespace):
    nss_aim = str('aim: <'+aim_namespace+'>')
    aim_rev = str(f"<{aim_namespace}>")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?aim ?aim_name ?bot ?bot_type ?bot_name
    WHERE {
        ?aim rdf:type ddss:AIM .
        VALUES ?aim {
            """+aim_rev+"""
        }
        ?aim ddss:hasModelName ?aim_name .
        ?bot rdf:type ?bot_type .
        VALUES ?bot_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        ?bot ddss:partOf ?aim .
        ?bot ddss:hasName ?bot_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['aim', 'aim_name', 'bot', 'bot_type', 'bot_name'])
    output = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        bot = row.bot.replace(aim_namespace, '')
        bot_type = row.bot_type.replace(o_bot, '')
        bot_name = row.bot_name.replace(aim_namespace, '')
        output.append(namedlist(aim, aim_name, bot, bot_type, bot_name))
    return output

def rq_aim_documents(aim_namespace):
    nss_aim = str('aim: <'+aim_namespace+'>')
    aim_rev = str(f"<{aim_namespace}>")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?aim ?aim_name ?document ?doc_type ?doc_name
    WHERE {
        ?aim rdf:type ddss:AIM .
        VALUES ?aim {
            """+aim_rev+"""
        }
        ?aim ddss:hasModelName ?aim_name .
        ?document rdf:type ?doc_type .
        VALUES ?doc_type {
            ddss:IFC
            ddss:PDF
            ddss:CSV
            ddss:PNG
            ddss:JPEG
            ddss:PCD
            ddss:TXT
            ddss:IFC2x3
            ddss:IFC4
        }
        ?document ddss:partOf ?aim .
        ?document ddss:hasFileName ?doc_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['aim', 'aim_name', 'document', 'doc_type', 'doc_name'])
    output = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        document = row.document.replace(aim_namespace, '')
        doc_type = row.doc_type.replace(o_ddss, '')
        doc_name = row.doc_name.replace('', '')
        output.append(namedlist(aim, aim_name, document, doc_type, doc_name))
    return output

def rq_aim_events(aim_namespace):
    nss_aim = str('aim: <'+aim_namespace+'>')
    aim_rev = str(f"<{aim_namespace}>")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?aim ?aim_name ?event ?event_type ?event_startdatetime ?event_description
    WHERE {
        ?aim rdf:type ddss:AIM .
        VALUES ?aim {
            """+aim_rev+"""
        }
        ?aim ddss:hasModelName ?aim_name .
        ?event rdf:type ?event_type .
        VALUES ?event_type {
            ddss:Maintenance
            ddss:Survey
            ddss:Operations
            ddss:Inspections
            ddss:Renewal
            ddss:Refurbish
            ddss:EndOfLife
            ddss:Acquire
        } 
        ?event ddss:partOf ?aim .
        ?event ddss:startedAt ?event_startdatetime .
        ?event ddss:hasDescription ?event_description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['aim', 'aim_name', 'event', 'event_type', 'event_startdatetime', 'event_description'])
    output = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        event = row.event.replace(aim_namespace, '')
        event_type = row.event_type.replace(o_ddss, '')
        event_startdatetime = row.event_startdatetime.replace('', '')
        event_description = row.event_description.replace('', '')
        output.append(namedlist(aim, aim_name, event, event_type, event_startdatetime, event_description))
    return output

### data request models: instance models ###

def rq_event1(aim_namespace, instance): 
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?event ?type ?startdatetime ?enddatetime ?description ?subevent ?actor ?actor_name
    WHERE {
        ?event rdf:type ?type .
        VALUES ?event {
        	aim:"""+instance+"""
    	}
        VALUES ?type {
            ddss:Maintenance
            ddss:Survey
            ddss:Operations
            ddss:Inspections
            ddss:Renewal
            ddss:Refurbish
            ddss:EndOfLife
            ddss:Acquire
        } 
        ?event ddss:startedAt ?startdatetime .
        ?event ddss:hasDescription ?description .
        OPTIONAL {
            ?event ddss:hasSubEvent ?subevent .
            ?event ddss:endedAt ?enddatetime .
        }
        ?event ddss:involves ?actor .
        ?actor ddss:hasName ?actor_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'type', 'startdatetime', 'enddatetime', 'description', 'subevent', 'actor', 'actor_name'])
    output = []
    for row in result:
        id = row.event.replace(aim_namespace, '')
        type = row.type.replace(o_ddss, '')
        startdatetime = row.startdatetime
        enddatetime = row.enddatetime
        description = row.description
        if row.subevent is not None:
            subevent = row.subevent.replace(aim_namespace, '')
        else:
            subevent = str('')
        actor = row.actor.replace(o_oms, '')
        actor_name = row.actor_name
        output.append(namedlist(id, type, startdatetime, enddatetime, description, subevent, actor, actor_name))
    return output

def rq_actor1(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?actor ?name ?email ?phone_number
    WHERE {
        ?actor rdf:type ddss:Actor .
        VALUES ?actor {
        	aim:"""+instance+"""
    	}
        ?actor ddss:hasName ?name .
        ?actor ddss:hasEmailAddress ?email .
        ?actor ddss:hasPhoneNumber ?phone_number .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'name', 'email', 'phone_number'])
    output = []
    for row in result:
        id = row.actor
        id_rev = id.replace(o_ddss, '')
        name = row.name
        email = row.email
        phone_number = row.phone_number
        output.append(namedlist(id_rev, name, email, phone_number))
    return output

########################
### Data drop models ###
########################

### Data drop: check if existing data drop can be used ###

def dd_check_session_duration(current_dd_start_time):
    if current_dd_start_time != None:
        current_dd_start_time_rev = datetime.strptime(current_dd_start_time, '%Y-%m-%dT%H:%M')
        current_datetime = datetime.now()
        difference = current_datetime-current_dd_start_time_rev
        difference_in_minutes = difference.total_seconds() / 60
        if difference_in_minutes < 120:
            return True
        else:
            return False
    else:
        return False

### Data drop: select existing AIM ###

def rq_aim():    
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    SELECT ?namespace ?name
    WHERE {
        ?namespace rdf:type ddss:AIM .
        ?namespace ddss:hasModelName ?name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['namespace', 'name'])
    output = []
    for row in result:
        namespace = row.namespace
        name = row.name
        output.append(namedlist(namespace, name))
    return output

### Data drop: create new AIM ###

def dd_new_aim(aim_name):
    aim_default_namespace
    unique_aim_id = BNode()
    hashtag = '#'
    aim_namespace = aim_default_namespace+unique_aim_id+hashtag
    predicate1 = 'type'
    object1 = 'AIM'
    s1 = URIRef(aim_namespace)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'hasModelName'
    s2 = URIRef(aim_namespace)
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(aim_name)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s1, p1, o1,
    ))
    input.add((
        s2, p2, o2,
    ))
    return aim_namespace

### Data drop: create data drop ###

def dd_create(o_aim, user_id):
    ns_aim = Namespace(o_aim)
    unique_dd_id = BNode()
    predicate1 = 'type'
    object1 = 'DataDrop'
    s1 = URIRef(ns_aim+unique_dd_id)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'uploadedBy'
    user_id_rev = str(f"{user_id}")
    s2 = URIRef(ns_aim+unique_dd_id)
    p2 = URIRef(ns_ddss+predicate2)
    o2 = URIRef(ns_oms+user_id_rev)
    predicate3 = 'occurredAt'
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M")
    s3 = URIRef(ns_aim+unique_dd_id)
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(current_datetime)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s1, p1, o1,
    ))
    input.add((
        s2, p2, o2,
    ))
    input.add((
        s3, p3, o3,
    ))
    return unique_dd_id

### Data drop: add event ###

def rq_event2(o_aim):
    nss_aim = str('aim: <'+o_aim+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?event ?type ?startdatetime ?description
    WHERE {
        ?event rdf:type ?type .
        VALUES ?type {
            ddss:Maintenance
            ddss:Survey
            ddss:Operations
            ddss:Inspections
            ddss:Renewal
            ddss:Refurbish
            ddss:EndOfLife
            ddss:Acquire
        } 
        ?event ddss:startedAt ?startdatetime .
        ?event ddss:hasDescription ?description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'list_text'])
    output = []
    for row in result:
        list_text = str(f"{row.type} | {row.startdatetime} | {row.description} | id: {row.event}")
        list_text_rev = list_text.replace(o_ddss, '').replace(o_aim, '')
        id = row.event
        id_rev = id.replace(o_aim, '')
        output.append(namedlist(id_rev, list_text_rev))
    return output

def rq_event3(o_aim):
    nss_aim = str('aim: <'+o_aim+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?name ?email ?user
    WHERE {
        ?user rdf:type ddss:Actor .
        ?user ddss:hasName ?name .
        ?user ddss:hasEmailAddress ?email .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['name', 'email', 'id'])
    output = []
    for row in result:
        name = row.name
        email = row.email
        id = row.user
        id_rev = id.replace(o_oms, '')
        output.append(namedlist(name, email, id_rev))
    return output

def dd_event1(o_aim, event_type, event_description, startdatetime, enddatetime, related_actor, super_event, unique_dd_id):
    ns_aim = Namespace(o_aim)
    unique_event_id = BNode()
    s = URIRef(ns_aim+unique_event_id)
    predicate1 = 'type'
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+event_type)
    predicate2 = 'hasDescription'
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(event_description)
    predicate3 = 'startedAt'
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(startdatetime)
    predicate4 = 'endedAt'
    p4 = URIRef(ns_ddss+predicate4)
    o4 = Literal(enddatetime)
    predicate5 = 'involves'
    p5 = URIRef(ns_ddss+predicate5)
    o5 = URIRef(ns_oms+related_actor)
    if super_event != None:
        predicate6 = 'hasSubEvent'
        s6 = URIRef(ns_aim+super_event)
        p6 = URIRef(ns_ddss+predicate6)
        o6 = s
    predicate7 = 'relatesToEvent'
    s7 = URIRef(ns_aim+unique_dd_id)
    p7 = URIRef(ns_ddss+predicate7)
    o7 = s
    predicate8 = 'partOf'
    p8 = URIRef(ns_ddss+predicate8)
    o8 = URIRef(o_aim)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s, p1, o1,
    ))
    input.add((
        s, p2, o2,
    ))
    input.add((
        s, p3, o3,
    ))
    if enddatetime != "":
        input.add((
            s, p4, o4,
        ))
    input.add((
        s, p5, o5,
    ))
    if super_event != None:
        input.add((
            s6, p6, o6,
        ))
    input.add((
        s7, p7, o7,
    ))
    input.add((
        o7, p7, s7,
    ))
    input.add((
        s, p8, o8,
    ))
    return 'Success, added {} as an event with unique ID {}.'.format(event_type, unique_event_id)

def dd_event2(o_aim, unique_dd_id, unique_event_id):
    ns_aim = Namespace(o_aim)
    predicate1 = 'relatesToEvent'
    s1 = URIRef(ns_aim+unique_dd_id)
    p1 = URIRef(ns_ddss+predicate1)
    o1 = URIRef(ns_aim+unique_event_id)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s1, p1, o1,
    ))
    return 'Success, selected the event with unique ID {}.'.format(unique_event_id)

### Data drop: upload document: check for previous versions ###

def dd_prev_version_check(file_exists_check, o_aim):
    prev_version = file_exists_check[-1]
    prev_version_rev = str(f"'{prev_version}'")
    prev_location = str(document_storage_location+'/'+prev_version)
    prev_location_rev = str(f"'{prev_location}'")
    nss_aim = str('aim: <'+o_aim+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?document ?document_status
    WHERE {
        ?document rdf:type ?doc_type .
        VALUES ?doc_type {
            ddss:IFC
            ddss:PDF
            ddss:CSV
            ddss:PNG
            ddss:JPEG
            ddss:PCD
            ddss:TXT
            ddss:IFC2x3
            ddss:IFC4
        }
        ?document ddss:hasFileName ?filename .
        VALUES ?filename {
            """+prev_version_rev+"""
        }
        ?document ddss:locatedAt ?location .
        VALUES ?location {
            """+prev_location_rev+"""
        }
        OPTIONAL {
        ?document ddss:hasStatus ?document_status .
        }
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['document_id', 'document_status'])
    output = []
    for row in result:
        document_id = row.document
        document_id_rev = document_id.replace(o_aim, '')
        document_status = row.document_status
        if document_status != None:
            document_status_rev = document_status.replace(o_ddss, '')
        else:
            document_status_rev = ''
        output.append(namedlist(document_id_rev, document_status_rev))
    return output

### Data drop: upload document: upload document ###

def dd_document1(o_aim, file_name, file_type, file_location, copy_name, copy_type, copy_location, prev_version):
    ns_aim = Namespace(o_aim)
    unique_document_id = BNode()
    s = URIRef(ns_aim+unique_document_id)
    predicate1 = 'type'
    if file_type == 'ifc':
        object1 = 'IFC'
    elif file_type == 'pdf':
        object1 = 'PDF'
    elif file_type == 'csv':
        object1 = 'CSV'
    elif file_type == 'png':
        object1 = 'PNG'
    elif file_type == 'jpg' or file_type == 'jpeg':
        object1 = 'JPEG'
    elif file_type == 'pcd':
        object1 = 'PCD'
    elif file_type == 'txt':
        object1 = 'TXT'
    else:
        return 'Error! File type is not accepted.'
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'hasFileName'
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(file_name)
    predicate3 = 'locatedAt'
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(file_location)
    predicate4 = 'partOf'
    p4 = URIRef(ns_ddss+predicate4)
    o4 = URIRef(o_aim)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s, p1, o1,
    ))
    input.add((
        s, p2, o2,
    ))
    input.add((
        s, p3, o3,
    ))
    input.add((
        s, p4, o4,
    ))
    namedlist = collections.namedtuple('namedlist', ['id', 'file_type', 'file_name', 'storage_location', 'copy_id', 'copy_file_type', 'copy_file_name', 'copy_storage_location', 'prev_version_id', 'prev_version_status'])
    output = []
    empty_field = ''
    if copy_name != '':
        unique_copy_id = BNode()
        predicate5 = 'hasCopy'
        p5 = URIRef(ns_ddss+predicate5)
        o5 = URIRef(ns_aim+unique_copy_id)
        predicate6 = 'hasFileFormat'
        s6 = URIRef(ns_aim+unique_copy_id)
        p6 = URIRef(ns_ddss+predicate6)
        o6 = Literal(copy_type)
        predicate7 = 'hasFileName'
        s7 = URIRef(ns_aim+unique_copy_id)
        p7 = URIRef(ns_ddss+predicate7)
        o7 = Literal(copy_name)
        predicate8 = 'locatedAt'
        s8 = URIRef(ns_aim+unique_copy_id)
        p8 = URIRef(ns_ddss+predicate8)
        o8 = Literal(copy_location)
        input.add((
            s, p5, o5,
        ))
        input.add((
            s6, p6, o6,
        ))
        input.add((
            s7, p7, o7,
        ))
        input.add((
            s8, p8, o8,
        ))
    if prev_version != None:
        for document in prev_version:
            prev_version_id = document.document_id
            prev_version_status = document.document_status
    else:
        prev_version_id = ''
        prev_version_status = ''
    if prev_version_id != '':
        predicate9 = 'hasPreviousVersion'
        p9 = URIRef(ns_ddss+predicate9)
        o9 = URIRef(ns_aim+prev_version_id)
        input.add((
            s, p9, o9,
        ))
    if copy_name == None and prev_version_id == '':
        output.append(namedlist(unique_document_id, file_type, file_name, file_location, empty_field, empty_field, empty_field, empty_field, empty_field, empty_field))
    if copy_name == None and prev_version_id != '':
        output.append(namedlist(unique_document_id, file_type, file_name, file_location, empty_field, empty_field, empty_field, empty_field, prev_version_id, prev_version_status))
    if copy_name != None and prev_version_id == '':
        output.append(namedlist(unique_document_id, file_type, file_name, file_location, unique_copy_id, copy_type, copy_name, copy_location, empty_field, empty_field))
    if copy_name != None and prev_version_id != '':
        output.append(namedlist(unique_document_id, file_type, file_name, file_location, unique_copy_id, copy_type, copy_name, copy_location, prev_version_id, prev_version_status))
    return output

### Data drop: upload document: enrich metadata ###

def dd_document2(o_aim, unique_dd_id, unique_document_id, document_description, document_unique_identifier, document_creation_software, document_creation_software_version, preservation_until_date, content_type_documentation, content_type_geometrical, content_type_alphanumerical, document_status, prev_version_id, prev_version_status, responsible_actor):
    ns_aim = Namespace(o_aim)
    s = URIRef(ns_aim+unique_document_id)
    predicate1 = 'hasDescription'
    p1 = URIRef(ns_ddss+predicate1)
    o1 = Literal(document_description)
    predicate2 = 'hasUniqueIdentifier'
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(document_unique_identifier)
    predicate3 = 'hasCreationSoftware'
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(document_creation_software)
    predicate4 = 'hasCreationSoftwareVersion'
    p4 = URIRef(ns_ddss+predicate4)
    o4 = Literal(document_creation_software_version)
    predicate5 = 'hasPreservationUntilDate'
    p5 = URIRef(ns_ddss+predicate5)
    o5 = Literal(preservation_until_date)
    predicate6 = 'hasStatus'
    p6 = URIRef(ns_ddss+predicate6)
    o6 = URIRef(ns_ddss+document_status)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s, p1, o1,
    ))
    input.add((
        s, p2, o2,
    ))
    input.add((
        s, p3, o3,
    ))
    input.add((
        s, p4, o4,
    ))
    input.add((
        s, p5, o5,
    ))
    input.add((
        s, p6, o6,
    ))
    predicate7 = 'hasContentType'
    p7 = URIRef(ns_ddss+predicate7)
    if content_type_documentation == 'content_type_documentation_true':
        content_type_documentation = 'Documentation'
        o7a = URIRef(ns_ddss+content_type_documentation)
        input.add((
            s, p7, o7a,
        ))
    if content_type_geometrical == 'content_type_geometrical_true':
        content_type_geometrical = 'GeometricalInformation'
        o7b = URIRef(ns_ddss+content_type_geometrical)
        input.add((
            s, p7, o7b,
        ))
    if content_type_alphanumerical == 'content_type_alphanumerical_true':
        content_type_alphanumerical = 'AlphanumericalInformation'
        o7c = URIRef(ns_ddss+content_type_alphanumerical)
        input.add((
            s, p7, o7c,
        ))
    document_interaction_id = BNode()
    predicate8 = 'ConcernsDocument'
    s8 = URIRef(ns_aim+document_interaction_id)
    p8 = URIRef(ns_ddss+predicate8)
    o8 = s
    input.add((
            s8, p8, o8,
        ))
    if prev_version_status != None and prev_version_status != document_status:
        predicate9 = 'type'
        object9 = 'StatusChange'
        s9 = s8
        p9 = URIRef(ns_rdf+predicate9)
        o9 = URIRef(ns_ddss+object9)
        input.add((
            s9, p9, o9,
        ))
    if prev_version_id != None:
        predicate10 = 'type'
        object10 = 'Edit'
        s10 = s8
        p10 = URIRef(ns_rdf+predicate10)
        o10 = URIRef(ns_ddss+object10)
        input.add((
            s10, p10, o10,
        ))
    else:
        predicate11 = 'type'
        object11 = 'Creation'
        s11 = s8
        p11 = URIRef(ns_rdf+predicate11)
        o11 = URIRef(ns_ddss+object11)
        input.add((
            s11, p11, o11,
        ))
    predicate12 = 'Contains'
    s12 = URIRef(ns_aim+unique_dd_id)
    p12 = URIRef(ns_ddss+predicate12)
    o12 = s8
    input.add((
        s12, p12, o12,
    ))
    predicate13 = 'hasResponsibleActor'
    s13 = s8
    p13 = URIRef(ns_ddss+predicate13)
    o13 = URIRef(ns_oms+responsible_actor)
    input.add((
        s13, p13, o13,
    ))
        
def rq_ifc1(o_aim, document_storage_location):
    model = ifcopenshell.open(document_storage_location)
    namedlist = collections.namedtuple('namedlist', ['type', 'guid', 'name', 'longname', 'description'])
    model_data = []
    ifcsites = model.by_type('IFCSITE')
    for site in ifcsites:
        type = 'Site'
        guid = site.GlobalId
        name = site.Name
        long_name = site.LongName
        description = site.Description
        model_data.append(namedlist(type, guid, name, long_name, description))
    ifcbuildings = model.by_type('IFCBUILDING')
    for building in ifcbuildings:
        type = 'Building'
        guid = building.GlobalId
        name = building.Name
        long_name = building.LongName
        description = building.Description
        model_data.append(namedlist(type, guid, name, long_name, description))
    ifcbuildingstoreys = model.by_type('IFCBUILDINGSTOREY')
    for storey in ifcbuildingstoreys:
        type = 'Storey'
        guid = storey.GlobalId
        name = storey.Name
        long_name = storey.LongName
        description = storey.Description
        model_data.append(namedlist(type, guid, name, long_name, description))
    ifcspaces = model.by_type('IFCSPACE')
    for space in ifcspaces:
        type = 'Space'
        guid = space.GlobalId
        name = space.Name
        long_name = space.LongName
        description = space.Description
        model_data.append(namedlist(type, guid, name, long_name, description))
    # ifcelements = model.by_type('IFCELEMENT')
    # for element in ifcelements:
    #     type = 'Element'
    #     guid = element.GlobalId
    #     name = element.Name
    #     long_name = element.Tag
    #     description = element.Description
    #     model_data.append(namedlist(type, guid, name, long_name, description))
    nss_aim = str('aim: <'+o_aim+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?bot ?bot_type ?guid ?name ?longname ?description
    WHERE {
        ?bot rdf:type ?bot_type .
        VALUES ?bot_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
            }
        OPTIONAL {
            ?bot ddss:hasGuid ?guid .
            }
        OPTIONAL {
            ?bot ddss:hasName ?name .
            }
        OPTIONAL {
            ?bot ddss:hasLongName ?longname .
            }
        OPTIONAL {
            ?bot ddss:hasDescription ?description .
            }
    }
    """
    result = input.query(q)
    existing_data = []
    for row in result:
        uri = row.bot
        type = row.bot_type
        if type != None:
            type_rev1 = type.replace('rdflib.term.URIRef(', '')
            type_rev2 = type_rev1.replace("https://w3id.org/bot#", "")
            type_rev3 = type_rev2.replace(')', '')
        else:
            type_rev2 = type
        guid = row.guid
        if guid != None:
            guid_rev1 = guid.replace('rdflib.term.Literal(', '')
            guid_rev2 = guid_rev1.replace(')', '')
        else:
            guid_rev2 = guid
        name = row.name
        if name != None:
            name_rev1 = name.replace('rdflib.term.Literal(', '')
            name_rev2 = name_rev1.replace(')', '')
        else:
            name_rev2 = name
        long_name = row.longname
        if long_name != None:
            long_name_rev1 = long_name.replace('rdflib.term.Literal(', '')
            long_name_rev2 = long_name_rev1.replace(')', '')
        else:
            long_name_rev2 = long_name
        description = row.description
        if description != None:
            description_rev1 = guid.replace('rdflib.term.Literal(', '')
            description_rev2 = description_rev1.replace(')', '')
        else:
            description_rev2 = description
        existing_data.append(namedlist(type_rev3, guid_rev2, name_rev2, long_name_rev2, description_rev2))
    intersections = set(model_data).intersection(set(existing_data))
    return model_data, existing_data, intersections

def dd_ifc1(o_aim, related_original, related_new):
    ns_aim = Namespace(o_aim)
    nss_aim = str('aim: <'+o_aim+'>') 
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?bot ?guid
    WHERE {
        ?bot rdf:type ?bot_type .
        VALUES ?bot_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
            }
        ?bot ddss:hasGuid ?guid .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['uri', 'guid'])
    output = []
    for row in result:
        uri = row.bot
        uri_rev = uri.replace(o_ddss, '')
        guid = row.guid
        guid_rev1 = guid.replace('rdflib.term.Literal(', '')
        guid_rev2 = guid_rev1.replace(')', '')
        output.append(namedlist(uri_rev, guid_rev2))
        if guid_rev2 == related_original:
            input.open((sparql_endpoint_1, sparql_endpoint_2))
            predicate1 = 'hasGuid'
            s1 = URIRef(uri_rev)
            p1 = URIRef(ns_ddss+predicate1)
            o1 = Literal(related_new)
            input.add((
                s1, p1, o1,
            ))

def dd_ifc2(o_aim, unique_document_id, model_data, intersections):
    ns_aim = Namespace(o_aim)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    for instance in model_data:
        if instance not in intersections:
            uri = BNode()
            type = instance.type
            guid = instance.guid
            name = instance.name
            longname = instance.longname
            description = instance.description
            s = URIRef(ns_aim+uri)
            predicate1 = 'type'
            p1 = URIRef(ns_rdf+predicate1)
            o1 = URIRef(ns_bot+type)
            predicate2 = 'hasGuid'
            p2 = URIRef(ns_ddss+predicate2)
            o2 = Literal(guid)
            predicate3 = 'hasName'
            p3 = URIRef(ns_ddss+predicate3)
            o3 = Literal(name)
            predicate4 = 'hasLongName'
            p4 = URIRef(ns_ddss+predicate4)
            o4 = Literal(longname)
            predicate5 = 'hasDescription'
            p5 = URIRef(ns_ddss+predicate5)
            o5 = Literal(description)
            predicate6 = 'relatesToBuilding'
            s6 = URIRef(ns_aim+unique_document_id)
            p6 = URIRef(ns_ddss+predicate6)
            o6 = s
            predicate7 = 'partOf'
            p7 = URIRef(ns_ddss+predicate7)
            o7 = URIRef(o_aim)
            input.add((
                s, p1, o1,
            ))
            input.add((
                s, p2, o2,
            ))
            input.add((
                s, p3, o3,
            ))
            input.add((
                s, p4, o4,
            ))
            input.add((
                s, p5, o5,
            ))
            input.add((
                s6, p6, o6,
            ))
            input.add((
                s, p7, o7,
            ))



















########################
### test environment ###
########################

# def rq_model5(type):
#     input = sparqlstore.SPARQLUpdateStore()
#     input.open((sparql_endpoint_1))
#     q = """
#     PREFIX """+nss_bot+"""
#     PREFIX """+nss_ddss+"""
#     PREFIX """+nss_rdf+"""
#     PREFIX """+nss_org+"""
#     PREFIX """+nss_foaf+"""
#     PREFIX """+nss_oms+"""
#     PREFIX """+nss_aim+"""
#     SELECT ?subject
#     WHERE {
#         ?subject rdf:type """+type+"""
#     }
#     """
#     result = input.query(q)
#     output = []
#     for row in result:
#         subject = row.subject
#         if o_ddss in subject:
#             subject_rev = subject.replace(o_ddss, '')
#         elif o_rdf in subject:
#             subject_rev = subject.replace(o_rdf, '')
#         elif o_bot in subject:
#             subject_rev = subject.replace(o_bot, '')
#         elif o_org in subject:
#             subject_rev = subject.replace(o_org, '')
#         elif o_foaf in subject:
#             subject_rev = subject.replace(o_foaf, '')
#         else:
#             subject_rev = subject
#         output.append(subject_rev)
#     return output

# def rq_aim_content(aim):
#     nss_aim = str('aim: <'+aim+'>')
#     aim_rev = str(f"<{aim}>")
#     input = sparqlstore.SPARQLUpdateStore()
#     input.open((sparql_endpoint_1))
#     q = """
#     PREFIX """+nss_bot+"""
#     PREFIX """+nss_ddss+"""
#     PREFIX """+nss_rdf+"""
#     PREFIX """+nss_oms+"""
#     PREFIX """+nss_aim+"""
#     SELECT ?aim ?name ?site ?building ?storey ?space ?event ?document
#     WHERE {
#         ?aim rdf:type ddss:AIM .
#         VALUES ?aim {
#             """+aim_rev+"""
#         }
#         ?aim ddss:hasModelName ?name .
#     	OPTIONAL {
#             ?site rdf:type bot:Site .
#             ?site ddss:partOf ?aim .
#         }
#         OPTIONAL {
#             ?building rdf:type bot:Building .
#             ?building ddss:partOf ?aim .
#         }
#         OPTIONAL {
#             ?storey rdf:type bot:Storey .
#             ?storey ddss:partOf ?aim .
#         }
#         OPTIONAL {
#             ?space rdf:type bot:Space .
#             ?space ddss:partOf ?aim .
#         }
#         OPTIONAL {
#             ?event rdf:type ddss:Event .
#             ?event ddss:partOf ?aim .
#         }
#         OPTIONAL {
#             ?document rdf:type ?doc_type .
#             VALUES ?doc_type {
#                 ddss:IFC
#                 ddss:PDF
#                 ddss:CSV
#                 ddss:PNG
#                 ddss:JPEG
#                 ddss:PCD
#                 ddss:TXT
#                 ddss:IFC2x3
#                 ddss:IFC4
#             }
#             ?document ddss:partOf ?aim .
#         }
#     }
#     """
#     result = input.query(q)
#     namedlist = collections.namedtuple('namedlist', ['aim', 'name', 'site', 'building', 'storey', 'space', 'event', 'document'])
#     output = []
#     for row in result:
#         aim = row.aim
#         name = row.name
#         site = row.site
#         building = row.building
#         storey = row.storey
#         space = row.space
#         event = row.event
#         document = row.document
#         output.append(namedlist(aim, name, site, building, storey, space, event, document))
#     return output

# def rq_model2(query_construct, query_where):
#     input = SPARQLWrapper(sparql_endpoint_1)
#     input.setQuery("""
#     PREFIX """+o_bot+"""
#     CONSTRUCT { """+query_construct+""" }
#     WHERE { """+query_where+""" . }
#     """)
#     output = input.queryAndConvert().serialize(format=TURTLE)
#     return output

# def generate_unique_code():
#     length = 6
#     while True:
#         code = ''.join(random.choices(string.ascii_uppercase, k=length))
#         if Room.objects.filter(code=code).count() == 0:
#             break
#     return code

# class Room(models.Model):
#     code = models.CharField(max_length=8, default='', unique=True)
#     host = models.CharField(max_length=50, unique=True)
#     guest_can_pause = models.BooleanField(null=False, default=False)
#     votes_to_skip = models.IntegerField(null=False, default=1)
#     created_at = models.DateTimeField(auto_now_add=True)

# class Triple(models.Model):
#     subject = models.CharField(max_length=200)
#     ns_subject = models.CharField(max_length=200)
#     predicate = models.CharField(max_length=200)
#     ns_predicate = models.CharField(max_length=200)
#     object = models.CharField(max_length=200)
#     ns_object = models.CharField(max_length=200)

# def dd_model_test():
#     s = URIRef(Triple.ns_subject+Triple.subject)
#     p = URIRef(Triple.ns_predicate+Triple.predicate)
#     o = URIRef(Triple.ns_object+Triple.object)
#     input = sparqlstore.SPARQLUpdateStore()
#     input.open((sparql_endpoint_1, sparql_endpoint_2))
#     input.add((
#         s, p, o,
#     ))
#     return 'Success, added {} {} {}!'.format(Triple.subject, Triple.predicate, Triple.object)

# def dd_model1_new(subject):
#     predicate = 'type'
#     object = 'Site'
#     s = URIRef(ns_ddss+subject)
#     p = URIRef(ns_rdf+predicate)
#     o = URIRef(ns_bot+object)
#     input = sparqlstore.SPARQLUpdateStore()
#     input.open((sparql_endpoint_1, sparql_endpoint_2))
#     input.add((
#         s, p, o,
#     ))

# def dd_model2(site, subject, object):
#     if object == 'Building':
#         predicate1 = 'containsBuilding'
#     elif object == 'Storey':
#         predicate1 = 'containsStorey'
#     elif object == 'Space':
#         predicate1 = 'containsSpace'
#     elif object == 'Element':
#         predicate1 = 'containsElement'
#     else:
#         predicate1 = 'containsZone'
#     s1 = URIRef(ns_ddss+site)
#     p1 = URIRef(ns_bot+predicate1)
#     o1 = URIRef(ns_ddss+subject)
#     predicate2 = 'type'
#     s2 = URIRef(ns_ddss+subject)
#     p2 = URIRef(ns_rdf+predicate2)
#     o2 = URIRef(ns_bot+object)
#     input = sparqlstore.SPARQLUpdateStore()
#     input.open((sparql_endpoint_1, sparql_endpoint_2))
#     input.add((
#         s1, p1, o1,
#     ))
#     input.add((
#         s2, p2, o2,
#     ))
#     return 'Success, added {} as a bot:{}'.format(subject, object)

# class dd_info(models.Model):
#     dd_unique_id = models.CharField()
#     current_user_unique_id = models.CharField()

# class singleton(models.Model):
#     class Meta:
#         abstract = TRUE
#     def save(self, *args, **kwargs):
#         self.pk = 1
#         super(singleton, self).save(*args, **kwargs)
#     def delete(self, *args, **kwargs):
#         pass
#     @classmethod
#     def load(cls):
#         obj,_=cls.objects.get_or_create(pk=1)
#         return obj

# class ddss_settings(singleton):
#     sparql_endpoint_1 = models.CharField()
#     sparql_endpoint_2 = models.CharField()