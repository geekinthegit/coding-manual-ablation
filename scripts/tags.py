"""Tag-to-category mapping for the TalkMoves teacher tags.

Name strings follow the 1.2 list of the coding manual (verified against
the manual PDF, 2026-09-10). Tag numbers do not follow the 1.2 listing
order: 4 = Revoicing and 5 = Pressing for Accuracy, verified by checking
sample sentences against the manual definitions (see decisions/02-1-dataset-selection-and-scope.md, 2.1.3).
"Not coded" (tag 0) does not appear in the 1.2 list; the name is assigned
here. Manual-internal wording variants (e.g., "coded as Press for
Reasoning") are left as-is in the manual text and are not part of this
label set.
"""

TAG_TO_CATEGORY = {
    0: "Not coded",
    1: "Keeping Everyone Together",
    2: "Getting Students to Relate",
    3: "Restating",
    4: "Revoicing",
    5: "Pressing for Accuracy",
    6: "Pressing for Reasoning",
}

CATEGORY_TO_TAG = {name: tag for tag, name in TAG_TO_CATEGORY.items()}