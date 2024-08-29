import json

def generate_lambda_function(name, data):
    properties = data['Properties']
    print(properties)
    terraform_resource = {
        'resource': {
            'aws_lambda_function': {
                name: {
                    'function_name': properties['FunctionName'],
                    'handler': properties['Handler'],
                    'runtime': properties['Runtime'],
                    'memory_size': properties['MemorySize'],
                    'timeout': properties['Timeout'],
                    'tracing_config': {
                        'mode': 'Active' if properties['Tracing'] == 'Active' else 'PassThrough'
                    },
                    'environment': {
                        'variables': properties.get('Environment', {}).get('Variables')
                    }
                }
            },
            'aws_iam_role': {
                f"{name}_role": {
                    'name': f"{name}-role",
                    'assume_role_policy': json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Action": "sts:AssumeRole",
                                "Principal": {
                                    "Service": "lambda.amazonaws.com"
                                },
                                "Effect": "Allow"
                            }
                        ]
                    })
                }
            }
        }
    }
    
    terraform_resource['resource']['aws_lambda_function'][name]['role'] = f"${{aws_iam_role.{name}_role.arn}}"
    
    return terraform_resource

def generate_http_api(name, data):
    properties = data['Properties']
    
    return {
        'resource': {
            'aws_apigatewayv2_api': {
                name: {
                    'name': f"{name}-HttpApi",
                    'protocol_type': 'HTTP',
                    'body': json.dumps(properties['DefinitionBody'])
                }
            }
        }
    }

def generate_variables(parameters):
    return {
        'variable': {
            param_name: {
                'type': 'string',
                'default': param_data.get('Default', '')
            }
            for param_name, param_data in parameters.items()
        }
    }


def generate_dynamodb_table(name, data):
    properties = data['Properties']
    
    terraform_resource = {
        'resource': {
            'aws_dynamodb_table': {
                name: {
                    'count': f"${{var.EnvConfig{name.lower()}AsString == 'false' ? 1 : 0}}",
                    'name': properties.get('TableName', name),
                    'billing_mode': properties.get('BillingMode', 'PROVISIONED'),
                    'hash_key': properties['KeySchema'][0]['AttributeName'],
                    'attribute': [
                        {
                            'name': attr['AttributeName'],
                            'type': attr['AttributeType']
                        } for attr in properties['AttributeDefinitions']
                    ]
                }
            }
        }
    }
    
    # Add range key if it exists
    if len(properties['KeySchema']) > 1:
        terraform_resource['resource']['aws_dynamodb_table'][name]['range_key'] = properties['KeySchema'][1]['AttributeName']
    
    # Add provisioned throughput if applicable
    if properties.get('BillingMode', 'PROVISIONED') == 'PROVISIONED':
        terraform_resource['resource']['aws_dynamodb_table'][name]['read_capacity'] = properties['ProvisionedThroughput']['ReadCapacityUnits']
        terraform_resource['resource']['aws_dynamodb_table'][name]['write_capacity'] = properties['ProvisionedThroughput']['WriteCapacityUnits']
    
    return terraform_resource

def generate_step_function(name, data):
    properties = data['Properties']
    
    terraform_resource = {
        'resource': {
            'aws_sfn_state_machine': {
                name: {
                    'name': properties.get('StateMachineName', name),
                    'role_arn': properties['RoleArn'],
                    'definition': json.dumps(properties['Definition'])
                }
            }
        }
    }
    
    return terraform_resource


def generate_data_sources(sam_data):
    conditions = sam_data.get('Conditions', {})
    parameters = sam_data.get('Parameters', {})
    
    data_sources = {'data': {}}
    
    for condition_name, condition in conditions.items():
        if condition_name.endswith('UseExistingResource'):
            resource_name = condition_name.replace('UseExistingResource', '')
            param_name = f"EnvConfig{resource_name.lower()}AsString"
            
            if param_name in parameters:
                data_sources['data']['aws_ssm_parameter'] = {
                    resource_name: {
                        'name': f"${{var.environment_name}}/{resource_name.lower()}"
                    }
                }
    
    return data_sources