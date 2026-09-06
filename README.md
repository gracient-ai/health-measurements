# <type-name>

<The one question this repository answers, in the product's own words.>

## What is in here

| File | What it is |
|---|---|
| `<main-file>.yaml` | What the product runs on. Human and machine readable |
| `<main-file>.md` | The same content, rendered for a doctor to read |
| `sources/` | The documents it was read from |

## What approving means

An approval binds to a commit and means **every line at that commit is approved**. There is
no partial approval and no per-band sign-off. Approving a pull request here says: I have read
the whole of the rendered file, not only the lines that changed.

Pushing a new commit voids an approval already given, because an approval that survived a
change would cover a line it never saw.

## How a change reaches a patient

1. Somebody opens a pull request, by hand or from an extractor. Both are commits.
2. The checks run. They have to pass before it can merge.
3. A doctor reads `<main-file>.md` in the diff and approves.
4. Merging to `main` means reviewed. **It does not reach a patient.**
5. Somebody cuts a tag — `v3` — when it should go live. The tag deploys to the `patients`
   environment, which calls the console, which moves the live pointer and records who
   switched it.

## Settings this repository needs

Three of them carry rules nobody should have to enforce by hand:

- **Require a pull request before merging**, with **1 approval**, and **dismiss stale
  approvals when new commits are pushed**.
- **Require status checks to pass**: the `checks` workflow.
- **Require approval from someone other than the person who pushed.**

Doctors get **Write**, because GitHub only counts an approval from somebody with write
permission. Protected `main` is what stops write becoming a direct push.

## What the release workflow needs

Set on the repository, under Settings → Secrets and variables → Actions:

| | Name | What it is |
|---|---|---|
| Variable | `CONSOLE_BASE_URL` | Where the console answers |
| Variable | `KNOWLEDGE_TYPE` | The type name in the console's registry |
| Secret | `SWITCH_SECRET` | The console's `HC_SWITCH_SECRET` |

The secret goes on the `patients` environment rather than the repository, so a workflow on a
branch cannot read it.
