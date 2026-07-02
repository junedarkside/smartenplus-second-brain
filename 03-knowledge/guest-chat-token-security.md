# Guest Chat Token Security — OTP Gate Gaps

## Summary
Guest support chat uses time-limited tokens for authentication. Flow should be: enter email → receive OTP → verify → get token. Vulnerability: if token endpoint hands out tokens for existing conversations without OTP, anyone can read any guest's full chat history.

## Vulnerability Pattern

```python
class ConversationCreateView(APIView):
    def post(self, request):
        email = request.data.get('email')

        # ❌ Finds existing conversation → immediately returns token
        conv = Conversation.objects.filter(
            guest_email=email,
            status__in=[OPEN, PENDING],
        ).first()
        if conv:
            guest_token = make_guest_token(email, conv.id)
            return Response({'guest_token': guest_token})  # Free access!

        # New conv → create...
```

**Attack:** Customer A types Customer B's email → gets B's token → reads B's entire conversation (booking details, personal info, support history). No hacking required.

## Fix

```python
conv = Conversation.objects.filter(
    guest_email=email,
    status__in=[OPEN, PENDING],
).first()
if conv:
    return Response(
        {'error': 'OTP_REQUIRED', 'detail': 'Verify OTP to access existing conversation.'},
        status=status.HTTP_403_FORBIDDEN,
    )
# No existing conv → safe to create new
conv = Conversation.objects.create(guest_email=email, ...)
```

**Authenticated users:** Go through separate path (no token, no OTP). Unaffected.

## Edge Cases

**Closed conversation:**
- Filter is `status__in=[OPEN, PENDING]`
- Closed conv → no match → new conv created → correct (closed = resolved, new issue = new conv)

**New conversation:**
- No existing conv → 403 not needed → create → safe

## When This Matters

- **Phase 1** (chat only, no booking data): Risk low (metadata exposure only)
- **Phase 2** (booking context added): Risk medium
- **Phase 3** (OTA data visible): Risk high → OTP gate critical
- **Phase 4** (full account access): OTP gate mandatory

## Related
- [[guest-auth-flows]] — OTP + token patterns
- [[chat-security-checklist]] — all chat entry points

## Context
SmartEnPlus command-centre gap fix C3 — `ConversationCreateView` now returns 403 `OTP_REQUIRED` for existing guest conversations.
