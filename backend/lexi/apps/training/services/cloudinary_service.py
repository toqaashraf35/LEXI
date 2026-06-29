import cloudinary.uploader


def upload_video(file_path):
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="video",
        folder="lexi/training_videos",
    )
    return result.get("secure_url")