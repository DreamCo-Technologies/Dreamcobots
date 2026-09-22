# 20 memory places for Buddy

Cloud places get an export file. Buddy does not log into Google, Apple, or any cloud for you.

| # | Easy name | id |
|---|-----------|----|
| 1 | This computer | this_computer |
| 2 | Chats folder | chats_folder |
| 3 | Project notes | project_notes |
| 4 | This browser only | browser_only |
| 5 | A folder I choose | custom_folder |
| 6 | USB or external drive | usb_drive |
| 7 | GitHub export file | github_export |
| 8 | Google Drive | google_drive |
| 9 | Google Cloud Storage | google_cloud_storage |
| 10 | iCloud Drive | icloud_drive |
| 11 | Apple iCloud | apple_icloud |
| 12 | Dropbox | dropbox |
| 13 | Microsoft OneDrive | onedrive |
| 14 | Box | box |
| 15 | Proton Drive | proton_drive |
| 16 | Amazon S3 | amazon_s3 |
| 17 | Azure Blob Storage | azure_blob |
| 18 | Cloudflare R2 | cloudflare_r2 |
| 19 | Nextcloud or NAS | nextcloud |
| 20 | Backblaze B2 | backblaze_b2 |

```bash
python3 buddy/memory/memory_places.py places
python3 buddy/memory/memory_places.py choose icloud_drive
python3 buddy/memory/memory_places.py teach "Give short answers" --bot buddy
```
