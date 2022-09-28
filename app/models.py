from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.plugins.stores import sparqlstore
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import collections, os, zipfile, sys, fileinput, shutil
import ifcopenshell

####################
### Dependencies ###
####################

# rdflib
# ifcopenshell

###############################################################
### Connected SPARQL endpoints & document storage locations ###
###############################################################

sparql_endpoint_1 = settings.SPARQL_ENDPOINT_1
sparql_endpoint_2 = settings.SPARQL_ENDPOINT_2
document_storage_location = settings.MEDIA_ROOT
document_storage_location_rel = settings.MEDIA_ROOT_REL
aim_default_namespace = settings.AIM_DEFAULT_NAMESPACE
o_oms = settings.ORGANIZATION_DEFAULT_NAMESPACE
current_org = settings.CURRENT_ORG

######################################
### Global semantic web namespaces ###
######################################

o_ddss = 'https://github.com/chielvanderpas/ddss#'
ns_ddss = Namespace(o_ddss)
nss_ddss = 'ddss: <https://github.com/chielvanderpas/ddss#>'

o_rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
ns_rdf = Namespace(o_rdf)
nss_rdf = 'rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'

o_rdfs = 'http://www.w3.org/2000/01/rdf-schema#'
ns_rdfs = Namespace(o_rdfs)
nss_rdfs = 'rdfs: <http://www.w3.org/2000/01/rdf-schema#>'

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

ns_oms = Namespace(o_oms)
nss_oms = str('oms: <'+o_oms+'>')

####################
### Setup models ###
####################

def model_write_ontology():
    ontology = Graph()
    ontology.parse('ddss/app/ontology/DDSS_ontology.ttl')
    output = ontology.serialize(format="turtle")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    return output
    # input = sparqlstore.SPARQLUpdateStore()
    # input.open((sparql_endpoint_1, sparql_endpoint_2))
    # for s, p, o in ontology.quads((None, RDF.type, None, None)):
    #     input.add((
    #         s, p, o
    #     ))

    ### include adding organisation to graph

def define_current_org():
    predicate1 = 'type'
    object1 = 'Organization'
    s1 = URIRef(current_org)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_org+object1)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s1, p1, o1,
    ))

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

