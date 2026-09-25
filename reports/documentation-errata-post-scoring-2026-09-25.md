# Documentation errata recorded after main-study scoring (2026-09-25)

This document was written on 2026-09-25, after main-study scoring. It is separate from `reports/documentation-errata-2026-09-24.md`, which covers items identified during Roadmap 15 and was written before scoring; that document is not modified. This document does not modify any existing sentence in the `decisions/` documents or in `reports/protocol-freeze-record-2026-09-24.md`. Each item states the location, the current wording, the fact that currently holds, and the basis for that fact.

## Items

1. `reports/protocol-freeze-record-2026-09-24.md:153`
   - Current wording: "3. `decisions/02-3-sampling-design.md`: a Revision note (2026-09-24) records the seed and script name as announced in the 2026-09-23 note. Sampling rule unchanged. New sha256 of 02-3: 74873baa59c0396291d1d15c057289bd47eda41690b0e1d61d092d83f80561a4."
   - Current fact: this entry does not state the commit ID or the new file size of the change to `decisions/02-3-sampling-design.md`. The change was made in commit `6673383fb28476740c5ee1d22aa969b769e5c391`; at that commit the file is 8,096 B and its sha256 equals the value stated in line 153.
   - Basis: `git log --format=%H ed13ec2..187a252 -- decisions/02-3-sampling-design.md` returns only `6673383fb28476740c5ee1d22aa969b769e5c391`; `git cat-file -s 6673383:decisions/02-3-sampling-design.md` returns 8096; `git show 6673383:decisions/02-3-sampling-design.md | shasum -a 256` returns 74873baa59c0396291d1d15c057289bd47eda41690b0e1d61d092d83f80561a4. `ed13ec2` is the commit whose blobs are the source of the tracked-file sizes and sha256 values in the table introduced by `reports/protocol-freeze-record-2026-09-24.md:81` ("Tracked files, size and sha256 of the blob at `ed13ec2`").

2. `decisions/02-3-sampling-design.md:31`
   - Current wording: "These quantities will be reproduced in a repository script using the corresponding hypergeometric calculation (`scripts/[filename].py`)."
   - Current fact: the placeholder `scripts/[filename].py` was not replaced by an actual script file name. No repository script performing this hypergeometric calculation was created.
   - Basis: `git grep -n -i "hypergeom" 187a25245f1ab90acb40e5d569b67ab02d942553` returns one match, `187a25245f1ab90acb40e5d569b67ab02d942553:decisions/02-3-sampling-design.md:31`; `git grep -n -i -E "hypergeom|math\.comb|scipy|binom" 187a25245f1ab90acb40e5d569b67ab02d942553 -- scripts tests` returns no match (exit status 1).
