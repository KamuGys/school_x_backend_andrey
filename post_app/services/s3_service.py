import aioboto3
from post_app.core.config import settings


class S3Service:

    async def upload_file(self, file, filename):

        if not settings.AWS_ACCESS_KEY:
            return None

        try:
            session = aioboto3.Session()

            async with session.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY,
            ) as s3:

                await s3.put_object(
                    Bucket=settings.AWS_BUCKET,
                    Key=filename,
                    Body=file
                )

            return f"https://{settings.AWS_BUCKET}.s3.amazonaws.com/{filename}"

        except Exception as e:
            print("s3 error:", e)
            return None