#!/bin/bash

# First go to this same directory (must be run here)
cd ./cdk-solar-api/lambda_layer

# Add dependencies (for Python Lambda Layer)
pip install mysql-connector-python --target=./python
pip install aws_lambda_powertools --target=./python

# Now, the "python" folder will be used as part of the lambda layer...
# ... at the CDK deployment!

# # This would be the manual process (not necessary for CDK solution)
# # ZIP this "layer" folder (and upload it to create a Lambda Layer)
# zip -r layer.zip ./python
