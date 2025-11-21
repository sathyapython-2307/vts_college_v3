# Exam Violation Handling Implementation

## Overview
This implementation adds comprehensive violation detection and handling to the exam system. When a user violates exam rules (e.g., tab switching, right-click, dev tools), the system:
1. **Displays a violation notification** on the results page
2. **Prevents answer cheating** by showing answers from the last valid attempt instead
3. **Redirects automatically** to the score details page

## Changes Made

### 1. Backend Logic (`core/exam_views.py`)

#### Updated `exam_results()` View
**Location:** Lines 381-430

**Key Features:**
- Detects if current attempt has violations (`has_violations` and `violations.exists()`)
- **Implements violation-aware answer display:**
  - If current attempt has violations → displays answers from the last valid (non-violated) previous attempt
  - If no previous valid attempt exists → no answers are shown
  - Otherwise → displays current attempt's answers normally
  
**Logic Flow:**
```python
if has_violations:
    # Find last valid (non-violated) submitted attempt BEFORE current attempt
    last_valid = ExamAttempt.objects.filter(
        course_access=attempt.course_access,
        is_submitted=True,
        has_violations=False,
        attempt_number__lt=attempt.attempt_number  # Must be older than current
    ).order_by('-attempt_number').first()
    
    if last_valid:
        display_attempt = last_valid  # Show answers from this attempt
```

**Context Variables Passed to Template:**
- `attempt` - The current attempt (with violations)
- `display_attempt` - The attempt whose answers to display
- `has_violations` - Boolean flag for violation presence
- `violations` - QuerySet of all violations for this attempt
- `showing_previous_attempt` - Boolean indicating if previous attempt's answers are shown

### 2. Frontend Template (`templates/exam_results.html`)

#### Violation Alert Section (New)
**Styling:** `.violation-alert` class with yellow warning appearance
- **Header:** "⚠️ Exam Violation Detected"
- **Details:** Lists each violation type with occurrence count
- **Animation:** Slides down smoothly on page load

**Violation Types Displayed:**
- Right-Click Attempted
- Copy/Paste Attempted
- Developer Tools Opened
- Tab/Window Switch
- Back Button Navigation
- Fullscreen Exited
- Other Violation

#### Previous Attempt Info Banner (New)
**Styling:** `.previous-attempt-info` class with blue info appearance
- Displays only when `showing_previous_attempt` is True
- Shows attempt number of both current and displayed attempt
- Clearly states why previous answers are shown

#### Detailed Answers Section (Updated)
- Shows "From Attempt #X" subtitle when displaying previous attempt's answers
- Maintains all original answer details, explanations, and status badges

## User Experience Flow

### Scenario: User has exam violation

1. **During Exam:** User triggers violation (e.g., switches tab)
   - `exam_record_violation()` API records the violation
   - `attempt.has_violations = True` is set

2. **On Submission:** Exam is auto-submitted or manually submitted
   - Violation flag persists

3. **Results Page Redirect:** Automatic redirect to results
   - System detects violation
   - Finds last valid attempt (if exists)
   - Displays current attempt's score
   - Shows answers from valid attempt instead
   - Yellow warning banner shows violation details

### Example Display
```
┌─────────────────────────────────────────┐
│ ⚠️ Exam Violation Detected              │
│ • Tab/Window Switch (Occurred 2 times)  │
│ • Developer Tools Opened (Occurred 1)   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 📋 Note: Due to security violations     │
│ in this attempt (Attempt #2), you are   │
│ viewing answers from your last valid    │
│ attempt (Attempt #1).                   │
└─────────────────────────────────────────┘

[Score Results - shows current attempt score]

[Detailed Answers - from previous valid attempt]
```

## Database Model Considerations

The implementation relies on existing model fields:
- `ExamAttempt.has_violations` - Boolean flag
- `ExamAttempt.violation_count` - Count of violations
- `ExamViolation` - Related records with violation types
- `ExamAnswer` - Answers for each attempt (fetched from `display_attempt`)

## Security Benefits

1. **Prevents Answer Cheating:** Users cannot abuse violations to see answers
2. **Transparent Handling:** Clear notifications inform users of violations
3. **Fair Assessment:** Score reflects attempt with violations, but learning material from valid attempt
4. **Audit Trail:** All violations are recorded in `ExamViolation` model

## Edge Cases Handled

1. **First attempt with violation, no previous attempt:**
   - No answers displayed
   - Violation warning shown
   - Score displayed

2. **Multiple violations in one attempt:**
   - All violations listed in alert
   - Each shows occurrence count

3. **Violation in previous attempt too:**
   - Skips violated attempts
   - Fetches oldest non-violated attempt
   - Uses `has_violations=False` filter

## Testing Recommendations

1. Create exam attempt with violations
2. Verify violation alert displays with correct types
3. Submit exam with violation
4. Check that answers show from previous valid attempt
5. Check that score displayed is from current (violated) attempt
6. Test with multiple violation types
7. Test when no previous valid attempt exists

## Files Modified

1. `core/exam_views.py` - Updated `exam_results()` function
2. `templates/exam_results.html` - Added violation alerts, updated styling

## No Breaking Changes

- All existing exam functionality remains unchanged
- Previous attempts without violations work exactly as before
- Certificate generation unchanged
- Score calculation unchanged
- Only violation-flagged attempts show new behavior
