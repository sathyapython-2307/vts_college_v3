# ESC Key Violation Handling Fix

## Problem
When a user pressed the ESC key during an exam, nothing happened:
- No violation notification was shown
- The results page did not redirect
- The exam continued without any security response

## Root Cause
The ESC key was **not included in the blocked keyboard shortcuts list** in the anti-cheat detection system.

## Solution
Added ESC key (`e.key === 'Escape'`) to the blocked keys list in the keyboard event handler.

### Changes Made

**File:** `templates/exam_portal.html`  
**Location:** Anti-cheat keyboard handler (line ~664)

**What was added:**
1. **ESC key to blocked combos array:**
   ```javascript
   e.key === 'Escape',  // Added this line
   ```

2. **Specific violation handling for ESC:**
   ```javascript
   // Specific message for ESC key
   if (e.key === 'Escape') {
       message = 'Exiting fullscreen using ESC key is not allowed during the exam.';
       violationType = 'exit_fullscreen';
   }
   ```

3. **Dynamic violation recording:**
   - ESC key violations are recorded as `exit_fullscreen` type
   - Other blocked key violations remain as `dev_tools` type
   - Both trigger exam auto-submission

## Behavior After Fix

### When user presses ESC during exam:

1. **Immediate Action:**
   - Event is prevented (`e.preventDefault()`)
   - Exam does NOT exit fullscreen

2. **Server Recording:**
   - Violation is recorded as `exit_fullscreen` type
   - Auto-submit flag is set to `true`

3. **User Notification:**
   - Yellow violation alert modal appears
   - Message: "Exiting fullscreen using ESC key is not allowed during the exam. This violation has been recorded. Your exam will now be submitted."

4. **Automatic Redirection:**
   - Exam is auto-submitted
   - User is redirected to exam results page
   - Results page shows:
     - ⚠️ Violation warning with ESC key details
     - Blue info banner explaining answers from last valid attempt
     - Score from the attempted (violated) exam
     - Answers from previous valid attempt (if exists)

## ESC Key Violation Detection
- Detected in real-time during exam
- Recorded in `ExamViolation` model with type `exit_fullscreen`
- Visible in Django admin and on results page
- Prevents users from easily escaping fullscreen to access resources

## Blocked Keys/Combinations Complete List
Now includes:
- F12 (Developer Tools)
- F5 (Refresh)
- **Escape (ESC) - NEW**
- Ctrl+R or Cmd+R (Refresh)
- Ctrl+Shift+I or Cmd+Shift+I (Inspector)
- Ctrl+Shift+K or Cmd+Shift+K (Console)
- Ctrl+Shift+C or Cmd+Shift+C (Selector)
- Ctrl+C or Cmd+C (Copy)
- Ctrl+X or Cmd+X (Cut)
- Alt+F4 (Close Window)
- Ctrl+Q (Quit)

## Testing
To verify the fix:
1. Start an exam
2. Enter fullscreen mode
3. Press ESC key
4. Expected: Violation alert appears and exam auto-submits
5. Expected: Results page shows ESC key violation with answers from previous attempt

## Impact
- **No breaking changes:** All other exam functionality remains unchanged
- **Security improvement:** Prevents users from exiting fullscreen using ESC
- **Fair assessment:** Users cannot bypass fullscreen constraints using ESC
