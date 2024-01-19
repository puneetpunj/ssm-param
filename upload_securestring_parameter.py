"""
Script for updating AWS Systems Manager Parameter Store SecureString parameters from a CSV file.

Usage:
    python upload_securestring_parameter.py <environment_name>

e.g:
    python upload_securestring_parameter.py test
"""
import csv
import subprocess
import sys

# AWS CLI command to update the SecureString parameter
def update_parameter(param_name, value):
    """
    Update AWS Systems Manager Parameter Store SecureString parameter.

    Args:
        parameter_name (str): The name of the parameter.
        secure_value (str): The secure value for the parameter.
        environment_name (str): The name of the environment.

    Returns:
        None
    """
    command = (
        f'aws ssm put-parameter --name {param_name} '
        f'--value {value} --type SecureString --overwrite '
        f'--no-cli-pager'
    )
    try:
        print(f"Updating parameter: {param_name}")
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print(f"Error updating parameter {parameter_name}: {exc}")
        sys.exit(1)

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python script.py <environment_name>")
    sys.exit(1)

# Extract the environment name from the command line arguments
environment_name = sys.argv[1]
file_name = f"{environment_name}-params.csv"

# Read CSV file and update parameters
with open(file_name, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        parameter_name = f"/lucidity/{environment_name}/{row['ParameterName']}"
        secure_value = row['SecureValue']

        # Call the function to update the SecureString parameter
        update_parameter(parameter_name, secure_value)