def register_model(username, email, password, first_name, last_name, phone_number, role):
    user = User.objects.create_user(username, email, password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    unique_user_id = BNode()
    predicate1 = 'type'
    object1 = 'Actor'
    s = URIRef(ns_oms+unique_user_id)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'hasName'
    full_name = str(first_name+' '+last_name)
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(full_name)
    predicate3 = 'hasEmailAddress'
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(email)
    predicate4 = 'hasPhoneNumber'
    p4 = URIRef(ns_ddss+predicate4)
    o4 = Literal(phone_number)
    predicate5 = 'hasRole'
    p5 = URIRef(ns_ddss+predicate5)
    o5 = Literal(ns_oms+role)
    predicate6 = 'subClassOf'
    object6 = 'Agent'
    p6 = URIRef(ns_rdfs+predicate6)
    o6 = URIRef(ns_org+object6)
    predicate7 = 'memberOf'
    p7 = URIRef(ns_rdfs+predicate7)
    o7 = URIRef(current_org)
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
    input.add((
        s, p7, o7,
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
    SELECT ?user ?phone_number ?role ?organization
    WHERE {
        ?user rdf:type ddss:Actor .
        ?user ddss:hasEmailAddress ?email .
        VALUES ?email {
            """+email_rev+"""
        }
        ?user ddss:hasPhoneNumber ?phone_number .
        ?user ddss:hasRole ?role .
        ?user rdfs:memberOf ?organization .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['user', 'phone_number', 'role', 'organization'])
    output = []
    for row in result:
        user = row.user.replace(o_oms, '')
        phone_number = row.phone_number
        role = row.role.replace(ns_oms, '')
        organization = row.organization
        output.append(namedlist(user, phone_number, role, organization))
    return output

def add_roles(role):
    predicate1 = 'type'
    object1 = 'Role'
    s1 = URIRef(ns_oms+role)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    input.add((
        s1, p1, o1,
    ))

def rq_roles():
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    SELECT ?role
    WHERE {
        ?role rdf:type ddss:Role .
    }
    """
    result = input.query(q)
    roles = []
    for row in result:
        role = row.role.replace(o_oms, '')
        roles.append(role)
    return roles

def org_edit_actor(actor_id, actor_phone_number_new, actor_phone_number_old, actor_role_new, actor_role_old):
    if actor_phone_number_new != actor_phone_number_old:
        predicate1 = 'hasPhoneNumber'
        s1 = URIRef(ns_oms+actor_id)
        p1 = URIRef(ns_ddss+predicate1)
        o1 = Literal(actor_phone_number_new)
        o2 = Literal(actor_phone_number_old)
        input = sparqlstore.SPARQLUpdateStore()
        input.open((sparql_endpoint_1, sparql_endpoint_2))
        input.add((
            s1, p1, o1,
        ))
        input.remove(( 
            s1, p1, o2,
        ), context=None)
    if actor_role_new != actor_role_old:
        predicate3 = 'hasRole'
        s3 = URIRef(ns_oms+actor_id)
        p3 = URIRef(ns_ddss+predicate3)
        o3 = URIRef(ns_oms+actor_role_new)
        o4 = URIRef(ns_oms+actor_role_old)
        input = sparqlstore.SPARQLUpdateStore()
        input.open((sparql_endpoint_1, sparql_endpoint_2))
        input.add((
            s3, p3, o3,
        ))
        input.remove(( 
            s3, p3, o4,
        ), context=None)

def org_add_actor(actor_name, actor_email, actor_phone_number, actor_role):
    unique_user_id = BNode()
    predicate1 = 'type'
    object1 = 'Actor'
    s = URIRef(ns_oms+unique_user_id)
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'hasName'
    p2 = URIRef(ns_ddss+predicate2)
    o2 = Literal(actor_name)
    predicate3 = 'hasEmailAddress'
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(actor_email)
    predicate4 = 'hasPhoneNumber'
    p4 = URIRef(ns_ddss+predicate4)
    o4 = Literal(actor_phone_number)
    predicate5 = 'hasRole'
    p5 = URIRef(ns_ddss+predicate5)
    o5 = URIRef(ns_oms+actor_role)
    predicate6 = 'subClassOf'
    object6 = 'Agent'
    p6 = URIRef(ns_rdfs+predicate6)
    o6 = URIRef(ns_org+object6)
    predicate7 = 'memberOf'
    p7 = URIRef(ns_rdfs+predicate7)
    o7 = URIRef(current_org)
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
    input.add((
        s, p7, o7,
    ))

###########################
### Data request models ###
###########################

### data request models: create custom sparql query ###

def rq_sparql_query(query):
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    """+query+"""
    """
    result = input.query(q)
    aims = rq_aim()
    output = []
    for row in result:
        triple = str(f"{row}")
        triple_rev = triple.replace('rdflib.term.URIRef(', '').replace('rdflib.term.Literal(', '').replace('(', '').replace(')', '').replace(o_rdf, 'rdf:').replace(o_rdfs, 'rdfs:').replace(o_bot, 'bot:').replace(o_foaf, 'foaf:').replace(o_org, 'org:').replace(o_ddss, 'ddss:').replace(o_oms, '').replace("'", "").replace(',', ' |')
        for aim in aims:
            aim_namespace = aim.namespace
            aim_name = aim.name
            triple_rev = triple_rev.replace(aim_namespace, aim_name+':')
        output.append(triple_rev)
    return output

### data request models: aims ###

def rq_aim_fork(aim_namespace):
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
    SELECT ?parent_fork ?child_fork
    WHERE {
        ?aim rdf:type ddss:AIM .
        VALUES ?aim {
            """+aim_rev+"""
        }
        ?aim ddss:hasModelName ?aim_name .
        OPTIONAL {
            ?aim ddss:isForkOf ?parent_fork 
        }
        OPTIONAL {
            ?aim ddss:hasFork ?child_fork 
        }
    }
    """
    result = input.query(q)
    parent_forks = []
    child_forks = []
    for row in result:
        if row.parent_fork != None:
            parent_fork = row.parent_fork.replace('', '')
            parent_forks.append(parent_fork)
        if row.child_fork != None:
            child_fork = row.child_fork.replace('', '')
            child_forks.append(child_fork)
    return parent_forks, child_forks

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
        ?bot ddss:hasBotName ?bot_name .
    }
    """
    result = input.query(q)
    namedlist1 = collections.namedtuple('namedlist', ['aim', 'aim_name', 'bot', 'bot_type', 'bot_name'])
    output1 = []
    output2 = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        bot = row.bot
        bot_rev = bot.replace(aim_namespace, '')
        bot_type = row.bot_type.replace(o_bot, '')
        bot_name = row.bot_name.replace(aim_namespace, '')
        output1.append(namedlist1(aim, aim_name, bot_rev, bot_type, bot_name))
        relations = rq_aim_bot_relations(aim_namespace, bot)
        output2 = output2+relations
    return output1, output2

def rq_aim_bot_relations(aim_namespace, bot):
    nss_aim = str('aim: <'+aim_namespace+'>')
    bot_rev = str(f"<{bot}>")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?bot_parent ?bot_child
    WHERE {
        ?bot_parent bot:containsZone ?bot_child .
        VALUES ?bot_parent {
            """+bot_rev+"""
        }
    }
    """
    result = input.query(q)
    bot_parent = None
    bot_child = None
    namedlist = collections.namedtuple('namedlist', ['bot_parent', 'bot_child'])
    relations = []
    for row in result:
        bot_parent = row.bot_parent.replace(aim_namespace, '')
        bot_child = row.bot_child.replace(aim_namespace, '')
        relations.append(namedlist(bot_parent, bot_child))
    return relations

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
        ?event ddss:hasEventDescription ?event_description .
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

def rq_aim_datadrops1(aim_namespace):
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
    SELECT ?aim ?aim_name ?data_drop ?upload_actor ?upload_actor_name ?datetime
    WHERE {
        ?aim rdf:type ddss:AIM .
        VALUES ?aim {
            """+aim_rev+"""
        }
        ?aim ddss:hasModelName ?aim_name .
        ?data_drop ddss:ddPartOf ?aim .
        ?data_drop ddss:uploadedBy ?upload_actor .
        ?upload_actor ddss:hasName ?upload_actor_name .
        ?data_drop ddss:occurredAt ?datetime .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['aim', 'aim_name', 'data_drop', 'upload_actor', 'upload_actor_name', 'datetime'])
    output = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        data_drop = row.data_drop.replace(aim_namespace, '')
        upload_actor = row.upload_actor.replace(o_oms, '')
        upload_actor_name = row.upload_actor_name.replace('', '')
        datetime = row.datetime.replace('', '')
        output.append(namedlist(aim, aim_name, data_drop, upload_actor, upload_actor_name, datetime))
    return output

def rq_aim_datadrops2(aim_namespace):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?data_drop ?document ?document_name ?type
    WHERE {
        ?data_drop rdf:type ddss:DataDrop .
        ?data_drop ddss:contains ?document_interaction .
        ?document_interaction ddss:concernsDocument ?document .
        ?document ddss:hasFileName ?document_name .
        ?document_interaction rdf:type ?type .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['data_drop', 'document', 'document_name', 'type'])
    output = []
    for row in result:
        data_drop = row.data_drop.replace(aim_namespace, '')
        document = row.document.replace(aim_namespace, '')
        document_name = row.document_name.replace('', '')
        type = row.type.replace(o_ddss, '')
        output.append(namedlist(data_drop, document, document_name, type))
    return output

def rq_aim_datadrops3(aim_namespace):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?data_drop ?event ?event_type ?event_datetime ?event_description
    WHERE {
        ?data_drop rdf:type ddss:DataDrop .
        ?data_drop ddss:relatesToEvent ?event .
        ?event rdf:type ?event_type .
        ?event ddss:startedAt ?event_datetime .
        ?event ddss:hasEventDescription ?event_description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['data_drop', 'event', 'event_type', 'event_datetime', 'event_description'])
    output = []
    for row in result:
        data_drop = row.data_drop.replace(aim_namespace, '')
        event = row.event.replace(aim_namespace, '')
        event_type = row.event_type.replace(o_ddss, '')
        event_datetime = row.event_datetime.replace('', '')
        event_description = row.event_description.replace('', '')
        output.append(namedlist(data_drop, event, event_type, event_datetime, event_description))
    return output

### data request models: event instance models ###

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
    SELECT ?event ?type ?startdatetime ?enddatetime ?description ?actor ?actor_name
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
        ?event ddss:hasEventDescription ?description .
        OPTIONAL {
            ?event ddss:endedAt ?enddatetime .
        }
        ?event ddss:involves ?actor .
        ?actor ddss:hasName ?actor_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'type', 'startdatetime', 'enddatetime', 'description', 'actor', 'actor_name'])
    output = []
    for row in result:
        id = row.event.replace(aim_namespace, '')
        type = row.type.replace(o_ddss, '')
        startdatetime = row.startdatetime
        enddatetime = row.enddatetime
        description = row.description
        actor = row.actor.replace(o_oms, '')
        actor_name = row.actor_name
        output.append(namedlist(id, type, startdatetime, enddatetime, description, actor, actor_name))
    return output

def rq_event3(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?event ?bot ?bot_type ?bot_name
    WHERE {
        VALUES ?event {
            aim:"""+instance+"""
        }
        ?bot rdf:type ?bot_type .
        VALUES ?bot_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        ?event ddss:relatesToPhysicalObject ?bot .
        ?bot ddss:hasBotName ?bot_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['event', 'bot', 'bot_type', 'bot_name'])
    output = []
    for row in result:
        event = row.event.replace('', '')
        bot = row.bot.replace(aim_namespace, '')
        bot_type = row.bot_type.replace(o_bot, '')
        bot_name = row.bot_name.replace(aim_namespace, '')
        output.append(namedlist(event, bot, bot_type, bot_name))
    return output

def rq_event4(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?event ?superevent ?superevent_type ?superevent_startdatetime ?superevent_description
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
        ?superevent ddss:hasSubEvent ?event .
        ?superevent rdf:type ?superevent_type .
        ?superevent ddss:startedAt ?superevent_startdatetime .
        ?superevent ddss:hasEventDescription ?superevent_description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'superevent', 'superevent_type', 'superevent_startdatetime', 'superevent_description'])
    output = []
    for row in result:
        id = row.event.replace(aim_namespace, '')
        superevent = row.superevent.replace(aim_namespace, '')
        superevent_type = row.superevent_type.replace(o_ddss, '')
        superevent_startdatetime = row.superevent_startdatetime.replace('', '')
        superevent_description = row.superevent_description.replace('', '')
        output.append(namedlist(id, superevent, superevent_type, superevent_startdatetime, superevent_description))
    return output

def rq_event5(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?event ?subevent ?subevent_type ?subevent_startdatetime ?subevent_description
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
        ?event ddss:hasSubEvent ?subevent .
        ?subevent rdf:type ?subevent_type .
        ?subevent ddss:startedAt ?subevent_startdatetime .
        ?subevent ddss:hasEventDescription ?subevent_description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'subevent', 'subevent_type', 'subevent_startdatetime', 'subevent_description'])
    output = []
    for row in result:
        id = row.event.replace(aim_namespace, '')
        subevent = row.subevent.replace(aim_namespace, '')
        subevent_type = row.subevent_type.replace(o_ddss, '')
        subevent_startdatetime = row.subevent_startdatetime.replace('', '')
        subevent_description = row.subevent_description.replace('', '')
        output.append(namedlist(id, subevent, subevent_type, subevent_startdatetime, subevent_description))
    return output

def rq_event6(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?event ?data_drop ?datetime ?upload_actor ?upload_actor_name
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
        ?data_drop ddss:relatesToEvent ?event .
        ?data_drop ddss:occurredAt ?datetime .
        ?data_drop ddss:uploadedBy ?upload_actor .
        ?upload_actor ddss:hasName ?upload_actor_name .
        
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['event', 'data_drop', 'datetime', 'upload_actor', 'upload_actor_name'])
    output = []
    for row in result:
        event = row.event.replace(aim_namespace, '')
        data_drop = row.data_drop.replace(aim_namespace, '')
        datetime = row.datetime.replace('', '')
        upload_actor = row.upload_actor.replace(o_oms, '')
        upload_actor_name = row.upload_actor_name.replace('', '')
        output.append(namedlist(event, data_drop, datetime, upload_actor, upload_actor_name))
    return output

### data request models: bot instance models ###

def rq_bot1(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
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
    SELECT ?bot ?bot_type ?name ?longname ?description ?aim ?aim_name (GROUP_CONCAT(DISTINCT ?guid; SEPARATOR=", ") AS ?guids)
    WHERE {
        ?bot rdf:type ?bot_type .
        VALUES ?bot {
        	aim:"""+instance+"""
    	}
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
            ?bot ddss:hasBotName ?name .
            }
        OPTIONAL {
            ?bot ddss:hasBotLongName ?longname .
            }
        OPTIONAL {
            ?bot ddss:hasBotDescription ?description .
            }
        ?bot ddss:partOf ?aim .
        ?aim ddss:hasModelName ?aim_name .
    }
    GROUP BY ?bot ?bot_type ?name ?longname ?description ?aim ?aim_name
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['uri', 'type', 'guids', 'name', 'longname', 'description', 'aim', 'aim_name'])
    output = []
    for row in result:
        uri = row.bot.replace(aim_namespace, '')
        type = row.bot_type.replace(o_bot, '')
        guids = row.guids
        name = row.name
        long_name = row.longname
        description = row.description
        aim = row.aim
        aim_name = row.aim_name
        output.append(namedlist(uri, type, guids, name, long_name, description, aim, aim_name))
    return output

def rq_bot2(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?bot ?document ?document_name
    WHERE {
        VALUES ?bot {
            aim:"""+instance+"""
        }
        ?document ddss:relatesToPhysicalObject ?bot .
        ?document ddss:hasFileName ?document_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['bot', 'document', 'document_name'])
    output = []
    for row in result:
        bot = row.bot.replace(aim_namespace, '')
        document = row.document.replace(aim_namespace, '')
        document_name = row.document_name.replace('', '')
        output.append(namedlist(bot, document, document_name))
    return output

def rq_bot3(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?parent ?parent_name ?parent_type ?child ?child_name ?child_type
    WHERE {
        VALUES ?child {
            aim:"""+instance+"""
        }
        ?parent rdf:type ?parent_type .
        VALUES ?parent_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        ?parent bot:containsZone ?child .
        ?child rdf:type ?child_type .
        VALUES ?child_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        OPTIONAL {
            ?parent ddss:hasBotName ?parent_name .
        }
        OPTIONAL {
            ?child ddss:hasBotName ?child_name .
        }
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['parent', 'parent_name', 'parent_type', 'child', 'child_name', 'child_type'])
    output = []
    for row in result:
        parent = row.parent.replace(aim_namespace, '')
        parent_name = row.parent_name
        parent_type = row.parent_type.replace(o_bot, '')
        child = row.child.replace(aim_namespace, '')
        child_name = row.child_name
        child_type = row.child_type.replace(o_bot, '')
        output.append(namedlist(parent, parent_name, parent_type, child, child_name, child_type))
    return output

def rq_bot4(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?parent ?parent_name ?parent_type ?child ?child_name ?child_type
    WHERE {
        VALUES ?parent {
            aim:"""+instance+"""
        }
        ?parent rdf:type ?parent_type .
        VALUES ?parent_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        ?parent bot:containsZone ?child .
        ?child rdf:type ?child_type .
        VALUES ?child_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        OPTIONAL {
            ?parent ddss:hasBotName ?parent_name .
        }
        OPTIONAL {
            ?child ddss:hasBotName ?child_name .
        }
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['parent', 'parent_name', 'parent_type', 'child', 'child_name', 'child_type'])
    output = []
    for row in result:
        parent = row.parent.replace(aim_namespace, '')
        parent_name = row.parent_name
        parent_type = row.parent_type.replace(o_bot, '')
        child = row.child.replace(aim_namespace, '')
        child_name = row.child_name
        child_type = row.child_type.replace(o_bot, '')
        output.append(namedlist(parent, parent_name, parent_type, child, child_name, child_type))
    return output

def rq_bot5(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?bot ?event ?event_description
    WHERE {
        VALUES ?bot {
            aim:"""+instance+"""
        }
        ?event ddss:relatesToPhysicalObject ?bot .
        ?event ddss:hasEventDescription ?event_description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['bot', 'event', 'event_description'])
    output = []
    for row in result:
        bot = row.bot.replace(aim_namespace, '')
        event = row.event.replace(aim_namespace, '')
        event_description = row.event_description.replace('', '')
        output.append(namedlist(bot, event, event_description))
    return output

### data request models: actor instance models ###

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
        	oms:"""+instance+"""
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
        id = row.actor.replace(o_oms, '')
        name = row.name
        email = row.email
        phone_number = row.phone_number
        output.append(namedlist(id, name, email, phone_number))
    return output

def rq_actor2(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?upload_actor ?upload_actor_name ?data_drop ?datetime
    WHERE {
        ?upload_actor rdf:type ddss:Actor .
        VALUES ?upload_actor {
            oms:"""+instance+"""
        }
        ?data_drop ddss:uploadedBy ?upload_actor .
        ?upload_actor ddss:hasName ?upload_actor_name .
        ?data_drop ddss:occurredAt ?datetime .
        ?data_drop ddss:ddPartOf <"""+aim_namespace+"""> .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['upload_actor', 'upload_actor_name', 'data_drop', 'datetime'])
    output = []
    for row in result:
        upload_actor = row.upload_actor.replace(o_oms, '')
        upload_actor_name = row.upload_actor_name.replace('', '')
        data_drop = row.data_drop.replace(aim_namespace, '')
        datetime = row.datetime.replace('', '')
        output.append(namedlist(upload_actor, upload_actor_name, data_drop, datetime))
    return output

def rq_actor3():
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    SELECT ?user ?name ?email ?organization ?phone_number ?role
    WHERE {
        ?user rdf:type ddss:Actor .
        ?user ddss:hasName ?name .
        ?user ddss:hasEmailAddress ?email .
        ?user rdfs:memberOf ?organization.  
        ?user ddss:hasPhoneNumber ?phone_number .
        ?user ddss:hasRole ?role .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'name', 'email', 'organization', 'phone_number', 'role'])
    output = []
    for row in result:
        id = row.user.replace(o_oms, '')
        name = row.name
        organization = row.organization
        email = row.email
        phone_number = row.phone_number
        role = row.role.replace(o_oms, '')
        output.append(namedlist(id, name, email, organization, phone_number, role))
    return output

### data request models: document instance models ###

def rq_document1(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?document ?doc_type ?content_type ?status ?preserve_until ?unique_identifier ?description ?file_name ?copy ?copy_name ?copy_storage_location ?creation_software ?creation_software_version ?prev_version ?aim ?aim_name ?storage_location
    WHERE {
        ?document rdf:type ?doc_type .
        VALUES ?document {
            aim:"""+instance+"""
        }
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
        OPTIONAL {
            ?document ddss:hasContentType ?content_type .
        }
        ?document ddss:hasStatus ?status .
        ?document ddss:hasPreservationUntilDate ?preserve_until .
        OPTIONAL {
            ?document ddss:hasUniqueIdentifier ?unique_identifier .
        }
        ?document ddss:hasDocumentDescription ?description .
        ?document ddss:hasFileName ?file_name .
        OPTIONAL {
            ?document ddss:hasCopy ?copy .
            ?copy ddss:hasCopyFileName ?copy_name .
            ?copy ddss:copyStoredAt ?copy_storage_location .
        }
        ?document ddss:hasCreationSoftware ?creation_software .
        ?document ddss:hasCreationSoftwareVersion ?creation_software_version .
        OPTIONAL {
            ?document ddss:hasPreviousVersion ?prev_version .
        }
        ?document ddss:partOf ?aim .
        ?aim ddss:hasModelName ?aim_name .
        ?document ddss:storedAt ?storage_location .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['id', 'doc_type', 'content_type', 'status', 'preserve_until', 'unique_identifier', 'description', 'file_name', 'copy', 'copy_name', 'copy_storage_location', 'creation_software', 'creation_software_version', 'prev_version', 'aim_namespace', 'aim_name', 'storage_location'])
    output = []
    for row in result:
        id = row.document.replace(aim_namespace, '')
        doc_type =row.doc_type.replace(o_ddss, '')
        if row.content_type != None:
            content_type = row.content_type.replace(o_ddss, '')
        else:
            content_type = None
        status = row.status.replace(o_ddss, '')
        preserve_until = row.preserve_until.replace('', '')
        if row.unique_identifier != None:
            unique_identifier = row.unique_identifier.replace('', '')
        else:
            unique_identifier = None
        description = row.description.replace('', '')
        file_name = row.file_name.replace('', '')
        if row.copy != None:
            copy = row.copy.replace(aim_namespace, '')
            copy_name = row.copy_name.replace('', '')
            copy_storage_location = row.copy_storage_location.replace('', '')
        else:
            copy = None
            copy_name = None
            copy_storage_location = None
        creation_software = row.creation_software.replace('', '')
        creation_software_version = row.creation_software_version.replace('', '')
        if row.prev_version != None:
            prev_version = row.prev_version.replace(aim_namespace, '')
        else:
            prev_version = None
        aim_namespace = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        storage_location = row.storage_location.replace('', '')
        output.append(namedlist(id, doc_type, content_type, status, preserve_until, unique_identifier, description, file_name, copy, copy_name, copy_storage_location, creation_software, creation_software_version, prev_version, aim_namespace, aim_name, storage_location))
    return output

def rq_document2(aim_namespace, document_data):
    namedlist = collections.namedtuple('namedlist', ['prev_version', 'prev_version_name', 'prev_version_status'])
    prev_versions = []
    for instance in document_data:
        instance_id = instance.id
        prev_version, prev_version_name, prev_version_status = rq_document3(aim_namespace, instance_id)
        prev_versions.append(namedlist(prev_version, prev_version_name, prev_version_status))
        while prev_version != None:
            instance = prev_version
            prev_version, prev_version_name, prev_version_status = rq_document3(aim_namespace, instance)
            if prev_version != None:
                prev_versions.append(namedlist(prev_version, prev_version_name, prev_version_status))
            if prev_version == None:
                break
    return prev_versions

def rq_document3(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?prev_version ?prev_version_name ?prev_version_status
    WHERE {
        ?document rdf:type ?doc_type .
        VALUES ?document {
            aim:"""+instance+"""
        }
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
        ?document ddss:hasPreviousVersion ?prev_version .
        ?prev_version ddss:hasFileName ?prev_version_name .
        ?prev_version ddss:hasStatus ?prev_version_status .
    }
    """
    result = input.query(q)
    prev_version = None
    prev_version_name = None
    prev_version_status = None
    for row in result:
        prev_version = row.prev_version.replace(aim_namespace, '')
        prev_version_name = row.prev_version_name.replace('', '')
        prev_version_status = row.prev_version_status.replace(o_ddss, '')
    return prev_version, prev_version_name, prev_version_status

def rq_document4(aim_namespace, document_data):
    namedlist = collections.namedtuple('namedlist', ['newer_version', 'newer_version_name', 'newer_version_status'])
    newer_versions = []
    for instance in document_data:
        instance_id = instance.id
        newer_version, newer_version_name, newer_version_status = rq_document5(aim_namespace, instance_id)
        newer_versions.append(namedlist(newer_version, newer_version_name, newer_version_status))
        while newer_version != None:
            instance = newer_version
            newer_version, newer_version_name, newer_version_status = rq_document5(aim_namespace, instance)
            if newer_version != None:
                newer_versions.append(namedlist(newer_version, newer_version_name, newer_version_status))
            if newer_version == None:
                break
    return newer_versions

def rq_document5(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?newer_version ?newer_version_name ?newer_version_status
    WHERE {
        ?document rdf:type ?doc_type .
        VALUES ?document {
            aim:"""+instance+"""
        }
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
        ?newer_version ddss:hasPreviousVersion ?document .
        ?newer_version ddss:hasFileName ?newer_version_name .
        ?newer_version ddss:hasStatus ?newer_version_status .
    }
    """
    result = input.query(q)
    newer_version = None
    newer_version_name = None
    newer_version_status = None
    for row in result:
        newer_version = row.newer_version.replace(aim_namespace, '')
        newer_version_name = row.newer_version_name.replace('', '')
        newer_version_status = row.newer_version_status.replace(o_ddss, '')
    return newer_version, newer_version_name, newer_version_status

def rq_document6(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?document ?data_drop ?datetime ?upload_actor ?upload_actor_name (GROUP_CONCAT(DISTINCT ?document_interaction; SEPARATOR=", ") AS ?document_interactions) (GROUP_CONCAT(DISTINCT ?document_interaction_type; SEPARATOR=", ") AS ?document_interaction_types)
    WHERE {
            VALUES ?document {
                aim:"""+instance+"""
            }
            ?document_interaction ddss:concernsDocument ?document .
    		?document_interaction rdf:type ?document_interaction_type .
            ?data_drop ddss:contains ?document_interaction .
            ?data_drop ddss:occurredAt ?datetime .
            ?data_drop ddss:uploadedBy ?upload_actor .
    		?upload_actor ddss:hasName ?upload_actor_name . }
    GROUP BY ?document ?data_drop ?datetime ?upload_actor ?upload_actor_name

    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['document', 'data_drop', 'datetime', 'upload_actor', 'upload_actor_name', 'document_interaction_types',])
    output = []
    for row in result:
        document = row.document.replace('', '')
        data_drop = row.data_drop.replace(aim_namespace, '')
        datetime = row.datetime.replace('', '')
        upload_actor = row.upload_actor.replace(o_oms, '')
        upload_actor_name = row.upload_actor_name.replace('', '')
        document_interaction_types = row.document_interaction_types.replace(aim_namespace, '')
        output.append(namedlist(document, data_drop, datetime, upload_actor, upload_actor_name, document_interaction_types))
    return output

def rq_document7(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?document_interaction_type ?resp_actor ?resp_actor_name
    WHERE {
        ?document rdf:type ?doc_type .
        VALUES ?document {
            aim:"""+instance+"""
        }
        ?document_interaction ddss:concernsDocument ?document .
        ?document_interaction rdf:type ?document_interaction_type .
        ?document_interaction ddss:hasResponsibleActor ?resp_actor .
        ?resp_actor ddss:hasName ?resp_actor_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['document_interaction_type', 'resp_actor', 'resp_actor_name',])
    output = []
    for row in result:
        document_interaction_type = row.document_interaction_type.replace(o_ddss, '')
        resp_actor = row.resp_actor.replace(o_oms, '')
        resp_actor_name = row.resp_actor_name.replace('', '')
        output.append(namedlist(document_interaction_type, resp_actor, resp_actor_name))
    return output

def rq_document8(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?document ?bot ?bot_type ?bot_name
    WHERE {
        ?document rdf:type ?doc_type .
        VALUES ?document {
            aim:"""+instance+"""
        }
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
        ?bot rdf:type ?bot_type .
        VALUES ?bot_type {
            bot:Site
            bot:Building
            bot:Storey
            bot:Space
            bot:Element
        }
        ?document ddss:relatesToPhysicalObject ?bot .
        ?bot ddss:hasBotName ?bot_name .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['document', 'bot', 'bot_type', 'bot_name'])
    output = []
    for row in result:
        document = row.document.replace('', '')
        bot = row.bot.replace(aim_namespace, '')
        bot_type = row.bot_type.replace(o_bot, '')
        bot_name = row.bot_name.replace(aim_namespace, '')
        output.append(namedlist(document, bot, bot_type, bot_name))
    return output

### data request models: data drop instance models ###

def rq_datadrop1(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?data_drop ?upload_actor ?upload_actor_name ?datetime
    WHERE {
        ?data_drop rdf:type ddss:DataDrop .
        VALUES ?data_drop {
            aim:"""+instance+"""
        }
        ?data_drop ddss:uploadedBy ?upload_actor .
        ?upload_actor ddss:hasName ?upload_actor_name .
        ?data_drop ddss:occurredAt ?datetime .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['data_drop', 'upload_actor', 'upload_actor_name', 'datetime'])
    output = []
    for row in result:
        data_drop = row.data_drop.replace(aim_namespace, '')
        upload_actor = row.upload_actor.replace(o_oms, '')
        upload_actor_name = row.upload_actor_name.replace('', '')
        datetime = row.datetime.replace('', '')
        output.append(namedlist(data_drop, upload_actor, upload_actor_name, datetime))
    return output

def rq_datadrop2(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?data_drop ?document ?document_name ?type
    WHERE {
        ?data_drop rdf:type ddss:DataDrop .
        VALUES ?data_drop {
            aim:"""+instance+"""
        }
        ?data_drop ddss:contains ?document_interaction .
        ?document_interaction ddss:concernsDocument ?document .
        ?document ddss:hasFileName ?document_name .
        ?document_interaction rdf:type ?type .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['data_drop', 'document', 'document_name', 'type'])
    output = []
    for row in result:
        data_drop = row.data_drop.replace(aim_namespace, '')
        document = row.document.replace(aim_namespace, '')
        document_name = row.document_name.replace('', '')
        type = row.type.replace(o_ddss, '')
        output.append(namedlist(data_drop, document, document_name, type))
    return output

def rq_datadrop3(aim_namespace, instance):
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?data_drop ?event ?event_type ?event_datetime ?event_description
    WHERE {
        ?data_drop rdf:type ddss:DataDrop .
        VALUES ?data_drop {
            aim:"""+instance+"""
        }
        ?data_drop ddss:relatesToEvent ?event .
        ?event rdf:type ?event_type .
        ?event ddss:startedAt ?event_datetime .
        ?event ddss:hasEventDescription ?event_description .
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['data_drop', 'event', 'event_type', 'event_datetime', 'event_description'])
    output = []
    for row in result:
        data_drop = row.data_drop.replace(aim_namespace, '')
        event = row.event.replace(aim_namespace, '')
        event_type = row.event_type.replace(o_ddss, '')
        event_datetime = row.event_datetime.replace('', '')
        event_description = row.event_description.replace('', '')
        output.append(namedlist(data_drop, event, event_type, event_datetime, event_description))
    return output

### data_request_models: index page ###

def rq_index_aim_count():
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    SELECT (count(distinct ?aim) as ?aim_count)
    WHERE {
        ?aim rdf:type ddss:AIM .
    	?aim ddss:hasModelName ?aim_name .
    }
    LIMIT 5
    """
    result = input.query(q)
    for row in result:
        aim_count = row.aim_count
    return aim_count

def rq_index_aim():
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    SELECT ?aim ?aim_name (GROUP_CONCAT(DISTINCT ?data_drop; SEPARATOR=", ") AS ?dds) (GROUP_CONCAT(DISTINCT ?datetime; SEPARATOR=", ") AS ?datetimes)
    WHERE {
    SELECT * {
        ?aim rdf:type ddss:AIM .
    	?aim ddss:hasModelName ?aim_name .
        ?data_drop rdf:type ddss:DataDrop .
        ?data_drop ddss:ddPartOf ?aim .
        ?data_drop ddss:occurredAt ?datetime .
        }
    ORDER BY DESC(?datetime)
    }
	GROUP BY ?aim ?aim_name
    ORDER BY DESC(?datetimes)
    LIMIT 5
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['aim', 'aim_name'])
    output = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        output.append(namedlist(aim, aim_name))
    return output

def rq_index_dd():
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    SELECT ?aim ?aim_name ?data_drop ?upload_actor ?upload_actor_name ?datetime
    WHERE {
        ?data_drop rdf:type ddss:DataDrop .
        ?data_drop ddss:ddPartOf ?aim .
        ?aim ddss:hasModelName ?aim_name .
        ?data_drop ddss:uploadedBy ?upload_actor .
        ?upload_actor ddss:hasName ?upload_actor_name .
        ?data_drop ddss:occurredAt ?datetime .
    }
    ORDER BY DESC(?datetime)
    LIMIT 5
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['aim', 'aim_name', 'data_drop', 'data_drop_rev', 'upload_actor', 'upload_actor_name', 'datetime'])
    output = []
    for row in result:
        aim = row.aim.replace('', '')
        aim_name = row.aim_name.replace('', '')
        data_drop = row.data_drop.replace('', '')
        data_drop_rev = data_drop.rsplit('#', 1)[1]
        upload_actor = row.upload_actor.replace(o_oms, '')
        upload_actor_name = row.upload_actor_name.replace('', '')
        datetime = row.datetime.replace('', '')
        output.append(namedlist(aim, aim_name, data_drop, data_drop_rev, upload_actor, upload_actor_name, datetime))
    return output

### data request models: current aim ###

def rq_current_aim(o_aim):
    aim_rev = str(f"<{o_aim}>")
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_oms+"""
    SELECT ?aim_name
    WHERE {
        ?aim rdf:type ddss:AIM .
        VALUES ?aim {
            """+aim_rev+"""
        }
        ?aim ddss:hasModelName ?aim_name .
    }
    """
    result = input.query(q)
    for row in result:
        aim_name = row.aim_name.replace('', '')
    return aim_name


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
    return aim_namespace, unique_aim_id

### Data drop: create data drop ###

def dd_create(o_aim, user_id):
    ns_aim = Namespace(o_aim)
    unique_dd_id = BNode()
    s = URIRef(ns_aim+unique_dd_id)
    predicate1 = 'type'
    object1 = 'DataDrop'
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+object1)
    predicate2 = 'uploadedBy'
    user_id_rev = str(f"{user_id}")
    p2 = URIRef(ns_ddss+predicate2)
    o2 = URIRef(ns_oms+user_id_rev)
    predicate3 = 'occurredAt'
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M")
    p3 = URIRef(ns_ddss+predicate3)
    o3 = Literal(current_datetime)
    predicate4 = 'ddPartOf'
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
    return unique_dd_id

### Data drop: add event ###

def rq_event2(o_aim):
    nss_aim = str('aim: <'+o_aim+'>')
    aim_rev = str(f"<{o_aim}>")
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
        ?event ddss:partOf ?aim .
        VALUES ?aim {
            """+aim_rev+"""
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
        ?event ddss:hasEventDescription ?description .
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

def dd_event1(o_aim, event_type, event_description, startdatetime, enddatetime, related_actor, super_event, unique_dd_id):
    ns_aim = Namespace(o_aim)
    unique_event_id = BNode()
    s = URIRef(ns_aim+unique_event_id)
    predicate1 = 'type'
    p1 = URIRef(ns_rdf+predicate1)
    o1 = URIRef(ns_ddss+event_type)
    predicate2 = 'hasEventDescription'
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
    return unique_event_id

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
    return unique_event_id

def dd_event3(o_aim, bot_relations, unique_event_id):
    ns_aim = Namespace(o_aim)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    for relation in bot_relations:
        predicate = 'relatesToPhysicalObject'
        s = URIRef(ns_aim+unique_event_id)
        p = URIRef(ns_ddss+predicate)
        o = URIRef(ns_aim+relation)
        input.add((
            s, p, o,
        ))

### Data drop: upload document: check for previous versions ###

def dd_prev_version_check(file_exists_check, o_aim, unique_aim_id):
    prev_version = file_exists_check[-1]
    prev_version_rev = str(f"'{prev_version}'")
    prev_location = str(document_storage_location+'/'+unique_aim_id+'/'+prev_version)
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
        ?document ddss:storedAt ?location .
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
    predicate3 = 'storedAt'
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
    if copy_name != None:
        unique_copy_id = BNode()
        predicate5 = 'hasCopy'
        p5 = URIRef(ns_ddss+predicate5)
        o5 = URIRef(ns_aim+unique_copy_id)
        predicate6 = 'hasFileFormat'
        s6 = URIRef(ns_aim+unique_copy_id)
        p6 = URIRef(ns_ddss+predicate6)
        o6 = Literal(copy_type)
        predicate7 = 'hasCopyFileName'
        s7 = URIRef(ns_aim+unique_copy_id)
        p7 = URIRef(ns_ddss+predicate7)
        o7 = Literal(copy_name)
        predicate8 = 'copyStoredAt'
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
    predicate1 = 'hasDocumentDescription'
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
    predicate8 = 'concernsDocument'
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
    predicate12 = 'contains'
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

def dd_ifc1a(o_aim, document_storage_location):
    namedlist1 = collections.namedtuple('namedlist', ['type', 'guid', 'name', 'longname', 'description'])
    model_data = []
    namedlist2 = collections.namedtuple('namedlist', ['parent_guid', 'parent_name','parent_type', 'child_guid', 'child_name', 'child_type']) 
    relations = []
    ifc_file = ifcopenshell.open(document_storage_location)
    items = ifc_file.by_type('IfcProject')
    for item in items:
        model_data, relations = dd_ifc1_append_instance(item, namedlist1, model_data, namedlist2, relations)
    existing_data, intersections = dd_ifc1b(o_aim, model_data)
    return model_data, relations, existing_data, intersections

def dd_ifc1_append_instance(element, namedlist1, model_data, namedlist2, relations):     
    type = element.is_a().replace('IfcSite', 'Site').replace('IfcBuildingStorey', 'Storey').replace('IfcBuilding', 'Building').replace('IfcSpace', 'Space')
    guid = element.GlobalId
    name = element.Name
    long_name = element.LongName
    description = element.Description
    if type != 'IfcProject':
        model_data.append(namedlist1(type, guid, name, long_name, description))
    if (element.is_a('IfcSpatialStructureElement')):
        for rel in element.ContainsElements:
            relatedElements = rel.RelatedElements       
            for child in relatedElements:
                if (child.is_a('IFCSITE') or child.is_a('IFCBUILDING') or child.is_a('IFCBUILDINGSTOREY') or child.is_a('IFCSPACE')):  
                    relations.append(namedlist2(element.GlobalId, element.Name, element.is_a(), child.GlobalId, child.Name, child.is_a()))
                    dd_ifc1_append_instance(child, namedlist1, model_data, namedlist2, relations)           
    if (element.is_a('IfcObjectDefinition')):
        for rel in element.IsDecomposedBy:
            relatedObjects = rel.RelatedObjects
            for child in relatedObjects:
                if (child.is_a('IFCSITE') or child.is_a('IFCBUILDING') or child.is_a('IFCBUILDINGSTOREY') or child.is_a('IFCSPACE')):
                    relations.append(namedlist2(element.GlobalId, element.Name, element.is_a(), child.GlobalId, child.Name, child.is_a()))
                    dd_ifc1_append_instance(child, namedlist1, model_data, namedlist2, relations)
    return model_data, relations

def dd_ifc1b(o_aim, model_data):
    nss_aim = str('aim: <'+o_aim+'>')
    aim_rev = str(f"<{o_aim}>")
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
        ?bot ddss:partOf ?aim .
        VALUES ?aim {
            """+aim_rev+"""
        }
        OPTIONAL {
            ?bot ddss:hasGuid ?guid .
            }
        OPTIONAL {
            ?bot ddss:hasBotName ?name .
            }
        OPTIONAL {
            ?bot ddss:hasBotLongName ?longname .
            }
        OPTIONAL {
            ?bot ddss:hasBotDescription ?description .
            }
    }
    """
    result = input.query(q)
    namedlist = collections.namedtuple('namedlist', ['uri', 'type', 'guid', 'name', 'longname', 'description'])
    existing_data = []
    for row in result:
        uri = row.bot
        type = row.bot_type
        if type != None:
            type = type.replace("https://w3id.org/bot#", "")
        guid = row.guid
        name = row.name
        long_name = row.longname
        description = row.description
        existing_data.append(namedlist(uri, type, guid, name, long_name, description))
    model_data_guid = []
    for instance in model_data:
        instance_guid = instance.guid
        model_data_guid.append(instance_guid)
    existing_data_guid = []
    for instance in existing_data:
        instance_guid = instance.guid.replace('rdflib.term.Literal(', '').replace(')', '')
        existing_data_guid.append(instance_guid)
    intersections = set(model_data_guid).intersection(set(existing_data_guid))
    return existing_data, intersections

def dd_ifc1(o_aim, related_original, related_new):
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
    for row in result:
        uri = row.bot
        guid = row.guid
        if guid == related_original:
            input.open((sparql_endpoint_1, sparql_endpoint_2))
            predicate1 = 'hasGuid'
            s1 = URIRef(uri)
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
            predicate3 = 'hasBotName'
            p3 = URIRef(ns_ddss+predicate3)
            o3 = Literal(name)
            predicate4 = 'hasBotLongName'
            p4 = URIRef(ns_ddss+predicate4)
            o4 = Literal(longname)
            predicate5 = 'hasBotDescription'
            p5 = URIRef(ns_ddss+predicate5)
            o5 = Literal(description)
            predicate6 = 'relatesToPhysicalObject'
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

def dd_ifc3(o_aim, model_data, relations, existing_data):
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    exists_check = []
    for existing_instance in existing_data:
        existing_instance_guid = existing_instance.guid
        existing_instance_guid_rev = existing_instance_guid.replace('rdflib.term.Literal(', '').replace(')', '')
        exists_check.append(existing_instance_guid_rev)
    for rel_instance in relations:
        for model_instance in model_data:
            if model_instance.guid not in exists_check:
                if rel_instance.parent_guid == model_instance.guid:
                    parent_guid = rel_instance.parent_guid
                    child_guid = rel_instance.child_guid
                    parent_uri = dd_ifc4(o_aim, parent_guid)
                    child_uri = dd_ifc4(o_aim, child_guid)
                    input = sparqlstore.SPARQLUpdateStore()
                    input.open((sparql_endpoint_1, sparql_endpoint_2))
                    predicate1 = 'containsZone'
                    s1 = URIRef(parent_uri)
                    p1 = URIRef(ns_bot+predicate1)
                    o1 = URIRef(child_uri)   
                    input.add((
                        s1, p1, o1,
                    ))
                

def dd_ifc4(o_aim, instance_guid):                
    nss_aim = str('aim: <'+o_aim+'>') 
    instance_guid_rev = str(f"'{instance_guid}'")
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
        ?bot ddss:hasGuid ?guid .
        VALUES ?guid {
            """+instance_guid_rev+"""
        }
    }
    """
    result = input.query(q)
    for row in result:
        uri = row.bot
    return uri

def dd_document3(o_aim, bot_relations, unique_document_id):
    ns_aim = Namespace(o_aim)
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    for relation in bot_relations:
        predicate = 'relatesToPhysicalObject'
        s = URIRef(ns_aim+unique_document_id)
        p = URIRef(ns_ddss+predicate)
        o = URIRef(ns_aim+relation)
        input.add((
            s, p, o,
        ))

###################
### Fork models ###
###################

def fork_export(aim_namespace):
    unique_aim_id = aim_namespace.replace(aim_default_namespace, '').replace('#', '')
    unique_fork_id = BNode()
    ns_aim = Namespace(aim_namespace)
    ns_aim_default = Namespace(aim_default_namespace)
    nss_aim = str('aim: <'+aim_namespace+'>')
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q1 = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    CONSTRUCT {
        ?s ?p ?o
    }
    WHERE {
        ?s ?p ?o .
        FILTER(STRSTARTS(STR(?s), STR(aim:)))
    }
    """
    result = input.query(q1)
    g = Graph()
    g.bind('ddss', ns_ddss)
    g.bind('bot', ns_bot)
    g.bind('rdf', ns_rdf)
    g.bind('rdfs', ns_rdfs)
    g.bind('oms', ns_oms)
    g.bind('aim', ns_aim)
    for row in result:
        g.add(row)
    output_location = str(document_storage_location_rel+'/fork_exports')
    q2 = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    PREFIX """+nss_aim+"""
    SELECT ?storage_location
    WHERE {
        ?document ddss:storedAt ?storage_location .
        FILTER(STRSTARTS(STR(?document), STR(aim:)))
    }
    """
    document_locations_q = input.query(q2)
    zip_file_location = str(output_location+'/'+unique_fork_id+'_fork_export.zip')
    zip_file = zipfile.ZipFile(zip_file_location, 'w')
    for row in document_locations_q:
        location = row.storage_location.replace('', '')
        location_rev = location.replace(document_storage_location, document_storage_location_rel)
        document_name = location.rsplit('/', 1)[1]
        zip_file.write(location_rev, arcname=os.path.join(location_rev.replace(location_rev, str('documents/'+document_name))))
    ttl_destination = str(output_location+'/'+unique_aim_id+'_fork_rdf_export.ttl')
    file_system = FileSystemStorage(location=output_location)
    predicate1 = 'isForkOf'
    s1 = URIRef(ns_aim_default+unique_fork_id+'#')
    p1 = URIRef(ns_ddss+predicate1)
    o1 = URIRef(ns_aim_default+unique_aim_id+'#')
    g.add((
        s1, p1, o1,
    ))
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    predicate2 = 'hasFork'
    s2 = URIRef(ns_aim_default+unique_aim_id+'#')
    p2 = URIRef(ns_ddss+predicate2)
    o2 = URIRef(ns_aim_default+unique_fork_id+'#')
    input.add((
        s2, p2, o2,
    ))
    g.serialize(destination=ttl_destination)
    old_prefix = str('@prefix aim: <'+aim_default_namespace+unique_aim_id+'#>')
    new_prefix = str('@prefix aim: <'+aim_default_namespace+unique_fork_id+'#>')
    for line in fileinput.input(ttl_destination, inplace=True):
        line = line.replace(old_prefix, new_prefix)
        sys.stdout.write(line)
    zip_file.write(ttl_destination, arcname=os.path.join(ttl_destination.replace(ttl_destination, 'fork_rdf_export.ttl')))
    file_system.delete(unique_aim_id+'_fork_rdf_export.ttl')
    zip_file.close()
    return zip_file_location

def fork_import(uploaded_file, uploaded_file_name):
    unique_fork_id = uploaded_file_name.replace('_fork_export.zip', '')
    zip_file = zipfile.ZipFile(uploaded_file, 'r')
    import_rdf_zip = zip_file.open('fork_rdf_export.ttl')
    import_rdf = Graph()
    import_rdf.parse(import_rdf_zip)
    p1 = URIRef(ns_ddss+'storedAt')
    import_rdf.remove((
        None, p1, None
    ))
    q = """
    PREFIX """+nss_bot+"""
    PREFIX """+nss_ddss+"""
    PREFIX """+nss_rdf+"""
    PREFIX """+nss_org+"""
    PREFIX """+nss_foaf+"""
    PREFIX """+nss_oms+"""
    SELECT ?document ?doc_name
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
        ?document ddss:hasFileName ?doc_name .    
    }
    """
    documents = import_rdf.query(q)
    predicate = 'storedAt'
    p2 = URIRef(ns_ddss+predicate)
    new_storage_location = str(document_storage_location+'/'+unique_fork_id+'/')
    try:
        os.mkdir(os.path.join(document_storage_location, unique_fork_id))
    except OSError as e:
        if e.errno == 17:
            pass
    for doc in documents:
        source = zip_file.open(str('documents/'+doc.doc_name))
        target = open(os.path.join(new_storage_location, doc.doc_name), "wb")
        with source, target:
            shutil.copyfileobj(source, target)
        s2 = URIRef(doc.document)
        o2 = Literal(new_storage_location+doc.doc_name)
        import_rdf.add((
            s2, p2, o2,
        ))
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1, sparql_endpoint_2))
    for s, p, o in import_rdf.triples((None, None, None)):
        input.add((
            s, p, o
        ))