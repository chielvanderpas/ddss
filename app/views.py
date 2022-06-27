from enum import unique
from http.client import HTTPResponse
from msilib.schema import File
from operator import contains
from tokenize import Name
from urllib import request
from django import views
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from rdflib import Namespace
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from . import models
import collections, os, sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

############################
### Authentication views ###
############################

def login(request):
    if request.user.is_authenticated:
        first_name = request.user.get_short_name()
        welcome_message = 'Welcome {}!'.format(first_name)
        return render(request, 'index.html', {'welcome_message':welcome_message, 'first_name':first_name})
    else:
        welcome_message = 'Welcome, please log in using your credentials.'
        return render(request, 'auth/login.html', {'welcome_message':welcome_message})

def login_proceed(request):
    input_username = request.POST.get('username')
    input_password = request.POST.get('password')
    output = models.login_model(request, input_username, input_password)
    if output == 'success':
        first_name = request.user.get_short_name()
        username = request.user.get_username()
        welcome_message = 'Welcome {}!'.format(first_name)
        unique_user_id = models.rq_user_id(username)
        request.session['unique_user_id'] = unique_user_id
        return render(request, 'index.html', {'welcome_message':welcome_message, 'first_name':first_name})
    else:
        welcome_message = 'Welcome, please log in using your credentials.'
        return render(request, 'auth/login.html', {'output':output, 'welcome_message':welcome_message})

def register(request):
    return render(request, 'auth/register.html')
    
