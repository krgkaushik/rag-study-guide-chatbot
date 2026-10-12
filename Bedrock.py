import boto3
import json

client = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

model_id = "apac.amazon.nova-micro-v1:0"

question = input("Enter your Question: ")

response = client.invoke_model(
    modelId=model_id,
    body=json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": question
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 500,
            "temperature": 0.7
        }
    })
)

response_body = json.loads(response["body"].read())

print(response_body)``