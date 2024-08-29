import json
import os
from sam2terra.sam_parser import parse_sam_template
from sam2terra.terraform_generator import (
    generate_lambda_function,
    generate_http_api,
    generate_dynamodb_table,
    generate_step_function,
    generate_variables
)

def convert_sam_to_terraform(sam_template_path):
    # Parse SAM template
    sam_data = parse_sam_template(sam_template_path)
    
    # Create output directory
    os.makedirs('terraform_output', exist_ok=True)
    
    # Convert resources
    for resource_name, resource_data in sam_data['Resources'].items():
        resource_type = resource_data['Type']
        
        if resource_type == 'AWS::Serverless::Function':
            terraform_resource = generate_lambda_function(resource_name, resource_data)
            write_terraform_file(f'{resource_name}_lambda.tf.json', terraform_resource)
        elif resource_type == 'AWS::Serverless::HttpApi':
            terraform_resource = generate_http_api(resource_name, resource_data)
            write_terraform_file(f'{resource_name}_api.tf.json', terraform_resource)
        elif resource_type == 'AWS::DynamoDB::Table':
            terraform_resource = generate_dynamodb_table(resource_name, resource_data)
            write_terraform_file(f'{resource_name}_dynamodb.tf.json', terraform_resource)
        elif resource_type == 'AWS::StepFunctions::StateMachine':
            terraform_resource = generate_step_function(resource_name, resource_data)
            write_terraform_file(f'{resource_name}_step_function.tf.json', terraform_resource)
    
    # Generate data sources for existing resources
    generate_data_sources(sam_data)
    
    # Convert parameters
    variables = generate_variables(sam_data.get('Parameters', {}))
    write_terraform_file('variables.tf.json', variables)

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
    
    write_terraform_file('data_sources.tf.json', data_sources)

def write_terraform_file(filename, content):
    with open(f'terraform_output/{filename}', 'w') as f:
        json.dump(content, f, indent=2)

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: sam-to-terraform <path_to_sam_template>")
        sys.exit(1)
    
    sam_template_path = sys.argv[1]
    convert_sam_to_terraform(sam_template_path)
    print("Conversion completed. Check the 'terraform_output' directory for results.")

if __name__ == "__main__":
    main()