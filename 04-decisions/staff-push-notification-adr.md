---
name: staff-push-notification-adr
description: ADR — staff mobile push notifications. Chat push = AD frontend only (Supabase realtime, zero BE workload). Ticket push = 1 lightweight BE signal (no Celery). Tag-based dedup kills notification spam. 4-agent + leader deep review.
metadata:
  type: decision
  status: accepted
  date: 2026-07-08
  repos: admin-dashboard, smartenplus-backend
---

# Staff Mobile Push Notifications — ADR

## Summary

Staff get mobile push when: (1) customer sends chat message, (2) new ticket created. Decision avoids BE workload for chat — AD frontend already receives every `cs_messages` INSERT via Supabase realtime; it triggers browser push directly. Only tickets need 1 lightweight BE signal (Django-only, can't reach frontend otherwise). No Celery task added. No new external service.

---

## Key Design Decisions & Reasoning

### Why frontend-only for chat push

BE already at capacity (`prod-capacity-celery-audit`: 1-worker, `sync_pending_charges` is 9-min blocker). Adding Celery push tasks for every customer message competes directly. But AD frontend already receives every `cs_messages` INSERT via `useStaffInboxRealtime.onEvent` — this is free, already wired, zero new infrastructure. Foreground tab → browser `Notification` API. Background/closed tab → service worker `push` event (requires prior subscription).

### Why no push for new CS conversations

No `assigned_to` on `Conversation` model → any new conv would broadcast to all 5 staff simultaneously. Combined with `tag`-based dedup (below), the **first customer message** in a new conv already triggers the chat push. New conv + first message = 1 notification. Adding a separate "new conversation" push = duplicate noise. Drop it.

### Notification spam solved by `tag` field

Web Notification `tag` collapses multiple notifications from same conversation into ONE. Customer sends 10 rapid messages in conv 123 → staff device shows exactly 1 notification (each replaces previous). This is browser-native, costs nothing.

### Ticket push routing

`Ticket.assigned_to` exists. Push only assigned staff if set; broadcast all staff if unassigned. Tickets are low-frequency (not chat volume) — 1 synchronous HTTP call in `post_save` signal is safe, no Celery needed.

---

## Final Architecture

```
CHAT MESSAGES (customer → existing conv)
─────────────────────────────────────────
Supabase cs_messages INSERT
  → useStaffInboxRealtime.onEvent (SideList.js) — already wired
      sender === 'customer'?
        Tab on /cs AND conv visible  → no push (staff sees it live)
        Tab hidden OR not on /cs     → service worker showNotification()
                                       tag: 'cs-conv-{conversation_id}'
                                       (collapses N messages → 1 notification)
  Zero BE involvement. Zero Celery. Zero new workload.

NEW TICKET (change/cancel/pax request)
────────────────────────────────────────
Ticket post_save (created=True)
  assigned_to set   → push to that staff's subscriptions only
  assigned_to null  → push to all StaffPushSubscription
  Direct HTTP via pywebpush in signal (no Celery, low frequency)

NEW CS CONVERSATION
────────────────────
Dropped — first customer message covers it via chat push above.
No duplicate notification.
```

---

## Implementation Plan

### BE — `smartenplus-backend` (minimal — tickets only)

**1. `requirements.txt`**
```
pywebpush>=2.0.0
```

**2. `Smartenplus/settings.py`** — add after `SUPABASE_SERVICE_ROLE_KEY` (line ~601):
```python
# Web Push VAPID — generate: py-vapid --gen
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY')        # no default — fails loud
VAPID_PUBLIC_KEY = config('VAPID_PUBLIC_KEY')           # no default — fails loud
VAPID_CLAIMS_EMAIL = config('VAPID_CLAIMS_EMAIL', default='ops@smartenplus.co.th')
```

**3. `cs/models.py`** — append new model (no change to existing tables):
```python
class StaffPushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['user'])]
```

**4. `cs/push.py`** — new helper (keeps signal thin, reusable):
```python
import json
from django.conf import settings
from pywebpush import webpush, WebPushException
from .models import StaffPushSubscription


def send_push_to_subscriptions(qs, title, body, url, tag):
    """Send Web Push to a queryset of StaffPushSubscription. Deletes stale 404/410."""
    stale = []
    for sub in qs:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                },
                data=json.dumps({'title': title, 'body': body, 'url': url, 'tag': tag}),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': f'mailto:{settings.VAPID_CLAIMS_EMAIL}'},
            )
            sub.last_used_at = __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
            sub.save(update_fields=['last_used_at'])
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                stale.append(sub.id)
    if stale:
        StaffPushSubscription.objects.filter(id__in=stale).delete()
```

**5. `tickets/signals.py`** — add after existing 3 receivers:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket

@receiver(post_save, sender=Ticket)
def notify_staff_new_ticket(sender, instance, created, **kwargs):
    if not created:
        return
    from cs.models import StaffPushSubscription
    from cs.push import send_push_to_subscriptions

    if instance.assigned_to_id:
        qs = StaffPushSubscription.objects.filter(user=instance.assigned_to)
    else:
        qs = StaffPushSubscription.objects.all()

    send_push_to_subscriptions(
        qs=qs,
        title='New customer request',
        body=instance.request_type or 'New ticket',
        url=f'/tickets/{instance.id}',
        tag=f'ticket-{instance.id}',
    )
```

**6. `cs/views.py` + `cs/urls.py`** — subscribe/unsubscribe endpoint:
```python
# cs/views.py
class PushSubscriptionView(APIView):
    permission_classes = [IsAdminOrIsStaff]

    def post(self, request):
        StaffPushSubscription.objects.update_or_create(
            endpoint=request.data['endpoint'],
            defaults={
                'user': request.user,
                'p256dh': request.data['keys']['p256dh'],
                'auth': request.data['keys']['auth'],
            },
        )
        return Response({'status': 'subscribed'})

    def delete(self, request):
        StaffPushSubscription.objects.filter(
            endpoint=request.data.get('endpoint'), user=request.user
        ).delete()
        return Response({'status': 'unsubscribed'})

# cs/urls.py — add:
path('push/subscribe/', PushSubscriptionView.as_view(), name='push-subscribe'),
```

---

### AD — `admin-dashboard`

**7. VAPID key generation** (once):
```bash
npx web-push generate-vapid-keys
# VAPID_PUBLIC_KEY  → AD .env.local as NEXT_PUBLIC_VAPID_PUBLIC_KEY
# VAPID_PRIVATE_KEY → BE .env only
```

**8. `public/manifest.json`** — required for iOS PWA push:
```json
{
  "name": "SmartEnPlus Admin",
  "short_name": "SEP Admin",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1976d2",
  "icons": [{ "src": "/smartenplus.svg", "sizes": "any", "type": "image/svg+xml" }]
}
```

**9. `pages/_document.js`** — add in `<Head>`:
```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#1976d2" />
```

**10. `public/sw.js`** — new service worker:
```javascript
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {};
  event.waitUntil(
    self.registration.showNotification(data.title || 'SmartEnPlus Admin', {
      body: data.body || '',
      icon: '/smartenplus.svg',
      badge: '/favicon.ico',
      tag: data.tag || 'staff-notification',
      data: { url: data.url || '/cs' },
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((list) => {
      const existing = list.find((c) => c.url.includes(self.location.origin));
      if (existing) { existing.focus(); return; }
      return clients.openWindow(event.notification.data.url);
    })
  );
});
```

**11. `hooks/usePushSubscription.js`** — new hook (~45 lines):
```javascript
const BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '').trim();
const VAPID_PUBLIC_KEY = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

