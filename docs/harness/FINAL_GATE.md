# Final Gate

## Human Acceptance Required

All execution slices require explicit human acceptance before being marked as done.

## Acceptance Criteria

1. All required files for the slice exist
2. No forbidden files were created
3. Quality gates are satisfied
4. Evidence artifacts are documented
5. Rollback notes are provided

## Process

1. Agent completes execution slice
2. Agent returns summary with all required sections
3. Human reviews artifacts and evidence
4. Human approves or rejects
5. Only upon approval is slice marked as done

## Rejection

If rejected, the slice returns to `running` state with rejection reasons documented.
