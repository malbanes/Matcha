from flask import current_app
import boto3, botocore
import hashlib
import logging
from botocore.exceptions import ClientError


def upload_file_to_s3(file, bucket_name, path):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=current_app.config["S3_KEY"],
        aws_secret_access_key=current_app.config["S3_SECRET"],
    )
    path = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    file.filename = str(path) + "/" + file.filename
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ContentType": file.content_type  # Set appropriate content type as per the file
            },
        )
    except Exception as e:
        #print("Something Happened: ", e)
        return e
    return (
        "{}{}".format(current_app.config["S3_LOCATION"], file.filename),
        file.filename,
    )


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3 = boto3.client(
        "s3",
        aws_access_key_id=current_app.config["S3_KEY"],
        aws_secret_access_key=current_app.config["S3_SECRET"],
    )
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
