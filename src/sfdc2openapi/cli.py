import click
from sfdc2openapi.utilities import Utilities

@click.command()
@click.option('--domain', '-d', 'domain', required=True, type=click.STRING, help='Salesforce domain name to connect to.')
@click.option('--version', '-v', 'version', required=True, type=click.STRING, help='Salesforce API version (e.g. "v64.0").')
@click.option('--object', '-o', 'object', required=True, type=click.STRING, help='Salesforce object to include in the generated Open API definition.')
@click.option('--output', '-O', 'output', required=True, type=click.STRING, help='Output path where the generated Open API definition should be saved.')
@click.option('--client-id', '-i', 'client_id', required=False, type=click.STRING, help='(Optional) Client ID used to connect to Salesforce. If not specified, then the value will be read from the environment variable named "SFDC_CLIENT_ID".')
@click.option('--client-secret', '-s', 'client_secret', required=False, type=click.STRING, help='(Optional) Client ID used to connect to Salesforce. If not specified, then the value will be read from the environment variable named "SFDC_CLIENT_SECRET".')
@click.option('--debug', '-D', 'debug', flag_value=True, required=False, type=click.BOOL, is_flag=True, help='Flag to print debugging info to the terminal.')
def main(domain, version, object, output, client_id, client_secret, debug):
    
    utilities = Utilities(domain=domain, client_id=client_id, client_secret=client_secret, version=version, object=object)
    utilities.getObjectMetadata(debug=debug)
    utilities.generateOpenApi(output=output)

if __name__ == '__main__':
    main()