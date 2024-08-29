# aws-sam-to-terraform

AWS SAM to Terraform Converter

## Description

This project provides a tool to convert AWS Serverless Application Model (SAM) templates to Terraform configuration files. It parses SAM templates and generates equivalent Terraform resources, making it easier to migrate from SAM to Terraform or to use Terraform for deploying serverless applications originally defined in SAM.

## Features

- Converts AWS::Serverless::Function to aws_lambda_function
- Converts AWS::Serverless::HttpApi to aws_apigatewayv2_api
- Handles DynamoDB tables (AWS::DynamoDB::Table)
- Supports Step Functions (AWS::StepFunctions::StateMachine)
- Generates Terraform variables from SAM Parameters
- Supports environment-specific configurations
- Handles conditional resource creation based on SAM template conditions

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sauravpanda/aws-sam-to-terraform.git
   cd aws-sam-to-terraform
   ```

2. Install the required dependencies:
   ```
   poetry install
   ```

## Usage

1. Ensure your SAM template is in the same directory as the script, named `sam_template.yaml`.

2. Run the converter:
   ```
   poetry run sam2terra/converter.py sam_template.yaml
   ```

3. Check the `terraform_output` directory for the generated Terraform files.

## Generated Files

- `*_lambda.tf.json`: Lambda function configurations
- `*_api.tf.json`: API Gateway configurations
- `*_dynamodb.tf.json`: DynamoDB table configurations
- `*_step_function.tf.json`: Step Functions configurations
- `variables.tf.json`: Terraform variables
- `data_sources.tf.json`: Data sources for existing resources

## Environment-Specific Deployment

The converter generates an `environment_name` variable. When applying the Terraform configuration, specify the environment:

```
terraform apply -var="environment_name=dev"
```

This will replace all instances of `<EnvironmentName>` in the parameter default values with the specified environment name.

## Limitations

- Complex SAM features or nested intrinsic functions may not be fully supported
- Generated Terraform files may require manual adjustments for advanced scenarios
- Not all SAM resource types are currently supported

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
