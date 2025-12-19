# WhatsApp Bridge & Archiver Bot Analysis

**Date:** December 18, 2025
**Issue:** Archiver bot repeatedly removed from bridged WhatsApp rooms

## Summary

The Message Archiver Bot (`@archiver:matrix.radx.dev`) was being removed from WhatsApp-bridged Matrix rooms with the message:

> "WhatsApp bridge bot removed Message Archiver Bot: User is not in remote chat"

This document captures the root cause analysis and proposed solutions.

---

## Root Cause Analysis

### Initial Hypothesis (Incorrect)

We initially suspected the issue was related to:
- Phone running out of battery
- WhatsApp session invalidation
- Server reboots causing reconnection issues

### Actual Root Cause

**The archiver removal was caused by the mautrix-whatsapp bridge's scheduled "portal resync" feature, not by phone/connection issues.**

#### Timeline of Events (December 17, 2025)

| Time (UTC) | Event |
|------------|-------|
| 18:38:40 | Message received in "XP Ops" WhatsApp group |
| 18:38:40 | Bridge enqueued portal resync: `next_resync_in: "2h28m"` |
| 21:06:40 | Scheduled portal resync executed |
| 21:06:40 | Bridge queried WhatsApp for group members (returned 3 participants) |
| 21:06:41 | Bridge removed archiver: "User is not in remote chat" |

#### Key Log Evidence

```json
// 18:38:40 - Resync scheduled after receiving a message
{"message":"Enqueued resync for portal","jid":"120363421909369050@g.us","next_resync_in":"2h28m0.030613368s"}

// 21:06:41 - Archiver removed during portal resync
{"action":"handle remote event","bridge_evt_type":"RemoteEventChatResync","req_body":{"membership":"leave","displayname":"Message Archiver Bot","reason":"User is not in remote chat"}}
```

### Why This Happens

1. **Portal Resync Feature**: The mautrix-whatsapp bridge periodically syncs Matrix room membership with WhatsApp group membership
2. **Trigger**: Receiving a message in a bridged room schedules a resync ~2.5 hours later
3. **Sync Logic**: During resync, the bridge:
   - Queries WhatsApp for current group participants
   - Compares with Matrix room members
   - Removes any Matrix users not in the WhatsApp group
4. **Archiver Impact**: Since the archiver is a Matrix-only bot (not a WhatsApp participant), it gets removed every time a portal resync runs

### Timing Coincidence

The phone battery dying around 21:06 was **coincidental**. The resync was already scheduled at 18:38 and would have run regardless of phone status.

---

## Separate Issue: Session Invalidation

A separate issue required re-logging into WhatsApp this morning. This was caused by:

1. Server rebooted at 11:36 UTC (Dec 18)
2. Bridge restarted and attempted to reconnect
3. Phone was offline (dead battery)
4. WhatsApp couldn't verify the session without the phone
5. Session was invalidated, requiring new QR code login

**Key difference from official WhatsApp Desktop**: The bridge runs on a remote server and must re-authenticate after restart if the phone is offline. Official clients run locally and maintain session state differently.

---

## Bridge Configuration Changes Made

Updated `/home/matrix-ai/services/whatsapp-bridge/config/config.yaml`:

```yaml
# Auto-reconnect after unknown errors (was: null)
unknown_error_auto_reconnect: 30m
```

This helps the bridge recover from temporary disconnections without manual intervention.

---

## Proposed Solutions

### Option 1: Power Level Protection (Simplest)

**Concept**: Give the archiver bot a higher power level than the whatsappbot in each bridged room. Matrix power levels control who can kick whom.

**Implementation**:
```
In Element: Room Settings → Roles & Permissions → Set @archiver:matrix.radx.dev as Admin (100)
```

**Pros**:
- Simple, no code changes
- Immediate effect

**Cons**:
- Must be configured per-room
- Need to verify bridge respects power levels for kicks
- New rooms require manual setup

---

### Option 2: Auto-Reinvite Script (Recommended)

**Concept**: Create a monitoring service that detects when the archiver is kicked and automatically re-invites it.

**Implementation**:
1. Create a Matrix bot/script that monitors room membership events
2. When archiver's membership changes to "leave" with reason "User is not in remote chat"
3. Automatically send an invite to re-add the archiver
4. Run as a systemd service

**Architecture**:
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Matrix Server  │────▶│  Reinvite Bot    │────▶│  Archiver Bot   │
│  (membership    │     │  (monitors &     │     │  (re-invited)   │
│   events)       │     │   re-invites)    │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**Pros**:
- Works regardless of power levels
- Handles all rooms automatically
- Self-healing system

**Cons**:
- Brief gap where archiver may miss messages (seconds)
- Additional service to maintain
- Requires admin credentials

---

### Option 3: Database-Only Archiver

**Concept**: Modify the archiver to read messages directly from the mautrix-whatsapp PostgreSQL database instead of requiring Matrix room membership.

**Implementation**:
- Query the `mautrix_whatsapp` database directly
- Tables contain all bridged messages with timestamps
- Remove dependency on Matrix room membership

**Pros**:
- Eliminates the problem entirely
- More robust architecture
- No race conditions

**Cons**:
- Requires code changes to archiver
- Loses real-time Matrix event stream
- Couples archiver to bridge database schema

---

## Database Information

The mautrix-whatsapp bridge stores data in PostgreSQL:

**Database**: `mautrix_whatsapp`

**Key Tables**:
- `portal` - Room mappings between WhatsApp groups and Matrix rooms
- `message` - Bridged message history
- `user_login` - WhatsApp session data
- `whatsmeow_device` - Device/session keys

**Portal Persistence**: Room mappings are preserved across re-logins. When re-authenticating with `!wa login`, the bridge remembers existing group-to-room mappings.

---

## WhatsApp Multi-Device Behavior

### Session Invalidation Criteria

1. **14 days phone offline** - Primary phone inactive for 14+ days logs out all linked devices
2. **Manual unlink** - User removes device from phone's "Linked Devices" settings
3. **Unofficial app detection** - WhatsApp may flag unofficial clients (whatsmeow library)
4. **Server restart while phone offline** - Session verification fails without phone
5. **Device limit** - Exceeding 4 linked devices

### Bridge vs Official Clients

| Aspect | Official WhatsApp Desktop | mautrix-whatsapp Bridge |
|--------|---------------------------|-------------------------|
| Client type | Official, signed | Unofficial (whatsmeow) |
| Runs on | Local device | Remote server |
| Session recovery | Local state preserved | Must re-auth with phone |
| WhatsApp treatment | Full tolerance | Subject to stricter rules |

---

## Recommendations

1. **Immediate**: Implement Option 2 (Auto-Reinvite Script) for self-healing behavior
2. **Short-term**: Test Option 1 (Power Levels) as a simpler alternative
3. **Long-term**: Consider Option 3 (Database-Only) for a more robust architecture
4. **Infrastructure**: Keep a dedicated phone always charged and connected for WhatsApp bridging

---

## Related Files

- Bridge config: `/home/matrix-ai/services/whatsapp-bridge/config/config.yaml`
- Bridge logs: `/home/matrix-ai/logs/mautrix-whatsapp.log`
- Bridge database: PostgreSQL `mautrix_whatsapp`
- Systemd service: `/etc/systemd/system/matrix-ai.service`
