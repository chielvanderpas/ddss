from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'app'
urlpatterns = [
    ############################
    ### index models ###########
    path('', views.index, name='index'),
    ############################
    ### setup models ###########
    # path('setup/', views.write_ontology, name='setup'),
    ############################
    ### authentication model ###
    path('login/', views.login, name= 'login'),
    path('login/proceed/', views.login_proceed, name= 'login_proceed'),
    path('register/', views.register, name='register'),
    path('register/proceed/', views.register_proceed, name='register_proceed'),
    path('logout/', views.logout, name='logout'),
    ############################
    ### settings models ########
    path('settings/', views.settings, name='settings'),
    path('org/', views.edit_org, name='org'),
    path('org/actor/add/1/', views.edit_org_add, name='org_actor_add'),
    path('org/actor/add/2/', views.edit_org_add_proceed, name='org_actor_add_proceed'),
    path('org/actor/edit/1/', views.edit_org_edit, name='org_actor_edit'),
    path('org/actor/edit/2/', views.edit_org_edit_proceed, name='org_actor_edit_proceed'),
    ############################
    ### data request models ####
    path('search/content/', views.content, name='content'),
    path('instance/aim/content/', views.instance_aim_content, name='instance_aim_content'),
    path('instance/aim/dd/', views.instance_aim_dd, name='instance_aim_dd'),
    path('instance/event/', views.instance_event, name='instance_event'),
    path('instance/document/', views.instance_document, name='instance_document'),
    path('instance/document/download/', views.instance_document_download, name='instance_document_download'),
    path('instance/document/download/2/<str:file_path>', views.instance_document_download2, name='instance_document_download2'),
    path('instance/actor/', views.instance_actor, name='instance_actor'),
    path('instance/building/', views.instance_bot, name='instance_bot'),
    path('instance/datadrop/', views.instance_datadrop, name='instance_datadrop'),
    path('search/start/', views.search_start, name='search_start'),
    # path('search/results/', views.search_results, name='search_results'),
    path('search/sparql_query/1/', views.sparql_query_1, name='sparql_query_1'),  
    path('search/sparql_query/2/', views.sparql_query_2, name='sparql_query_2'),  
    ############################
    ### data drop models #######
    path('dd/welcome/', views.dd_welcome, name='dd_welcome'),
    path('dd/continue/', views.dd_continue, name='dd_continue'),
    path('dd/select_aim/', views.dd_select_aim, name='dd_select_aim'),
    path('dd/existing_aim/', views.dd_select_existing_aim, name='dd_select_existing_aim'),
    path('dd/new_aim/1/', views.dd_create_new_aim_1, name='dd_create_new_aim_1'),
    path('dd/new_aim/2/', views.dd_create_new_aim_2, name='dd_create_new_aim_2'),
    path('dd/upload_file/1/', views.dd_upload_file_1, name='dd_upload_file_1'),
    path('dd/upload_file/2/', views.dd_upload_file_2, name='dd_upload_file_2'),
    path('dd/upload_file/3/', views.dd_upload_file_3, name='dd_upload_file_3'),
    path('dd/upload_file/4/', views.dd_upload_file_4, name='dd_upload_file_4'),
    path('dd/upload_file/5/', views.dd_upload_file_5, name='dd_upload_file_5'),
    path('dd/upload_file/6/', views.dd_upload_file_6, name='dd_upload_file_6'),
    path('dd/select_event/', views.dd_select_event, name='dd_select_event'),
    path('dd/existing_event/1/', views.dd_select_existing_event_1, name='dd_select_existing_event_1'),
    path('dd/new_event/1/', views.dd_create_new_event_1, name='dd_create_new_event_1'),
    path('dd/new_event/2/', views.dd_create_new_event_2, name='dd_create_new_event_2'),
    path('dd/link_event/1/', views.dd_link_event_1, name='dd_link_event_1'),
    path('dd/link_event/2/', views.dd_link_event_2, name='dd_link_event_2'),
    path('dd/end/1/', views.dd_end_1, name='dd_end_1'),
    path('dd/end/2/', views.dd_end_2, name='dd_end_2'),
    ############################
    ### fork models ############
    path('fork/', views.fork, name='fork'),
    path('fork/export/1/', views.fork_export_1, name='fork_export_1'),
    path('fork/export/2/', views.fork_export_2, name='fork_export_2'),
    path('fork/import/1/', views.fork_import_1, name='fork_import_1'),
    path('fork/import/2/', views.fork_import_2, name='fork_import_2'),
    path('fork/import/3/', views.fork_import_3, name='fork_import_3'),
    path('fork/import/4/', views.fork_import_4, name='fork_import_4'),
    path('fork/import/5/', views.fork_import_5, name='fork_import_5'),
    ############################
    # path('ifc_viewer/', views.ifc_viewer, name='ifc_viewer'),
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
