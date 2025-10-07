import json
import os
import requests
from pathlib import Path
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

class Utilities:
    
    def __init__(self, domain, client_id, client_secret, version, object):
        
        # Get the current script path
        self.class_path = Path(__file__)
        
        # Initialise the global variables
        self.metadata = {}
        self.openapi_template = {}
        self.domain = domain
        self.version = version
        self.object = object
        
        # Authenticate with Salesforce
        if not client_id:
            client_id = os.environ['SFDC_CLIENT_ID']
        if not client_secret:
            client_secret = os.environ['SFDC_CLIENT_SECRET']
        token_url = f'https://{ domain }/services/oauth2/token'
        self.client = BackendApplicationClient(client_id=client_id)
        self.oauth = OAuth2Session(client=self.client)
        self.token = self.oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
        
        # Read the openapi template
        with open(self.class_path.parent / 'config/openapi_template.json', 'r', encoding='utf-8') as file:
            self.openapi_template = json.load(file)

    def getTemplate(self):
        return self.openapi_template
    
    def debugRequest(self, r, attempts=0):
        print('\n')
        print('Attempts: ' + str(attempts))
        print('Method: ' + r.request.method)
        print('Headers: ' + str(r.request.headers))
        print('URL: ' + r.request.url)
        print('Body: ' + str(r.request.body))
        print('Hooks: ' + str(r.request.hooks))
        print('Status: ' + str(r.status_code))
        print('Response: ' + r.text)
        print('\n')
    
    def getObjectMetadata(self, debug):

        url = f'https://{ self.domain }/services/data/{ self.version }/sobjects/{ self.object }/describe'
        headers = { 'Accept': 'application/json' }
        r = self.oauth.get(url, headers=headers)
        
        if debug:
            self.debugRequest(r)

        # Handle the response
        if r.status_code < 200 or r.status_code > 299:
            resp = {
                'status': r.status_code,
                'text': r.text
            }
            raise ValueError(resp)
        else:
            self.metadata = r.json()

    def generateOpenApi(self, output):

        # Define the type mapping:
        map_types = {
            'address': 'object',
            'anyType': 'string',
            'calculated': 'string',
            'combobox': 'string',
            'boolean': 'string',
            'currency': 'number',
            'date': 'string',
            'datetime': 'string',
            'double': 'number',
            'email': 'string',
            'encryptedstring': 'string',
            'id': 'string',
            'int': 'integer',
            'location': 'string',
            'masterrecord': 'string',
            'multipicklist': 'string',
            'percent': 'number',
            'phone': 'string',
            'picklist': 'string',
            'reference': 'string',
            'string': 'string',
            'textarea': 'string',
            'url': 'string'
        }

        # Build the properties
        properties = {}
        for field in self.metadata['fields']:
            property = {}
            
            if field['type'] not in map_types:
                print(f'WARNING: Unmapped field type "{ field['type'] }". Defaulting to string.')
                property['type'] = 'string'
            else:
                property['type'] = map_types[field['type']]

            # Check if a field should be read only
            if not field['updateable']:
                property['readOnly'] = True

            # Map the formats
            if field['type'] == 'date':
                property['format'] = 'date'
            elif field['type'] == 'datetime':
                property['format'] = 'date-time'
            elif field['type'] == 'int':
                property['format'] = 'int32'
            elif field['type'] == 'percent':
                property['format'] = 'double'

            # Save the property
            properties[field['name']] = property

        # Initialise the swagger
        swagger = self.openapi_template

        # Add the new QueryResult schema
        query_name = 'QueryResult' + self.object
        query_result_schema = swagger['components']['schemas']['QueryResult']
        query_result_schema['properties']['records']['items']['properties'] = properties

        # Add the new SObject schema
        sobject_name = 'SObject' + self.object
        sobject_schema = swagger['components']['schemas']['SObject']
        del sobject_schema['properties']['Id']
        sobject_schema['properties'].update(properties)

        # Update the URL
        swagger['servers'][0]['url'] = f'https://{ self.domain }/services/data/{ self.version }'

        # Add the new schemas
        swagger['components']['schemas'][query_name] = query_result_schema
        swagger['components']['schemas'][sobject_name] = sobject_schema

        # Update the query path
        swagger['paths']['/query']['get']['operationId'] = swagger['paths']['/query']['get']['operationId'] + self.object
        swagger['paths']['/query']['get']['responses']['200']['content']['application/xml']['schema']['$ref'] = '#/components/schemas/' + query_name
        swagger['paths']['/query']['get']['responses']['200']['content']['application/json']['schema']['$ref'] = '#/components/schemas/' + query_name

        # Update the create path
        path_name = '/sobjects/' + self.object
        action = 'post'
        swagger['paths'][path_name] = swagger['paths'].pop('/sobjects/{sObject}')
        del swagger['paths'][path_name]['get']
        swagger['paths'][path_name][action]['operationId'] = swagger['paths'][path_name][action]['operationId'] + self.object
        swagger['paths'][path_name][action]['parameters'] = [obj for obj in swagger['paths'][path_name][action]['parameters'] if obj['name'] != 'sObject']
        del swagger['paths'][path_name][action]['requestBody']['content']['application/json']['examples']
        swagger['paths'][path_name][action]['requestBody']['content']['application/json']['schema']['$ref'] = '#/components/schemas/' + sobject_name

        # Update the get object path
        path_name = '/sobjects/' + self.object + '/{id}'
        swagger['paths'][path_name] = swagger['paths'].pop('/sobjects/{sObject}/{id}')
        action = 'get'
        swagger['paths'][path_name][action]['operationId'] = swagger['paths'][path_name][action]['operationId'] + self.object
        swagger['paths'][path_name][action]['parameters'] = [obj for obj in swagger['paths'][path_name][action]['parameters'] if obj['name'] != 'sObject']
        swagger['paths'][path_name][action]['responses']['200']['content']['application/json']['schema']['$ref'] = '#/components/schemas/' + sobject_name

        # Update the delete object path
        action = 'delete'
        swagger['paths'][path_name][action]['operationId'] = swagger['paths'][path_name][action]['operationId'] + self.object
        swagger['paths'][path_name][action]['parameters'] = [obj for obj in swagger['paths'][path_name][action]['parameters'] if obj['name'] != 'sObject']

        # Update the patch object path
        action = 'patch'
        swagger['paths'][path_name][action]['operationId'] = swagger['paths'][path_name][action]['operationId'] + self.object
        swagger['paths'][path_name][action]['parameters'] = [obj for obj in swagger['paths'][path_name][action]['parameters'] if obj['name'] != 'sObject']
        del swagger['paths'][path_name][action]['requestBody']['content']['application/json']['examples']
        swagger['paths'][path_name][action]['requestBody']['content']['application/json']['schema']['$ref'] = '#/components/schemas/' + sobject_name

        with open(output, 'w', encoding='utf-8') as file:
            json.dump(swagger, file, indent=4)