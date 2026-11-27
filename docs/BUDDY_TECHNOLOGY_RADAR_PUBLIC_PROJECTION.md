# Buddy Technology Radar: Canonical Archive and Public Projection

## Why the split exists

The complete append-only technology discovery archive remains at `config/generated/buddy-technology-radar.json`. It preserves historical observations, source provenance, first-seen/last-seen timestamps, status and derived counts.

GitHub Pages is a zero-cost static prototype with a 52 MiB site-size ceiling. The previous public mirror grew the site to approximately 55.17 MiB and caused deployment-cost verification to fail. The public page does not need every historical observation in its initial download.

## Public projection

The Pages file `website/data/buddy-technology-radar.json` is now a bounded projection containing the newest 500 records by the canonical archive's existing order. The policy is configured in `config/buddy/technology-discovery-policy.json`:

- `public_site.maximum_records = 500`
- `public_site.projection_mode = newest_records_bounded_view`
- `public_site.canonical_archive = config/generated/buddy-technology-radar.json`

The projection contains:
- The newest records for interactive browsing.
- `archive_summary`, which preserves full-archive totals and source counts.
- `summary`, recalculated for the records actually delivered to the browser.
- `public_projection`, which states the limit, included count, archive count and canonical archive path.

The radar UI distinguishes the full archive total from the bounded records currently loaded. No canonical history is deleted or truncated.

## Rebuild and verify

Offline, no-network rebuild:

```bash
python3 tools/refresh_buddy_technology_radar.py --project
python3 tools/refresh_buddy_technology_radar.py --check
python3 -m unittest tests.test_buddy_technology_radar
python3 tools/check_deployment_cost_policy.py
```

The `--project` mode reads the canonical archive, validates it, writes only the bounded Pages projection and refreshes the policy mirror. It does not call external sources or alter the canonical archive.

The scheduled/manual `--refresh` mode remains responsible for discovering public metadata and updating the canonical archive. It then writes the bounded Pages projection.

## Verification boundary

A passing size check confirms the static payload fits the configured budget. It does not prove the Pages site is deployed or live. The complete canonical archive remains available in the repository; the public website exposes only the bounded view. Changing the limit requires re-running the deployment-cost check and radar tests.
