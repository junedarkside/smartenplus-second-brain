# Feature Flag Kill Switch Pattern

## Problem
Need to disable a frontend feature (e.g., CS chat) instantly without redeployment. Must be togglable from admin dashboard. Must fail-open (feature stays enabled if BE unreachable).

## Pattern

### BE: FeatureFlag model (Django)
```python
class FeatureFlag(models.Model):
    key = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
```

### BE: View with GET=public, PATCH=staff-only
```python
class FeatureFlagView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrIsStaff()]

    def get(self, request, key):
        flag, _ = FeatureFlag.objects.get_or_create(key=key, defaults={'enabled': True})
        data = cache.get(f'flag:{key}')
        if data is None:
            data = {'enabled': flag.enabled}
            cache.set(f'flag:{key}', data, 60)
        return Response(data)

    def patch(self, request, key):
        flag, _ = FeatureFlag.objects.get_or_create(key=key, defaults={'enabled': True})
        flag.enabled = request.data.get('enabled', flag.enabled)
        flag.updated_by = request.user
        flag.save()
        cache.delete(f'flag:{key}')
        return Response({'enabled': flag.enabled})
```

### FE: useFeatureFlag hook (fail-open)
```javascript
import { useState, useEffect } from 'react';
export function useFeatureFlag(key) {
  const [enabled, setEnabled] = useState(true); // fail-open: true until fetch resolves
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/cs/feature-flags/${key}/`)
      .then(r => r.json())
      .then(d => { if (typeof d.enabled === 'boolean') setEnabled(d.enabled); })
      .catch(() => {}); // silent — keep true
  }, [key]);
  return enabled;
}
```

### FE: Component usage
```javascript
export default function MyWidget({ chatEnabled = true }) {
  // If flag disabled while open → show banner (don't unmount mid-conversation)
  if (!chatEnabled && state.status === 'open') {
    return <DisabledBanner />;
  }
  // Flag disabled + not open → hide entirely
  if (!chatEnabled) return null;
  // normal render...
}
```

### Admin: RTK Query endpoints
```javascript
getFeatureFlag: builder.query({ query: (key) => `/api/cs/feature-flags/${key}/`, providesTags: ['FeatureFlag'] }),
updateFeatureFlag: builder.mutation({
  query: ({ key, enabled }) => ({ url: `/api/cs/feature-flags/${key}/`, method: 'PATCH', body: { enabled } }),
  invalidatesTags: ['FeatureFlag'],
}),
```

## Key Rules
- **Fail-open:** `useState(true)` default. Never block feature on fetch error.
- **Cache 60s:** flag TTL = 60s. Changes propagate within 1 minute.
- **Banner before null:** check `!enabled && status==='open'` FIRST, then `if (!enabled) return null`. Prevents dead code.
- **Django admin as Day 1 kill switch** — no custom UI needed until Week 2.
- **Audit trail built-in:** `updated_by` FK + `updated_at` auto field.

## When to use
Any feature that needs instant rollback without redeploy: chat widget, new booking flow, experimental UI, SMS notifications.

## Source
Implemented 2026-06-23 session #155. Files: `cs/models.py`, `cs/views.py`, `hooks/useFeatureFlag.js`, `components/chat/ChatWidget.js`, `admin-dashboard/pages/dashboard/settings/settings.js`.