// Must be called inside a button onClick — NOT useEffect (iOS Safari hard requirement)
export async function requestPushPermissionAndSubscribe(accessToken) {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return false;
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') return false;

  const reg = await navigator.serviceWorker.ready;
  const existing = await reg.pushManager.getSubscription();
  const subscription = existing || await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
  });

  await fetch(`${BASE_URL}/api/cs/push/subscribe/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(subscription.toJSON()),
  });
  return true;
}
```

**12. `pages/_app.js`** — register SW:
```javascript
useEffect(() => {
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(console.error);
  }
}, []);
```

**13. `pages/cs/index.js`** — permission banner (reuse existing MUI Alert pattern, same slot as chat-disabled warning):
```javascript
import { requestPushPermissionAndSubscribe } from '@/hooks/usePushSubscription';

const [pushDismissed, setPushDismissed] = useState(
  () => typeof window !== 'undefined' && localStorage.getItem('cs_push_asked') === '1'
);

const handleEnablePush = async () => {
  localStorage.setItem('cs_push_asked', '1');
  setPushDismissed(true);
  const ok = await requestPushPermissionAndSubscribe(accessToken); // onClick = user gesture ✓
  showAlert(
    ok ? 'Push notifications enabled' : 'Notifications blocked — enable in browser settings',
    ok ? 'success' : 'warning'
  );
};

// In JSX (above conversation list):
{!pushDismissed && typeof window !== 'undefined' && Notification.permission === 'default' && (
  <Alert
    severity="info"
    action={<Button size="small" onClick={handleEnablePush}>Enable</Button>}
    onClose={() => { localStorage.setItem('cs_push_asked', '1'); setPushDismissed(true); }}
    sx={{ mb: 1 }}
  >
    {/iPhone|iPad/.test(navigator.userAgent)
      ? 'Install to Home Screen first, then tap Enable'
      : 'Get notified of new messages when this tab is in the background'}
  </Alert>
)}
```

**14. `pages/dashboard/SideList.js`** — chat push trigger (additive, inside existing `onEvent`):
```javascript
// Add inside onEvent callback after RTK cache patch (line ~113):
if (payload?.new?.sender === 'customer') {
  const isOnCsPage = window.location.pathname.startsWith('/cs');
  const isHidden = document.visibilityState === 'hidden';

  // OS push: tab backgrounded OR staff on a different page
  if (isHidden || !isOnCsPage) {
    if (Notification.permission === 'granted') {
      navigator.serviceWorker.ready.then((reg) => {
        reg.showNotification('New CS message', {
          body: payload.new.body?.slice(0, 80) || '',
          icon: '/smartenplus.svg',
          tag: `cs-conv-${payload.new.conversation_id}`, // collapses rapid messages → 1 notif
          data: { url: `/cs?conversation_id=${payload.new.conversation_id}` },
        });
      });
    } else if (!isOnCsPage) {
      showAlert('New CS message', 'info'); // fallback toast when push not granted
    }
  }

  // Toast only: tab active, staff on /cs but viewing a DIFFERENT conversation
  if (!isHidden && isOnCsPage) {
    const currentConvId = new URLSearchParams(window.location.search).get('conversation_id');
    if (String(payload.new.conversation_id) !== String(currentConvId)) {
      showAlert('New message in another conversation', 'info');
    }
    // Same conv as currently open → staff already sees it live, no notification
  }
}
```

---

## What NOT to Touch

- `useStaffInboxRealtime.js` — no structural change (onEvent callback extended in caller only)
- `useStaffChatRealtime.js` — untouched
- `ConversationDetail.js` — untouched
- All existing CS/ticket API endpoints — untouched
- `Conversation`, `Message` Django models — no field changes
- `Ticket` model — no field changes
- No new Celery task — `notify_staff_new_ticket` signal calls `send_push_to_subscriptions` directly (tickets are low-frequency; synchronous push call is safe)

---

## Notification Behavior Matrix

| Situation | What staff sees |
|---|---|
| Staff on `/cs`, viewing that exact conv | Nothing — sees it live in chat panel |
| Staff on `/cs`, viewing different conv | Toast only ("New message in another conversation") |
| Staff on different page, tab active | Toast + OS push |
| Tab backgrounded / screen locked | OS push |
| Tab closed, SW registered | OS push via service worker |
| Tab closed, push not registered | Nothing (badge on next open) |
| 10 rapid messages from same customer | 1 notification (tag collapses all) |
| New ticket, assigned to staff A | Only staff A gets push |
| New ticket, unassigned | All staff get push |

---

## iOS Safari Note

iOS 16.4+ requires PWA install (Add to Home Screen) before Web Push works. `manifest.json` (step 8) is required. `requestPermission()` must be in `onClick` not `useEffect` — iOS rejects non-gesture calls. Banner detects iOS and shows install instruction instead of standard copy.

---

## `.env` Changes

| Repo | Variable | Note |
|---|---|---|
| BE `.env` | `VAPID_PRIVATE_KEY` | `py-vapid --gen` or `npx web-push generate-vapid-keys` |
| BE `.env` | `VAPID_PUBLIC_KEY` | Same generation |
| BE `.env` | `VAPID_CLAIMS_EMAIL` | Default: ops@smartenplus.co.th |
| AD `.env.local` | `NEXT_PUBLIC_VAPID_PUBLIC_KEY` | Public key only — safe to expose in bundle |

---

## Verification

1. `POST /api/cs/push/subscribe/` with Bearer → `{"status":"subscribed"}`
2. Create `Ticket` (unassigned) → all staff devices get push "New customer request"
3. Create `Ticket` (assigned_to=staffA) → only staffA device gets push
4. Open AD in Chrome → `/cs` → click "Enable" → browser permission prompt
5. Background AD tab → send customer message via FE → 1 push notification on device
6. Send 5 rapid messages → still only 1 notification (tag collapses)
7. Click notification → opens `/cs?conversation_id=[id]`
8. iOS: Add to Home Screen → enable → repeat step 5
9. Revoke push (browser settings) → stale 410 → auto-deleted from `StaffPushSubscription`

---

## Implementation Status — 2026-07-09

SHIPPED locally. All infrastructure verified working end-to-end:
- VAPID keys set in BE `.env` + AD `.env.local`
- `StaffPushSubscription` migration `0013` applied
- `pywebpush` installed
- SW `activated`, PushSubscription stored in DB, chat push fires on tab hide

**Bug fixed during testing:** `renotify: true` added to `showNotification()` in both `SideList.js` (chat push) and `public/sw.js` (ticket push). Without it, tag-collapsed notification replacement shows no banner. Commit `63ef3f4` → `fix/push-renotify` → merged to develop 2026-07-09. See [[web-push-renotify-tag-collapse-bug]].

**Prod setup still needed:**
- AD Vercel env: add `NEXT_PUBLIC_VAPID_PUBLIC_KEY`
- BE VPS `.env`: add `VAPID_PRIVATE_KEY`, `VAPID_PUBLIC_KEY`, `VAPID_CLAIMS_EMAIL`
- Run `python manage.py migrate cs 0013` on VPS
- Restart BE

---

## Related

- [[cs-chat-supabase-offload]] — Supabase is chat write path; push for chat fires from AD not Django
- [[supabase-config-single-source-of-truth]] — VAPID keys follow same BE `.env` canonical pattern
- [[feature-flag-kill-switch-pattern]] — wrap `send_push_to_subscriptions` in `FeatureFlag.get('staff_push')` for kill switch
- [[prod-capacity-celery-audit]] — no new Celery task added by design; ticket push is synchronous in signal
- [[cs-architecture-decision]] — Django owns ticket lifecycle; signal fires on Django-side creates only
- [[web-push-renotify-tag-collapse-bug]] — renotify fix found during local test
- [[macos-notification-testing-gotchas]] — Focus/DND + pileup + visibility gotchas discovered during test
