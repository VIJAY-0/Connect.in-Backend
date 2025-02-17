# backend/api/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.files.base import ContentFile
from django.utils import timezone

from PIL import Image
from io import BytesIO



class User(AbstractUser):
    # Add related_name to the inherited fields to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Your custom fields
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')


    
class Wall(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="walls")
     name = models.CharField(max_length=255, unique=True)
     created_at = models.DateTimeField(auto_now_add=True)
     def __str__(self):
         return f"{self.user.username} Wall - {self.created_at}"



class WallThumbnail(models.Model):
    wall = models.ForeignKey(Wall, on_delete=models.CASCADE, related_name="thumbnails")
    image = models.ImageField(upload_to='wall_thumbnails/')



class Post(models.Model):
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    wall = models.ForeignKey(Wall, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)
    
    # This is our new field for storing an array (JSON) of additional image URLs.
    # Requires Django 3.1+ for built-in JSONField (or use a custom field if older).
    other_res = models.JSONField(blank=True, null=True, default=list)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s post - {self.created_at}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()  # We can keep this property since we'll have a reverse relation    
    
    def save(self, *args, **kwargs):
    
        print("Save called.... ")
        print("Save called.... ")
        print("Save called.... ")
        print("Save called.... ")
        print("Save called.... ")
        print("Save called.... ")
        
        """
        Override save() so we can:
        1. Save the original image as normal.
        2. Generate one or more additional compressed versions.
        3. Store their URLs in other_res as a JSON list.
        """
        # Step 1: Save the Post (and the original image) the normal way first.
        super().save(*args, **kwargs)

        # Step 2: If there's an image, open it and create optimized versions.
        if self.image and hasattr(self.image, 'path'):
            try:
                img = Image.open(self.image.path)
                img_format = 'WEBP'  # or 'JPEG', 'AVIF' (with pillow-avif-plugin), etc.
                # For demonstration, we create just one additional version.
                # You could create multiple (thumbnail, medium, large, etc.).

                # Example: a smaller, compressed version
                smaller_img = img.copy()
                smaller_img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                # smaller_img.thumbnail((800, 800), Image.ANTIALIAS)

                # Convert/Compress the image to the chosen format
                buffer = BytesIO()
                # "quality=70" means fairly decent compression. Tweak as needed.
                smaller_img.save(buffer, format=img_format, quality=10)

                # We must create a new Django file-like object to upload
                # For uniqueness, we can alter the filename extension or suffix
                optimized_name = f"{self.pk}_optimized.{img_format.lower()}"
                optimized_file = ContentFile(buffer.getvalue(), name=optimized_name)

                # Step 3: Actually save this second file somewhere in your media root.
                #         The easiest approach is to create a "secondary" ImageField
                #         on the fly or re-use the storage system:
                from django.core.files.storage import default_storage
                path = default_storage.save(
                    f'posts_other_res/{optimized_name}', optimized_file
                )
                # path is the relative storage path; to build the full URL, do:
                #   full_url = default_storage.url(path)

                # Optionally generate more versions if needed, storing each path or URL.

                # Step 4: Update other_res with the new version’s URL.
                # For instance, you can store a list of URL strings or structured data:
                stored_url = default_storage.url(path)

                # If other_res already contains data, we don’t want to lose it. So read it first:
                new_resolutions = self.other_res if self.other_res else []
                new_resolutions.append({
                    'label': 'smaller_webp',  # or "thumbnail", "avif", etc.
                    'url': stored_url,
                    'width': smaller_img.width,
                    'height': smaller_img.height
                })
                self.other_res = new_resolutions
                print("Other ress ... ", self.other_res)

                # Save again to update the other_res field
                super().save(update_fields=['other_res'])
            except Exception as e:
                # Log or handle the error. You may decide not to raise an exception
                # depending on how critical these extra images are.
                print(f"Error generating compressed versions: {e}")








class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s comment on {self.post}"

# class Likes(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.user.username}'s comment on {self.post}"

