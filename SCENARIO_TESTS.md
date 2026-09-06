# Later Connector — Scenario Tests (PST Part D)

## Plausible Scenario Testing
- S1: Connect account with OAuth Bearer Token via connect_later -> verified HTTP 200.
- S2: Query connected social profiles via list_profiles -> verify list of Instagram/Facebook/Pinterest profiles.
- S3: Fetch media assets from library via list_media -> verify image/video metadata.
- S4: Schedule social media post via create_post -> verified scheduled post returned.
- S5: Audit social media health via audit_social_health -> verified health report.
- S6: Delete scheduled post via delete_post -> verified removal.
- S7: Disconnect account via disconnect_later -> verified credential purge.

## Part D Checks
- D1 Deploy Verification: 24/24 platform checks passed.
- D2 Idempotency: Duplicate connection updates connection record without duplication.
- D3 Secret Leak Scan: Masked keys only; tokens never exposed in logs or ActionResult.
- D4 Regression Grep: Zero C30 email marketing remnants.
