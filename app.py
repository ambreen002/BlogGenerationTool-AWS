import boto3
import botocore.config
import json
from datetime import datetime

def generate_blog_using_bedrock(blogtopic:str) -> str:
    prompt=f"""<s>[INST]Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """

    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        bedrock=boto3.client("bedrock-runtime", region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300, retries={"max_attempts":3}))
        response=bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama2-13b-chat-v1")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""
    
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
    
def save_blog_in_s3(s3_key, s3_bucket, generated_blog):
    s3=boto3.client('s3')
    ensure_bucket_exists(s3, s3_bucket)

    try:
        s3.put_object(Body=generated_blog, Bucket=s3_bucket, Key=s3_key)
        print(f"Blog saved in s3 bucket {s3_bucket} with key {s3_key}")

    except Exception as e:
        print(f"Error saving the blog in s3: {e}")

def lambda_handler(event, context):
    event=json.loads(event['body'])
    blogtopic=event['blog_topic']

    generated_blog=generate_blog_using_bedrock(blogtopic=blogtopic)

    if generated_blog:
        current_time=datetime.now().strftime('%d%m%y%H%M%S')
        s3_key=f"blogoutput/{current_time}.txt"
        s3_bucket="bedrocktestappambreen"
        save_blog_in_s3(s3_key, s3_bucket, generated_blog)

    else:
        print("No blog was generated")

    return {
        "statusCode": 200,
        'body':json.dumps('Blog Generation is completed.')
    }
        
        




