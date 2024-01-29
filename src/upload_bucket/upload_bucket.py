"""Upload file to jasmin/minio"""
from dotenv import load_dotenv
import click
import boto3
import os

@click.command()
@click.option("-i", "--input", required=True, help="Full path of input file")
@click.option("-o", "--output", required=True, help="Name of output file")
@click.option("-b", "--bucket", required=False, help="Name of the bucket to upload to")
def main(input: str, output: str, bucket: str):
    upload_bucket(input, output, bucket)

def upload_bucket(input, output, bucket):
    
    """
        upload_bucket: Upload file to bucket

        Args:
            input (str): input file name.
            output (str): output file name.

        Returns:
            None
    """

    try:
        client = boto3.client(
            aws_access_key_id=os.environ.get("TOKEN"),
            aws_secret_access_key=os.environ.get("SECRET"),
            endpoint_url=os.environ.get("ENDPOINT"),
            service_name='s3',
            verify=False
        )

        with open(f'{input}', mode="rb") as local_file:
            response = client.put_object(
                ACL='public-read-write',
                Body= local_file,
                Bucket = f"{bucket}",
                Key=f"{output}",
            )

        print("upload done")

    except Exception as e:
        print(e)
        raise


if __name__ == "__main__":
    main()
