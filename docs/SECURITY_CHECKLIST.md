# Security Verification Checklist

Do not mark an item complete until it has been tested against the running application.

- [ ] Production uses PostgreSQL, not SQLite.
- [ ] Production `JWT_SECRET` is unique and not committed.
- [ ] `.env` is ignored by Git and not present in repository history.
- [ ] Organization A cannot read or modify Organization B's events.
- [ ] Employee cannot create, update, or delete events.
- [ ] Employee cannot cancel another employee's registration.
- [ ] Admin cannot access data outside their own organization.
- [ ] Invalid, expired, and tampered JWTs are rejected.
- [ ] Duplicate active registrations are rejected.
- [ ] Event capacity is not exceeded under concurrent PostgreSQL requests.
- [ ] Oversized and malformed inputs are rejected.
- [ ] CORS contains only trusted browser origins.
- [ ] Production allowed-host list contains only intended hostnames.
- [ ] Public signup has abuse protection before real public use.
- [ ] Rate limiting is implemented at a distributed/platform layer.
- [ ] Database backups and restore procedure are tested.
- [ ] Dependency and secret scans are enabled.
- [ ] A qualified reviewer has performed a security review before real client use.

This checklist is a plan for verification, not evidence that the checks have passed.
