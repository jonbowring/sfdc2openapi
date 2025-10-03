sfdc2openapi
============

Salesforce to OpenAPI 3.0 Utility

**Description:**

A utility for generating OpenAPI 3.0 definitions for Salesforce objects.

**Installation:**

Run the following commands to install the utility:

```
git clone https://github.com/jonbowring/sfdc2openapi.git

python -m build
```

**Usage:**

    sfdc2openapi [OPTIONS] [ARGS]

**Options:**

  -d, --domain TEXT         Salesforce domain name to connect to.  [required]
  -v, --version TEXT        Salesforce API version (e.g. "v64.0").  [required]
  -o, --object TEXT         Salesforce object to include in the generated Open
                            API definition.  [required]
  -O, --output TEXT         Output path where the generated Open API
                            definition should be saved.  [required]
  -i, --client-id TEXT      (Optional) Client ID used to connect to
                            Salesforce. If not specified, then the value will
                            be read from the environment variable named
                            "SFDC_CLIENT_ID".
  -s, --client-secret TEXT  (Optional) Client ID used to connect to
                            Salesforce. If not specified, then the value will
                            be read from the environment variable named
                            "SFDC_CLIENT_SECRET".
  -D, --debug               Flag to print debugging info to the terminal.
  --help                    Show this message and exit.

**Examples:**

Example 1: Generating an OpenAPI 3.0 definition for the v64 Contact object

```
sfdc2openapi --domain 'dummy-domain.develop.my.salesforce.com' --object 'Contact' --output 'Salesforce_Contact.json' --version 'v64.0'
```