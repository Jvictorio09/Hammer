#!/usr/bin/env python3
"""
Seed Case Studies / Projects by crawling a Google Drive folder

Recursively crawls a GDrive folder, treating each immediate child folder as a Project.
Only keeps landscape images (width >= height) for hero/thumb/full/gallery.

Usage:
  python manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design
  python manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-id=1 --dry-run --limit=3
  python manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design --mode=refresh --gallery-max=12
"""
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from myApp.models import Service, CaseStudy
from myApp.utils.google_drive_utils import get_drive_service, upload_from_google_drive_to_cloudinary
from googleapiclient.errors import HttpError


class Command(BaseCommand):
    help = "Seed Case Studies from Google Drive folder (landscape images only)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder-id",
            type=str,
            required=True,
            help="Google Drive folder ID (root folder containing project subfolders)"
        )
        parser.add_argument(
            "--service-id",
            type=int,
            help="Service ID to attach case studies to"
        )
        parser.add_argument(
            "--service-slug",
            type=str,
            help="Service slug to attach case studies to"
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Process only first N projects (for testing)"
        )
        parser.add_argument(
            "--gallery-max",
            type=int,
            default=24,
            help="Maximum gallery images per project (default: 24)"
        )
        parser.add_argument(
            "--mode",
            choices=["skip", "refresh"],
            default="skip",
            help="Duplicate handling: 'skip' existing or 'refresh' (update) them"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't write to DB, only log proposed actions"
        )
        parser.add_argument(
            "--cloudinary-folder",
            type=str,
            default="projects",
            help="Cloudinary folder prefix (default: 'projects')"
        )

    def handle(self, *args, **options):
        folder_id = options["folder_id"]
        service_id = options.get("service_id")
        service_slug = options.get("service_slug")
        limit = options.get("limit")
        gallery_max = options["gallery_max"]
        mode = options["mode"]
        dry_run = options["dry_run"]
        cloudinary_folder_prefix = options["cloudinary_folder"]

        # Validate service
        if not service_id and not service_slug:
            raise CommandError("Please specify --service-id or --service-slug")

        try:
            if service_id:
                service = Service.objects.get(id=service_id)
            else:
                service = Service.objects.get(slug=service_slug)
        except Service.DoesNotExist:
            raise CommandError(f"Service not found with {'id=' + str(service_id) if service_id else 'slug=' + service_slug}")

        self.stdout.write(self.style.SUCCESS(f"\n{'[DRY RUN] ' if dry_run else ''}Seeding Projects for Service: {service.title}"))
        self.stdout.write(f"Root GDrive Folder: {folder_id}")
        self.stdout.write(f"Mode: {mode}, Gallery Max: {gallery_max}\n")

        # Initialize Google Drive service
        try:
            drive_service = get_drive_service()
        except Exception as e:
            raise CommandError(f"Failed to initialize Google Drive service: {e}")

        # Discover projects (immediate child folders)
        self.stdout.write("🔍 Discovering project folders...")
        project_folders = self._list_folders(drive_service, folder_id)
        
        if not project_folders:
            self.stdout.write(self.style.WARNING("No project folders found."))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(project_folders)} project folder(s)"))

        # Apply limit if specified
        if limit:
            project_folders = project_folders[:limit]
            self.stdout.write(self.style.WARNING(f"Processing first {limit} project(s) only"))

        # Process each project
        stats = {
            "discovered": len(project_folders),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "no_landscape": 0,
            "errors": 0
        }

        for idx, folder in enumerate(project_folders, 1):
            folder_name = folder["name"]
            folder_id_inner = folder["id"]
            
            self.stdout.write(f"\n[{idx}/{len(project_folders)}] Processing: {folder_name}")
            
            try:
                # Collect all landscape images recursively
                landscape_images = self._collect_landscape_images_recursive(
                    drive_service, folder_id_inner, folder_name
                )
                
                if not landscape_images:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  No landscape images found. Skipping."))
                    stats["no_landscape"] += 1
                    continue
                
                self.stdout.write(f"  ✓ Found {len(landscape_images)} landscape image(s)")
                
                # Check if project already exists
                title = folder_name.strip()
                existing = CaseStudy.objects.filter(service=service, title=title).first()
                
                if existing and mode == "skip":
                    self.stdout.write(self.style.WARNING(f"  → Already exists (ID: {existing.id}). Skipping."))
                    stats["skipped"] += 1
                    continue
                
                # Upload images to Cloudinary
                if not dry_run:
                    uploaded_urls = self._upload_images_to_cloudinary(
                        drive_service,
                        landscape_images,
                        cloudinary_folder_prefix,
                        slugify(title),
                        gallery_max
                    )
                    
                    if not uploaded_urls:
                        self.stdout.write(self.style.ERROR(f"  ✗ Failed to upload images. Skipping."))
                        stats["errors"] += 1
                        continue
                else:
                    # Dry run: simulate URLs
                    uploaded_urls = {
                        "hero": f"https://cloudinary.example.com/{slugify(title)}/hero.jpg",
                        "thumb": f"https://cloudinary.example.com/{slugify(title)}/thumb.jpg",
                        "full": f"https://cloudinary.example.com/{slugify(title)}/full.jpg",
                        "gallery": [f"https://cloudinary.example.com/{slugify(title)}/gallery_{i}.jpg" for i in range(min(len(landscape_images) - 1, gallery_max))]
                    }
                
                # Prepare case study data
                case_study_data = {
                    "service": service,
                    "title": title,
                    "hero_image_url": uploaded_urls["hero"],
                    "thumb_url": uploaded_urls["thumb"],
                    "full_url": uploaded_urls["full"],
                    "gallery_urls": uploaded_urls["gallery"],
                    "summary": f"{title} — signature project.",
                    "description": f"{title} project seeded from Google Drive.",
                    "completion_date": None,
                    "scope": "Design & Build",
                    "size_label": "Custom",
                    "timeline_label": "12–16 weeks",
                    "status_label": "Completed",
                    "tags_csv": "portfolio,featured",
                    "cta_url": "",
                    "is_featured": False,
                    "sort_order": 0,
                }
                
                if not dry_run:
                    with transaction.atomic():
                        if existing:
                            # Update existing
                            for key, value in case_study_data.items():
                                if key != "service":
                                    setattr(existing, key, value)
                            existing.save()
                            self.stdout.write(self.style.SUCCESS(f"  ✓ Updated: {existing.title} (ID: {existing.id})"))
                            stats["updated"] += 1
                        else:
                            # Create new
                            case_study = CaseStudy.objects.create(**case_study_data)
                            self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {case_study.title} (ID: {case_study.id})"))
                            stats["created"] += 1
                else:
                    action = "UPDATE" if existing else "CREATE"
                    self.stdout.write(self.style.WARNING(f"  [DRY RUN] Would {action}: {title}"))
                    if existing:
                        stats["updated"] += 1
                    else:
                        stats["created"] += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error processing {folder_name}: {e}"))
                stats["errors"] += 1
                continue
        
        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("✔ Seed complete!"))
        self.stdout.write(f"  Discovered: {stats['discovered']}")
        self.stdout.write(f"  Created:    {stats['created']}")
        self.stdout.write(f"  Updated:    {stats['updated']}")
        self.stdout.write(f"  Skipped:    {stats['skipped']}")
        self.stdout.write(f"  No landscape: {stats['no_landscape']}")
        self.stdout.write(f"  Errors:     {stats['errors']}")
        
        if not dry_run:
            self.stdout.write(f"\n→ Visit /services/{service.slug}/ to see the projects gallery")
            self.stdout.write(f"→ Total Case Studies for this service: {service.case_studies.count()}")

    def _list_folders(self, service, parent_folder_id: str) -> List[Dict[str, str]]:
        """List immediate child folders in a parent folder."""
        try:
            query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            response = service.files().list(
                q=query,
                fields="files(id,name,createdTime)",
                orderBy="createdTime",
                pageSize=100
            ).execute()
            
            folders = response.get("files", [])
            return folders
        except HttpError as e:
            raise CommandError(f"Failed to list folders: {e}")

    def _collect_landscape_images_recursive(
        self, service, folder_id: str, folder_name: str
    ) -> List[Dict[str, Any]]:
        """
        Recursively collect all landscape images (width >= height) from folder and subfolders.
        Returns list of image file dicts sorted by createdTime.
        """
        landscape_images = []
        
        def _recurse(fid: str):
            try:
                query = f"'{fid}' in parents and trashed=false"
                response = service.files().list(
                    q=query,
                    fields="files(id,name,mimeType,createdTime,imageMediaMetadata)",
                    orderBy="createdTime",
                    pageSize=1000
                ).execute()
                
                items = response.get("files", [])
                
                for item in items:
                    mime_type = item.get("mimeType", "")
                    
                    # If it's a folder, recurse
                    if mime_type == "application/vnd.google-apps.folder":
                        _recurse(item["id"])
                    
                    # If it's an image, check if landscape
                    elif mime_type.startswith("image/"):
                        metadata = item.get("imageMediaMetadata", {})
                        width = metadata.get("width")
                        height = metadata.get("height")
                        
                        # Keep only if width >= height (landscape or square)
                        if width is not None and height is not None:
                            if width >= height:
                                landscape_images.append(item)
                                self.stdout.write(f"    → Landscape: {item['name']} ({width}x{height})")
                            else:
                                self.stdout.write(f"    ✗ Portrait (skipped): {item['name']} ({width}x{height})")
                        else:
                            self.stdout.write(f"    ✗ No dimensions (skipped): {item['name']}")
            
            except HttpError as e:
                self.stdout.write(self.style.ERROR(f"    Error reading folder {fid}: {e}"))
        
        _recurse(folder_id)
        
        # Sort by creation time
        landscape_images.sort(key=lambda x: x.get("createdTime", ""))
        
        return landscape_images

    def _upload_images_to_cloudinary(
        self,
        service,
        images: List[Dict[str, Any]],
        cloudinary_folder_prefix: str,
        project_slug: str,
        gallery_max: int
    ) -> Optional[Dict[str, Any]]:
        """
        Upload images to Cloudinary and return URLs.
        First image -> hero/thumb/full
        Rest -> gallery (up to gallery_max)
        """
        if not images:
            return None
        
        cloudinary_folder = f"{cloudinary_folder_prefix}/{project_slug}"
        uploaded = []
        
        for idx, img in enumerate(images):
            file_id = img["id"]
            file_name = img["name"]
            
            try:
                self.stdout.write(f"    ⬆️  Uploading {file_name}...")
                
                # Use existing upload function
                result, web_url, thumb_url, drive_metadata = upload_from_google_drive_to_cloudinary(
                    drive_file_id_or_url=file_id,
                    cloudinary_folder=cloudinary_folder,
                    public_id=f"{project_slug}_{idx:03d}",
                    tags=["project", project_slug],
                    auto_compress=True
                )
                
                uploaded.append({
                    "web_url": web_url,
                    "thumb_url": thumb_url,
                    "full_url": result.get("secure_url", web_url)
                })
                
                self.stdout.write(f"       ✓ Uploaded: {web_url}")
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"       ✗ Upload failed for {file_name}: {e}"))
                continue
        
        if not uploaded:
            return None
        
        # First image = hero/thumb/full
        hero = uploaded[0]["web_url"]
        thumb = uploaded[0]["thumb_url"]
        full = uploaded[0]["full_url"]
        
        # Rest = gallery (up to gallery_max)
        gallery = []
        for i in range(1, min(len(uploaded), gallery_max + 1)):
            gallery.append(uploaded[i]["web_url"])
        
        return {
            "hero": hero,
            "thumb": thumb,
            "full": full,
            "gallery": gallery
        }

