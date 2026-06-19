# ContractSerializer — Non-transport Field Gap

## Summary
`BookingSummarySerializer` → `ContractSerializer` had an explicit minimal `fields` list missing all non-transport contract data. Booking detail page received no tour info from API.

## Root Cause
`operators/serializers.py:ContractSerializer` used explicit `fields = [15 fields]`. Missing:
- `general_information` (FK → `GeneralInformation` model, has `description` RichTextField)
- `cancellation_policy` (FK → `policies.CancellationPolicy`)
- `image` (reverse: `imagegallery_set` → `ImageGallery` model)
- Flat fields: `tour_highlights`, `inclusions`, `exclusions`, `what_to_bring`, `difficulty_level`, `duration`, `instant_confirmation`, `mobile_ticket_enabled`, `meeting_point_type`, `meeting_point_details`

## Fix Pattern
Add 3 helper serializer classes **before** `ContractSerializer` (order matters — Python executes class body top-to-bottom):
```python
class _GeneralInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralInformation
        fields = '__all__'

class _CancellationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationPolicy
        fields = ['id', 'free_refund', 'refund_hours', 'charge_type', 'charge_amount']

class _ImageGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageGallery
        fields = ['id', 'image', 'order']
```

Use underscore prefix to avoid name collision with the full serializers defined later in the file.

Add to `ContractSerializer` class body:
```python
general_information = _GeneralInformationSerializer(read_only=True)
cancellation_policy = _CancellationPolicySerializer(read_only=True)
image = _ImageGallerySerializer(source='imagegallery_set', many=True, read_only=True)
```

## Key Facts
- `CancellationPolicy` model fields: `free_refund` (yes/no), `refund_hours` (DurationField), `charge_type`, `charge_amount`. **No `cancellation_window` field** — frontend `ServiceTabbedInfo.js` had this wrong, fixed to `refund_hours`.
- `duration` is `DurationField` → `str(timedelta)` → `"8:00:00"` format. `customFormatDuration()` splits on `:` — works correctly.
- `image` uses reverse accessor `imagegallery_set` via `source=` param.
- `requirements` field does NOT exist on `Contract` model — do not add.
- `GeneralInformation.description` is `RichTextField` (HTML). Frontend accesses `contract?.general_information?.description`.
- `CancellationPolicy` not in `policies.models` import by default — add to line 8 of serializers.py.

## Import fix
```python
# operators/serializers.py line 8 — add CancellationPolicy
from policies.models import CancellationPolicies, CancellationDetail, BaggagePolicy, GeneralInformation, CancellationPolicy
```

## Frontend fix in ServiceTabbedInfo.js
```js
// WRONG — no such field
cancellationPolicy.cancellation_window
// RIGHT
cancellationPolicy.refund_hours
```

## Related
[[checkout-confirmation-payment-crash]]
[[copy-cartitem-trip-none-guard]]
[[contract-trip-null-non-transport-pattern]]
