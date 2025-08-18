from app.assets.controllers.base_s3 import S3Controller


class ProfilePicturesController(S3Controller):
    def bucket(self) -> str:
        return "profilepictures"
