import asyncio
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, contents: bytes, key: str ):
        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=contents,
                )
                print(f"File {key} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def get_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                # with open(destination_path, "wb") as file:
                #     file.write(data)
                print(f"File {object_name} downloaded")
                return data
        except ClientError as e:
            print(f"Error downloading file: {e}")


# async def main():
#     s3_client = S3Client(
#         access_key="691a26fb9f03473e95db9fdacc9af1d9",
#         secret_key="226e51b0eb864925908ac11fc7746504",
#         endpoint_url="https://s3.ru-7.storage.selcloud.ru",
#         bucket_name="sadaka",
#     )
#
#     # Проверка, что мы можем загрузить, скачать и удалить файл
#     # await s3_client.upload_file("test.txt")
#     await s3_client.upload_file("move.mp4")
#     # await s3_client.get_file("test.txt", "text_local_file.txt")
#     # await s3_client.delete_file("test.txt")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())

