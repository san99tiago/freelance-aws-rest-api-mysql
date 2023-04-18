import json
import os

from aws_cdk import (
    Stack,
    CfnOutput,
    Fn,
    Duration,
    aws_lambda,
    aws_iam,
    aws_apigateway,
    aws_secretsmanager,
)
from constructs import Construct

class CdkStackComputeApiLambda(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name_prefix: str,
        main_resources_name: str,
        deployment_environment: str,
        deployment_version: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.construct_id = construct_id
        self.name_prefix = name_prefix
        self.main_resources_name = main_resources_name
        self.deployment_environment = deployment_environment
        self.deployment_version = deployment_version

        # Obtain important values from outputs of other stacks
        self.load_values_from_other_stacks_outputs()

        # Lambda function creation
        self.create_policy_statement_for_lambda_to_secrets()
        self.create_lambda_role_policy()
        self.create_lambda_role()
        self.create_lambda_layer()
        self.create_lambda_function()

        # API gateway creation
        self.create_api_gateway()

        # Relevant CloudFormation outputs
        self.show_cloudformation_outputs()


    def load_values_from_other_stacks_outputs(self):
        """
        Method to load outputs from other stacks to use in this one (decoupled approach).
        """
        self.rds_host = Fn.import_value("RDSHost{}".format(self.deployment_environment))
        self.rds_db_name = Fn.import_value("RDSDBName{}".format(self.deployment_environment))
        self.secret_name_for_rds_credentials = Fn.import_value("SecretNameForRDSCredentials{}".format(self.deployment_environment))
        self.secret_name_for_api_credentials = Fn.import_value("SecretNameForAPICredentials{}".format(self.deployment_environment))

        print("Loaded <rds_host> value from other stack output is: ", self.rds_host)
        print("Loaded <rds_db_name> value from other stack output is: ", self.rds_db_name)
        print("Loaded <secret_name_for_rds_credentials> value from other stack output is: ", self.secret_name_for_rds_credentials)
        print("Loaded <secret_name_for_api_credentials> value from other stack output is: ", self.secret_name_for_api_credentials)


    def create_policy_statement_for_lambda_to_secrets(self):
        """
        Method to create IAM policy statement for secret-retrieval.
        """
        self.secrets_access_policy_statement = aws_iam.PolicyStatement(
            actions=[
                "secretsmanager:GetSecretValue",
                "kms:Decrypt",
                "kms:GenerateDataKey",
            ],
            effect=aws_iam.Effect.ALLOW,
            resources=["*"],
        )


    def create_lambda_role_policy(self):
        """
        Method to create IAM Policy based on all policy statements.
        """
        self.lambda_role_policy = aws_iam.Policy(
            self,
            id="{}-Policy".format(self.construct_id),
            policy_name="{}{}-Policy".format(self.name_prefix, self.main_resources_name),
            statements=[
                self.secrets_access_policy_statement,
            ],
        )


    def create_lambda_role(self):
        """
        Method that creates the role for Lambda function execution.
        """
        self.lambda_role = aws_iam.Role(
            self,
            id="{}-Role".format(self.construct_id),
            role_name="{}{}-Role".format(self.name_prefix, self.main_resources_name),
            description="Role for {} stack in ({}) environment".format(self.main_resources_name, self.deployment_environment),
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")],
        )

        self.lambda_role.attach_inline_policy(self.lambda_role_policy)


    def create_lambda_layer(self):
        """
        Method that creates the Lambda layer for python external dependencies.
        """
        # Get relative path for folder that contains Lambda function sources
        # ! Note--> we must obtain parent dirs to create path (that's why there are "os.path.dirname()")
        PATH_TO_LAYER_FOLDER = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "lambda_layer"
        )
        self.lambda_layer = aws_lambda.LayerVersion(
            self,
            id="{}-LambdaLayer".format(self.construct_id),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9],
            description="Lambda layer for python dependencies used for {} solution.".format(self.main_resources_name),
            code=aws_lambda.Code.from_asset(PATH_TO_LAYER_FOLDER),
        )


    def create_lambda_function(self):
        """
        Method that creates the main Lambda function.
        """
        # Get relative path for folder that contains Lambda function sources
        # ! Note--> we must obtain parent dirs to create path (that's why there is "os.path.dirname()")
        PATH_TO_FUNCTION_FOLDER = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "lambda_code"
        )
        print("Source code for lambda function obtained from: ", PATH_TO_FUNCTION_FOLDER)

        self.lambda_function = aws_lambda.Function(
            self,
            id="{}-Lambda".format(self.construct_id),
            function_name="{}{}".format(self.name_prefix, self.main_resources_name),
            code=aws_lambda.Code.from_asset(PATH_TO_FUNCTION_FOLDER),
            handler="lambda_function.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            environment={
                "RDS_HOST": self.rds_host,
                "RDS_DATABASE": self.rds_db_name,
                "RDS_SECRET_NAME": self.secret_name_for_rds_credentials,
                "API_SECRET_NAME": self.secret_name_for_api_credentials,
            },
            description="Lambda for {} functionalities (connects with rds to read leads and record API calls) in ({}) environment.".format(self.main_resources_name,self.deployment_environment),
            layers=[self.lambda_layer],
            role=self.lambda_role,
            timeout=Duration.minutes(1),
            memory_size=512,
        )

        self.lambda_function.add_alias(self.deployment_environment)


    def create_api_gateway(self):
        """
        Method that creates the API Gateway.
        """

        self.api = aws_apigateway.LambdaRestApi(
            self,
            id="{}-RestApi".format(self.construct_id),
            rest_api_name="{}{}".format(self.name_prefix, self.main_resources_name),
            description="API to create/read leads for the {} stack for ({}) environment".format(self.main_resources_name, self.deployment_environment),
            handler=self.lambda_function,
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET"],
            ),
            deploy_options=aws_apigateway.StageOptions(
                stage_name=self.deployment_version,
                description="{} release for handling requests that interact with the {} stack".format(self.deployment_environment, self.main_resources_name),
            ),
            deploy=True,
            retain_deployments=False,
            proxy=False,
        )

        self.leads_resource = self.api.root.add_resource("leads")
        self.leads_resource.add_method("GET") # GET /leads


    def show_cloudformation_outputs(self):
        """
        Method to create/add the relevant CloudFormation outputs.
        """
        CfnOutput(
            self,
            "DeploymentVersion",
            value=self.deployment_version,
            description="Current deployment's version",
        )

        CfnOutput(
            self,
            "DeploymentEnvironment",
            value=self.deployment_environment,
            description="Deployment environment",
        )

        CfnOutput(
            self,
            "NamePrefixes",
            value=self.name_prefix,
            description="Name prefixes for the resources",
        )

        CfnOutput(
            self,
            "LambdaFunctionARN",
            value=self.lambda_function.function_arn,
            description="ARN of the created Lambda function",
        )

        CfnOutput(
            self,
            "LambdaFunctionRoleARN",
            value=self.lambda_function.role.role_arn,
            description="Role for the created Lambda function",
        )

        CfnOutput(
            self,
            "BaseApiUrl",
            value=self.api.rest_api_id,
            description="Base URL for the API endpoint (includes latest stage)",
        )

        CfnOutput(
            self,
            "CompleteApiUrl",
            value="{}{}".format(self.api.url, "leads"),
            description="Complete URL for the API endpoint",
        )
        CfnOutput(
            self,
            "CompleteApiUrlWithQueryParams",
            value="{}{}?username=username&password=password&supplier_id=supplier_id&agent_id=agent_id&lead_id=lead_id".format(self.api.url, "leads"),
            description="Complete URL for the API endpoint",
        )
