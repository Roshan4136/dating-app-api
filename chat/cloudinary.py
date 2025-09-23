import cloudinary.uploader

def upload_file(file, resource_type="auto", folder="chat_media"):
    """
    Upload a file (bytes or file-like object) to Cloudinary.

    Args:
        file_bytes: bytes or file-like object (from request.FILES or bytes)
        resource_type: "image", "video", or "auto"
        folder: folder path in Cloudinary

    Returns:
        URL string of uploaded file
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            resource_type=resource_type
        )
        print("cloudinary upload result:", result)
        return result.get("secure_url")
    except Exception as e:
        print("Cloudinary upload error:", e)
        return None
