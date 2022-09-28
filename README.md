# DDSS
Durabel Data Storage System (DDSS) | Graduation Project for the MSc. Construction Management and Engineering at Eindhoven University of Technology.

In order to run DDSS, you need the following dependencies:

1) Python (version 3)
2) Django Framework (version 4.0)
3) Python package: rdflib
4) Python package: ifcopenshell
5) GraphDB

To use DDSS, follow these steps:

1) Install all dependencies mentioned above.
2) Open GraphDB, and create a new repository via 'Setup' > 'Repositories' > 'Create new repository'. Select 'GraphDB Free', define a 'Repository ID', and leave all other settings at their default value.
3) Create a folder on your computer where you want to store DDSS and name it 'ddss'. Download all content from this repository and place it in this folder.
4) Open the file 'settings.py' in the folder 'ddss' (ddss/ddss/settings.py) and define the settings in row 140-144 as described below.

  GraphDB_Repository_ID = 'test_repo'
  --> Replace 'test_repo' with the Repository ID' defined in step 2.

  Media_root_location = 'C:/Users/chiel/Desktop/django_ddss/ddss/'
  --> Replace with the location on your devices hard drive where the ddss folder is stored.

  AIM_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/aims/'
  --> Define the default namespace of AIMs.

  ORGANIZATION_DEFAULT_NAMESPACE = 'https://github.com/chielvanderpas/oms#'
  --> Define the default namespace of organisations.

  CURRENT_ORG = 'https://github.com/chielvanderpas/oms#fictional_test_org'
  --> Define the URI of the current organisation hosting DDSS.

5) Open GraphDB if GraphDB is not running yet. 
6) Open the root folder of your ddss installation in a command line interface.
7) Run the command 'python manage.py runserver'.
8) Open your webbrowser and navigate to '127.0.0.1:8000'. This should bring you to the DDSS dashboard. Here you can create an account and start using DDSS.

DDSS uses RDF for storing data. This data is structured according to the DDSS ontology. For more information about this ontology, see https://chielvanderpas.github.io/ddss-ontology/.

![DDSS PoC dashboard home page](https://user-images.githubusercontent.com/94625420/191916879-df5af4c5-f085-482f-b5c7-089b02f87bc6.png)
