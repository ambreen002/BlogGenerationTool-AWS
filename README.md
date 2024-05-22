# Blog Generation Using AWS Bedrock and S3

This project demonstrates how to generate a blog using AWS Bedrock's AI model and save the generated blog to an S3 bucket. The project consists of a Lambda function that handles the blog generation and storage, and an HTTP API Gateway that triggers the Lambda function via HTTP requests.

## Prerequisites

- AWS account with access to Bedrock and S3 services.
- Python 3.x installed.
- AWS CLI configured with appropriate permissions.

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
2. **Install dependencies**:
```bash
pip install boto3
```

## Configuration
Ensure you have the appropriate AWS credentials set up in your environment to allow boto3 to access Bedrock and S3 services.

## Code Overview
### Blog Generation
The generate_blog_using_bedrock function takes a blog topic as input and generates a blog using AWS Bedrock's language model.

```python
import boto3
import botocore.config
import json

def generate_blog_using_bedrock(blogtopic: str) -> str:
    prompt = f"""<s>[INST]Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
                               config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama2-13b-chat-v1")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""
```
### S3 Operations
The ensure_bucket_exists function checks if the S3 bucket exists, and if not, creates it.

```python
def ensure_bucket_exists(s3_client, bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket {bucket_name} created.")
        else:
            raise e
```

The save_blog_in_s3 function saves the generated blog to the specified S3 bucket.

```python
def save_blog_in_s3(s3_key, s3_bucket, generated_blog):
    s3 = boto3.client('s3')
    ensure_bucket_exists(s3, s3_bucket)

    try:
        s3.put_object(Body=generated_blog, Bucket=s3_bucket, Key=s3_key)
        print(f"Blog saved in s3 bucket {s3_bucket} with key {s3_key}")

    except Exception as e:
        print(f"Error saving the blog in s3: {e}")
```
### Lambda Handler
The lambda_handler function integrates the blog generation and S3 storage functionalities. It serves as the entry point for the Lambda function.

```python
from datetime import datetime

def lambda_handler(event, context):
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    generated_blog = generate_blog_using_bedrock(blogtopic=blogtopic)

    if generated_blog:
        current_time = datetime.now().strftime('%d%m%y%H%M%S')
        s3_key = f"blogoutput/{current_time}.txt"
        s3_bucket = "bedrocktestappambreen"
        save_blog_in_s3(s3_key, s3_bucket, generated_blog)
    else:
        print("No blog was generated")

    return {
        "statusCode": 200,
        'body': json.dumps('Blog Generation is completed.')
    }
```
## Deployment
1. **Package the Lambda function**:

```
zip -r function.zip .
```
2. **Create the Lambda function**:

```
aws lambda create-function --function-name BlogGenerator \
--zip-file fileb://function.zip --handler lambda_function.lambda_handler \
--runtime python3.8 --role arn:aws:iam::account-id:role/lambda-role
```

3. **Set up API Gateway**:

- Create a new HTTP API in API Gateway.
- Create a new resource and method (POST).
- Integrate the method with the Lambda function you created.
- Deploy the API to a new stage.

## Usage
Invoke the Lambda function with the following payload:
```
{
  "body": "{\"blog_topic\": \"Your blog topic here\"}"
}
```
