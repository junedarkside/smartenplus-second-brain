# Admin Dashboard CS Centralization Implementation Plan

## Summary
Implementation plan for CS Centralization blocker features in admin dashboard. Backend blockers complete (31/31 tests passing), frontend components ready. Admin dashboard needs integration and UI development.

## Context
CS Centralization blockers implemented in backend + customer-facing frontend (`smartenplus-frontend` `02bf22d`, `smartenplus-backend` `e60c61d`). Admin dashboard (`admin-dashboard`) needs to integrate these features for internal operations team.

## Implementation Plan

### Phase 1: Admin Ticket Detail Enhancement (Priority 1)
**Goal:** Surface blocker fields in ticket detail view for admin visibility

**Components to Create/Modify:**
1. **Enhanced Ticket Status Banner** - Adapt `TicketStatusBanner.js` from customer frontend
   - Add SLA deadline display (ack, operator, ota, resolution)
   - Show resolution stage progress
   - Emergency flag indicator
   - Admin-initiated badge

2. **Blocker Action Buttons** - New component for guard compliance
   - "Contact OTA" button (records `admin_contacted_ota_at` + note)
   - "Sync Now" button (triggers OTA sync)
   - "Emergency" toggle (bypasses normal flow)
   - Time-based warning messages (4h, 12h thresholds)

3. **Resolution Guard Modal** - Prevents accidental resolution
   - Shows blocker checks before allowing resolve
   - Displays OTA contact status
   - Confirms emergency justification if applicable

**Files to Create:**
- `components/tickets/TicketStatusBanner.js` (adapt from frontend)
- `components/tickets/BlockerActions.js` (new)
- `components/tickets/ResolutionGuardModal.js` (new)

**API Integration:**
- GET `/api/v1/tickets/{id}/` - Full ticket with blocker fields
- POST `/api/v1/tickets/{id}/contact-ota/` - Record OTA contact
- POST `/api/v1/tickets/{id}/emergency/` - Toggle emergency flag

### Phase 2: Admin Ticket List Enhancement (Priority 2)
**Goal:** Filter and sort tickets by blocker criteria

**Enhancements Needed:**
1. **Filter Panel** - Add blocker-specific filters
   - Emergency tickets toggle
   - SLA breach filters (ack, operator, ota, resolution)
   - OTA-awaiting tickets
   - Admin-initiated filter

2. **List Columns** - Add blocker indicators
   - Emergency flag column
   - SLA status indicator
   - Resolution stage badge
   - Time-to-resolution display

**Files to Modify:**
- `components/tickets/TicketList.js` (enhance existing)
- `store/tickets.js` (add filter actions)

### Phase 3: Admin OTA Booking Integration (Priority 3)
**Goal:** Admin interface for OTA booking management

**Components to Create:**
1. **OTA Booking Detail View** - Mirror of customer `/my-trip`
   - OTA booking status display
   - OtaBookingEvent timeline
   - TripNotification management

2. **Admin OTA Actions** - Emergency override capabilities
   - Manual booking update
   - Emergency status override
   - Direct OTA contact log

**Files to Create:**
- `pages/bookings/ota-booking-detail.js` (new)
- `components/bookings/OtaBookingTimeline.js` (new)
- `components/cs/OtaBookingAdminPanel.js` (new)

### Phase 4: Admin Help & Documentation (Priority 4)
**Goal:** Inline help content for CS Centralization workflows

**Documentation to Create:**
1. **Admin Guide Panel** - Help tooltip/sidebar
   - Blocker explanation
   - SLA breakdown reference
   - Emergency workflow guide

2. **Training Content** - On-screen guidance
   - Step-by-step blocker resolution
   - OTA contact best practices
   - Emergency escalation flow

## Help Content Structure

### HTML Help Files for CS Centralization