def register_proceed(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')
    username = request.POST.get('email')
    password = request.POST.get('password')
    models.register_model(username, email, password, first_name, last_name, phone_number)
    success_message = 'Your account has successfully been created, please log in using your credentials.'
    return render(request, 'auth/login.html', {'welcome_message':success_message})

def logout(request):
    models.logout_model(request)
    return render(request, 'auth/logout.html')

######################
### Settings views ###
######################

@login_required
def settings(request):
    first_name = request.user.get_short_name()
    full_name = request.user.get_full_name()
    email = request.user.get_username()
    phone_number = models.rq_settings1(email)
    sparql_endpoint_1 = models.sparql_endpoint_1
    sparql_endpoint_2 = models.sparql_endpoint_2
    document_storage_location = models.document_storage_location
    aim_default_namespace = models.aim_default_namespace
    welcome_message = 'Welcome {}!'.format(first_name)
    return render(request, 'settings/settings.html', {'welcome_message':welcome_message,'first_name':first_name, 'full_name':full_name, 'email':email, 'phone_number':phone_number, 'sparql_endpoint_1':sparql_endpoint_1, 'sparql_endpoint_2':sparql_endpoint_2, 'document_storage_location':document_storage_location, 'aim_default_namespace':aim_default_namespace})

@login_required
def edit_org(request):
    first_name = request.user.get_short_name()
    existing_users = models.rq_event2()
    return render(request, 'settings/edit_org.html', {'first_name':first_name, 'existing_users':existing_users})

@login_required
def edit_org_add(request):
    first_name = request.user.get_short_name()
    existing_users = models.rq_event2()
    return render(request, 'settings/edit_org.html', {'first_name':first_name, 'existing_users':existing_users})

@login_required
def edit_org_edit(request):
    first_name = request.user.get_short_name()
    user = request.POST.get('user')
    user_id, user_name, user_email = user.split(',')
    return render(request, 'settings/edit_org_edit.html', {'first_name':first_name, 'user_id':user_id, 'user_name':user_name, 'user_email':user_email})

########################
### Index page views ###
########################

@login_required
def index(request):
    first_name = request.user.get_short_name()
    welcome_message = 'Welcome {}!'.format(first_name)
    return render(request, 'index.html', {'welcome_message':welcome_message,'first_name':first_name})

##########################
### Data request views ###
##########################

@login_required
def search_start(request):
    first_name = request.user.get_short_name()
    existing_aims = models.rq_aim()
    return render(request, 'rq/search_start.html', {'first_name':first_name, 'existing_aims':existing_aims})

@login_required
def sparql_query_1(request):
    first_name = request.user.get_short_name()
    return render(request, 'rq/sparql_query.html', {'first_name':first_name})

@login_required
def sparql_query_2(request):
    first_name = request.user.get_short_name()
    query_select = request.POST.get('select')
    query_where = request.POST.get('where')
    output = models.rq_sparql_query(query_select, query_where)
    return render(request, 'rq/sparql_query.html', {'first_name':first_name, 'output':output})


# @login_required
# def search_results(request):
#     first_name = request.user.get_short_name()
#     type = 'ddss:Maintenance'
#     output = models.rq_model5(type)
#     return render(request, 'rq/instance.html', {'first_name':first_name, 'output':output})

# @login_required
# def instance_event(request):
#     first_name = request.user.get_short_name()
#     instance = str('N23b6107e76834f8ba718911db1e1ade8')
#     output = models.rq_events1(instance)
#     return render(request, 'rq/instance_event.html', {'first_name':first_name, 'output':output})

# @login_required
# def instance_actor(request):
#     first_name = request.user.get_short_name()
#     instance = request.POST.get('actor')
#     output = models.rq_actors1(instance)
#     return render(request, 'rq/instance_actor.html', {'first_name':first_name, 'output':output})

#######################
### Data drop views ###
#######################

@login_required
def dd_welcome(request):
    first_name = request.user.get_short_name()
    current_dd_start_time = request.session.get('current_dd_start_time', None)
    duration_dd_check = models.dd_check_session_duration(current_dd_start_time)
    if duration_dd_check == True:
        disabled = ''
    else:
        disabled = 'disabled'
    return render(request, 'dd/dd_welcome.html', {'first_name':first_name, 'disabled':disabled})

@login_required
def dd_start(request):
    first_name = request.user.get_short_name()
    request.session['new_dd'] = True
    existing_aims_check = models.rq_aim()
    if existing_aims_check == []:
        disabled = 'disabled'
    else:
        disabled = ''
    return render(request, 'dd/dd_start.html', {'first_name':first_name, 'disabled':disabled})

@login_required
def dd_continue(request):
    first_name = request.user.get_short_name()
    request.session['new_dd'] = False
    o_aim = request.session.get('o_aim', None)
    existing_events_check = models.rq_event1(o_aim)
    if existing_events_check == []:
        disabled = 'disabled'
    else:
        disabled = ''
    visibility_status = 'submit'
    return render(request, 'dd/dd_select_event.html', {'first_name':first_name, 'disabled':disabled, 'visibility_status':visibility_status})

@login_required
def dd_create_new_aim_1(request):
    first_name = request.user.get_short_name()
    return render(request, 'dd/dd_create_new_aim.html', {'first_name':first_name})

@login_required
def dd_create_new_aim_2(request):
    first_name = request.user.get_short_name()
    aim_name = request.POST.get('aim_name')
    o_aim = models.dd_new_aim(aim_name)
    request.session['o_aim'] = o_aim
    new_dd = request.session.get('new_dd', None)
    if new_dd == True:
        user_id = request.session.get('unique_user_id', None)
        unique_dd_id = models.dd_create(o_aim, user_id)
        request.session['unique_dd_id'] = unique_dd_id
        request.session['current_dd_start_time'] = datetime.now().strftime("%Y-%m-%dT%H:%M")
    else:
        unique_dd_id = request.session.get('unique_dd_id', None)
    existing_events_check = models.rq_event1(o_aim)
    if existing_events_check == []:
        disabled = 'disabled'
    else:
        disabled = ''
    visibility_status = 'hidden'
    return render(request, 'dd/dd_select_event.html', {'first_name':first_name, 'output':unique_dd_id, 'disabled':disabled, 'visibility_status':visibility_status})

@login_required
def dd_select_existing_aim_1(request):
    first_name = request.user.get_short_name()
    existing_aims = models.rq_aim()
    return render(request, 'dd/dd_search_aim.html', {'first_name':first_name, 'existing_aims':existing_aims})

@login_required
def dd_select_existing_aim_2(request):
    first_name = request.user.get_short_name()
    request.session['o_aim'] = request.POST.get('aim_namespace')
    o_aim = request.session.get('o_aim', None)
    new_dd = request.session.get('new_dd', None)
    if new_dd == True:
        user_id = request.session.get('unique_user_id', None)
        unique_dd_id = models.dd_create(o_aim, user_id)
        request.session['unique_dd_id'] = unique_dd_id
        request.session['current_dd_start_time'] = datetime.now().strftime("%Y-%m-%dT%H:%M")
    else:
        unique_dd_id = request.session.get('unique_dd_id', None)
    existing_events_check = models.rq_event1(o_aim)
    if existing_events_check == []:
        disabled = 'disabled'
    else:
        disabled = ''
    visibility_status = 'hidden'
    return render(request, 'dd/dd_select_event.html', {'first_name':first_name, 'output':unique_dd_id, 'disabled':disabled, 'visibility_status':visibility_status})

@login_required
def dd_select_existing_event_1(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    existing_events = models.rq_event1(o_aim)
    return render(request, 'dd/dd_select_existing_event.html', {'first_name':first_name, 'existing_events':existing_events})

@login_required
def dd_select_existing_event_2(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    unique_dd_id = request.session.get('unique_dd_id', None)
    unique_event_id = request.POST.get('event')
    output = models.dd_event2(o_aim, unique_dd_id, unique_event_id)
    return render(request, 'dd/dd_upload_file.html', {'first_name':first_name, 'output':output})

@login_required
def dd_create_new_event_1(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    existing_events = models.rq_event1(o_aim)
    existing_actors = models.rq_event2(o_aim)
    return render(request, 'dd/dd_create_new_event.html', {'first_name':first_name, 'existing_events':existing_events, 'existing_actors':existing_actors})

@login_required
def dd_create_extra_event_1(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    existing_events = models.rq_event1(o_aim)
    existing_actors =models.rq_event2(o_aim)
    event_type = request.POST.get('event_type')
    event_description = request.POST.get('event_description')
    startdatetime = request.POST.get('startdatetime')
    enddatetime = request.POST.get('enddatetime')
    related_actor = request.POST.get('related_actor')
    super_event = request.POST.get('super_event')
    unique_dd_id = request.session.get('unique_dd_id', None)
    output = models.dd_event1(o_aim, event_type, event_description, startdatetime, enddatetime, related_actor, super_event, unique_dd_id)
    return render(request, 'dd/dd_create_new_event.html', {'output':output, 'first_name':first_name, 'existing_events':existing_events, 'existing_actors':existing_actors})

@login_required
def dd_create_new_event_2(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    event_type = request.POST.get('event_type')
    event_description = request.POST.get('event_description')
    startdatetime = request.POST.get('startdatetime')
    enddatetime = request.POST.get('enddatetime')
    related_actor = request.POST.get('related_actor')
    super_event = request.POST.get('super_event')
    unique_dd_id = request.session.get('unique_dd_id', None)
    output = models.dd_event1(o_aim, event_type, event_description, startdatetime, enddatetime, related_actor, super_event, unique_dd_id)
    return render(request, 'dd/dd_upload_file.html', {'output':output, 'first_name':first_name})

@login_required
def dd_upload_file_1(request):
    first_name = request.user.get_short_name()
    return render(request, 'dd/dd_upload_file.html', {'first_name':first_name})

@login_required
def dd_upload_file_2(request):
    first_name = request.user.get_short_name()
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = file_name.rsplit('.', 1)[1]
    file_size = uploaded_file.size
    if file_type == 'ifc' or file_type == 'pdf' or file_type == 'csv' or file_type == 'png' or file_type == 'jpg' or file_type == 'jpeg' or file_type == 'pcd' or file_type == 'txt':
        o_aim = request.session.get('o_aim', None)
        file_name_no_type = file_name.split(".")[0]
        file_exists_check = [f for f in os.listdir(models.document_storage_location) if f.startswith(file_name_no_type) and f.endswith(file_type)]
        timestamp = datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        file_name_rev = str(file_name_no_type+'_'+timestamp+'.'+file_type)
        file_system = FileSystemStorage()
        file_system.save(file_name_rev, uploaded_file)
        file_location = str(models.document_storage_location+'/'+file_name_rev)
    else:
        error_message = 'This file type cannot be uploaded. Please upload a file of one of the following types: ifc, pdf, csv, png, jpeg, pcd, txt.'
        return render(request, 'dd/dd_upload_file.html', {'first_name':first_name, 'error_message':error_message})
    if 'copy_in_original_format' in request.FILES:
        copy_in_original_format = request.FILES['copy_in_original_format']
        copy_name = copy_in_original_format.name
        copy_name_no_type = copy_name.split(".")[0]
        copy_type = copy_name.split(".")[1].lower()
        copy_name_rev = str(copy_name_no_type+'_'+timestamp+'.'+copy_type)
        file_system.save(copy_name_rev, copy_in_original_format)
        copy_location = str(models.document_storage_location+'/'+copy_name_rev)
    else:
        copy_name = None
        copy_type = None
        copy_location = None
    if file_exists_check != []:
        prev_version = models.dd_prev_version_check(file_exists_check, o_aim)
    else:
        prev_version = None
    message = 'The document has successfully been uploaded. Please enrich the documents metadata in order to make sure it will be stored correctly.'
    existing_actors = models.rq_event2(o_aim)
    output = models.dd_document1(o_aim, file_name_rev, file_type, file_location, copy_name, copy_type, copy_location, prev_version)
    return render(request, 'dd/dd_enrich_file.html', {'first_name':first_name, 'message':message, 'output':output, 'existing_actors':existing_actors})

@login_required
def dd_upload_file_3(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    unique_dd_id = request.session.get('unique_dd_id', None)
    unique_document_id = request.POST.get('unique_document_id')
    document_type = request.POST.get('document_type')
    document_storage_location = request.POST.get('document_storage_location')
    document_description = request.POST.get('document_description')
    document_unique_identifier = request.POST.get('document_unique_identifier')
    document_creation_software = request.POST.get('document_creation_software')
    document_creation_software_version = request.POST.get('document_creation_software_version')
    preservation_until_date = request.POST.get('preservation_until_date')
    content_type_documentation = request.POST.get('content_type_documentation')
    content_type_geometrical = request.POST.get('content_type_geometrical')
    content_type_alphanumerical = request.POST.get('content_type_alphanumerical')
    document_status = request.POST.get('document_status')
    responsible_actor = request.POST.get('responsible_actor')
    if 'prev_version_id' in request.POST:
        prev_version_id = request.POST.get('prev_version_id')
        prev_version_status = request.POST.get('prev_version_status')
    else:
        prev_version_id = None
        prev_version_status = None
    models.dd_document2(o_aim, unique_dd_id, unique_document_id, document_description, document_unique_identifier, document_creation_software, document_creation_software_version, preservation_until_date, content_type_documentation, content_type_geometrical, content_type_alphanumerical, document_status, prev_version_id, prev_version_status, responsible_actor)
    if document_type == 'ifc':
        request.session['unique_document_id'] = unique_document_id
        request.session['document_storage_location'] = document_storage_location
        model_data, existing_data, intersections = models.dd_ifc1(o_aim, document_storage_location)
        type_check = []
        if any(a.type == 'Site' for a in existing_data):
            type_check.append('Site')
        if any(a.type == 'Building' for a in existing_data):
            type_check.append('Building')
        if any(a.type == 'Storey' for a in existing_data):
            type_check.append('Storey')
        if any(a.type == 'Space' for a in existing_data):
            type_check.append('Space')
        if any(a.type == 'Element' for a in existing_data):
                type_check.append('Element')
        return render(request, 'dd/dd_ifc.html', {'first_name':first_name, 'model_data':model_data, 'existing_data':existing_data, 'intersections':intersections, 'type_check':type_check})
    else:
        if unique_dd_id == None:
            disabled = 'disabled'
        else:
            disabled = ''
        return render(request, 'dd/dd_end.html', {'first_name':first_name, 'disabled':disabled})

@login_required
def dd_upload_file_4(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    document_storage_location = request.session.get('document_storage_location', None)
    related_original = request.POST.get('related_original')
    related_new = request.POST.get('related_new')
    models.dd_ifc2(o_aim, related_original, related_new)
    model_data, existing_data, intersections = models.dd_ifc1(o_aim, document_storage_location)
    type_check = []
    if any(a.type == 'Site' for a in existing_data):
        type_check.append('Site')
    if any(a.type == 'Building' for a in existing_data):
        type_check.append('Building')
    if any(a.type == 'Storey' for a in existing_data):
        type_check.append('Storey')
    if any(a.type == 'Space' for a in existing_data):
        type_check.append('Space')
    if any(a.type == 'Element' for a in existing_data):
        type_check.append('Element')
    return render(request, 'dd/dd_ifc.html', {'first_name':first_name, 'model_data':model_data, 'existing_data':existing_data, 'intersections':intersections, 'related_new_guid':related_new, 'type_check':type_check})


@login_required
def dd_upload_file_5(request):
    first_name = request.user.get_short_name()
    o_aim = request.session.get('o_aim', None)
    unique_document_id = request.session.get('unique_document_id', None)
    document_storage_location = request.session.get('document_storage_location', None)
    unique_dd_id = request.session.get('unique_dd_id', None)
    model_data, existing_data, intersections = models.dd_ifc1(o_aim, document_storage_location)
    models.dd_ifc3(o_aim, unique_document_id, model_data, intersections)
    if unique_dd_id == None:
        disabled = 'disabled'
    else:
        disabled = ''
    success = 'Your ifc-model has been succesfully uploaded and processed.'
    return render(request, 'dd/dd_end.html', {'first_name':first_name, 'disabled':disabled, 'message':success})

@login_required
def dd_end(request):
    first_name = request.user.get_short_name()
    request.session['unique_dd_id'] = None
    request.session['current_dd_start_time'] = None
    return render(request, 'index.html', {'first_name':first_name})


















########################
### test environment ###
########################

# from . import serializers
# from rest_framework import serializers, viewsets, generics

# def write_ontology(request):
#     welcome_message = models.model_write_ontology()
#     return render(request, 'index.html', {'welcome_message':welcome_message})
