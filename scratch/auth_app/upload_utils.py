"""
Alexandria National University (ANU) - Faculty of Engineering
Introduction to Database Systems - Lab 3 (Fall 2026)

Secure Image Upload Utility:
- Validates file extensions (JPEG, PNG, WebP)
- Inspects binary content with PIL.Image (rejecting executables, SVG, disguised scripts)
- Enforces strict file-size limits (5 MB max)
- Generates cryptographically unique filenames (UUID4)
- Prevents path traversal and directory escape attacks
"""

import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

# Allowed raster image extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
# Supported PIL image formats
ALLOWED_PIL_FORMATS = {'JPEG', 'PNG', 'WEBP'}
# Maximum file size in bytes (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_file(filename):
    """Check if filename has a permitted raster extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_and_save_image(file_storage, upload_folder, subfolder=''):
    """
    Validates and saves an uploaded image file securely.
    
    Args:
        file_storage: werkzeug.datastructures.FileStorage object from request.files
        upload_folder: Absolute base upload directory (e.g. static/uploads)
        subfolder: Subdirectory name ('authors' or 'books')
        
    Returns:
        tuple (success: bool, result_or_error: str)
        If success: (True, relative_path_like_'static/uploads/authors/xyz.jpg')
        If failure: (False, friendly_error_message)
    """
    if not file_storage or not file_storage.filename or file_storage.filename.strip() == '':
        return False, "No file selected."

    filename = file_storage.filename.strip()

    # 1. Extension Check
    if not allowed_file(filename):
        return False, "Invalid image format. Only JPEG, PNG, and WebP raster images are allowed."

    # 2. File Size Check (Check stream length)
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size == 0:
        return False, "The uploaded file is empty."

    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        return False, f"File size exceeds the {max_mb}MB limit. Please upload a smaller image."

    # 3. Content Inspection: Open and verify raster image content using Pillow
    try:
        img = Image.open(file_storage)
        img_format = img.format
        if img_format not in ALLOWED_PIL_FORMATS:
            return False, f"Unsupported image content format: '{img_format}'. Only JPEG, PNG, and WebP are allowed."
        
        # Verify image integrity (detects malformed images and disguised binaries)
        img.verify()
    except Exception as e:
        return False, "Invalid image file. The file could not be decoded as a valid raster image."

    # Reset stream pointer after verify
    file_storage.seek(0)

    # 4. Generate Safe Unique Filename
    clean_original = secure_filename(filename)
    ext = clean_original.rsplit('.', 1)[1].lower() if '.' in clean_original else 'jpg'
    unique_name = f"{uuid.uuid4().hex}_{clean_original}"
    if len(unique_name) > 80:
        unique_name = f"{uuid.uuid4().hex}.{ext}"

    # Ensure destination directories exist
    target_dir = os.path.join(upload_folder, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    target_path = os.path.join(target_dir, unique_name)

    # 5. Persist file safely to disk
    try:
        # Re-open and save cleanly (strips potential metadata exploits)
        with Image.open(file_storage) as img_to_save:
            # Convert RGBA to RGB for JPEG if needed
            if ext in ('jpg', 'jpeg') and img_to_save.mode in ('RGBA', 'P', 'LA'):
                img_to_save = img_to_save.convert('RGB')
            img_to_save.save(target_path, optimize=True)
            
        relative_path = f"static/uploads/{subfolder}/{unique_name}".replace('//', '/')
        return True, relative_path
    except Exception as save_err:
        return False, f"Failed to save image on server: {str(save_err)}"