**File:** `public/help/cs-centralization-admin-guide.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS Centralization Admin Guide</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .blocker-section { border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .workflow-step { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }
        .sla-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .sla-table th, .sla-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .sla-table th { background-color: #2196F3; color: white; }
        .emergency { border-left: 4px solid #f44336; background: #ffebee; }
        .success { border-left: 4px solid #4caf50; background: #e8f5e9; }
    </style>
</head>
<body>
    <h1>CS Centralization Admin Guide</h1>
    
    <div class="blocker-section">
        <h2>Understanding the 3 Blockers</h2>
        
        <h3>Blocker 1: Resolve-Block Guard</h3>
        <p><strong>Purpose:</strong> Prevent resolving OTA-awaiting tickets without OTA contact or update</p>
        <p><strong>When it activates:</strong> Ticket in `awaiting_ota_update` status</p>
        <p><strong>Time thresholds:</strong></p>
        <ul>
            <li><strong>&lt; 4 hours since OTA contact:</strong> Too soon to resolve (BLOCK)</li>
            <li><strong>4-12 hours since OTA contact:</strong> Warn, but allow with caution</li>
            <li><strong>&gt; 12 hours since OTA contact:</strong> Auto-allow (OTA non-responsive)</li>
        </ul>
        
        <h3>Blocker 2: SLA Display</h3>
        <p><strong>Purpose:</strong> Show ticket aging and resolution deadlines</p>
        <table class="sla-table">
            <tr>
                <th>Request Type</th>
                <th>Acknowledgment</th>
                <th>Operator Check</th>
                <th>OTA Update</th>
                <th>Total Resolution</th>
            </tr>
            <tr>
                <td>Cancellation</td>
                <td>4 hours</td>
                <td>12 hours</td>
                <td>24 hours</td>
                <td>36 hours total</td>
            </tr>
            <tr>
                <td>Date/Pax Change</td>
                <td>4 hours</td>
                <td>24 hours</td>
                <td>48 hours</td>
                <td>72 hours total</td>
            </tr>
            <tr>
                <td>Other Requests</td>
                <td>4 hours</td>
                <td>-</td>
                <td>-</td>
                <td>24 hours total</td>
            </tr>
        </table>
        
        <h3>Blocker 3: Emergency Path</h3>
        <p><strong>Purpose:</strong> Handle urgent OTA issues (customer stranded, safety concerns)</p>
        <p><strong>Workflow:</strong></p>
        <ol>
            <li>Toggle "Emergency" flag on ticket</li>
            <li>Override normal resolution guard</li>
            <li>Resolve immediately (manual reconciliation later)</li>
            <li>Document emergency justification in resolution note</li>
        </ol>
    </div>
    
    <div class="blocker-section">
        <h2>Admin Workflows</h2>
        
        <div class="workflow-step">
            <h3>Workflow 1: Handling OTA-Awaiting Tickets</h3>
            <ol>
                <li>Check SLA display for deadline status</li>
                <li>If &lt; 12 hours since OTA contact: Use "Contact OTA" button</li>
                <li>If &gt; 12 hours: Resolution guard auto-allows</li>
                <li>If urgent: Toggle "Emergency" and resolve</li>
            </ol>
        </div>
        
        <div class="workflow-step">
            <h3>Workflow 2: Emergency OTA Situations</h3>
            <ol>
                <li>Identify emergency (customer stranded, safety issue)</li>
                <li>Toggle "Emergency" flag on ticket</li>
                <li>Resolve ticket immediately</li>
                <li>Document emergency justification</li>
                <li>Manual reconciliation with OTA later</li>
            </ol>
        </div>
        
        <div class="workflow-step emergency">
            <h3>Workflow 3: SLA Breach Response</h3>
            <ol>
                <li>Red SLA indicator shows breach</li>
                <li>Check which deadline breached (ack/operator/ota/resolution)</li>
                <li>Escalate to supervisor if resolution deadline breached</li>
                <li>Document breach reason in resolution note</li>
            </ol>
        </div>
    </div>
    
    <div class="blocker-section success">
        <h2>Best Practices</h2>
        <ul>
            <li><strong>Always contact OTA first</strong> before resolving awaiting tickets</li>
            <li><strong>Use emergency flag sparingly</strong> - only for true emergencies</li>
            <li><strong>Document everything</strong> - resolution notes are audit trail</li>
            <li><strong>Check SLA displays daily</strong> - prioritize red/overdue tickets</li>
            <li><strong>Sync before resolving</strong> - ensure latest OTA status</li>
        </ul>
    </div>
    
    <div class="blocker-section">
        <h2>FAQ</h2>
        <dl>
            <dt><strong>Q: Can I override the resolve-block guard?</strong></dt>
            <dd>A: Yes, after 12h since OTA contact, or by toggling "Emergency" flag</dd>
            
            <dt><strong>Q: What happens if I accidentally resolve too early?</strong></dt>
            <dd>A: The guard prevents this under 4h. Between 4-12h, you get a warning but can proceed</dd>
            
            <dt><strong>Q: How do I know if a ticket is emergency-eligible?</strong></dt>
            <dd>A: Use judgment: customer stranded, safety concerns, immediate health issues</dd>
            
            <dt><strong>Q: Do emergency tickets skip all validation?</strong></dt>
            <dd>A: Yes, but you must document justification in the resolution note</dd>
        </dl>
    </div>
</body>
</html>
```

## Implementation Priority

**Phase 1 (Week 1):** Admin Ticket Detail Enhancement
- Adapt existing `TicketStatusBanner.js` from customer frontend
- Create blocker action components
- Integrate with existing ticket detail view

**Phase 2 (Week 2):** Admin Ticket List Enhancement  
- Add blocker-specific filters
- Enhance list columns with blocker indicators

**Phase 3 (Week 3):** Admin OTA Booking Integration
- Create OTA booking detail view
- Build admin OTA action panels

**Phase 4 (Week 4):** Admin Help & Documentation
- Deploy HTML help content
- Create in-app help tooltips
- Build training materials

## Related
- [[cs-centralization-blockers-implementation]] - Backend implementation
- [[cs-workflow-revised-2026-06-27]] - Business analysis
- [[admin-dashboard]] - Admin dashboard repo
- [[booking-command-centre-decision]] - Original decision