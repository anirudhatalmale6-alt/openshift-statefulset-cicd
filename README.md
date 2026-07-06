# GitHub → OpenShift CI/CD Pipeline

Push a StatefulSet manifest to the deploy branch → GitHub Actions runs unit tests,
then logs into your OpenShift cluster and applies the manifest. Fully hands-off.

## How it works

```
push to `deploy` branch
        │
        ▼
┌──────────────┐   tests pass    ┌────────────────────┐
│  Unit Tests  │ ──────────────▶ │  Deploy to OpenShift │
│  (pytest)    │                 │  oc login + oc apply │
└──────────────┘   tests fail    └────────────────────┘
        │                → build goes RED, deploy is skipped
        ▼
  results shown in the
  Actions job summary
```

- **Stage 1 – Unit Tests:** validates the StatefulSet manifest (valid YAML, correct
  kind, matching selector/labels, images present, etc.). Fails fast (`--maxfail=1`)
  and prints results into the Actions summary so you get a green/red badge at a glance.
- **Stage 2 – Deploy:** only runs if tests are green (`needs: test`). Installs and
  **caches** the `oc` CLI, logs in with your token secret, selects your namespace,
  server-side dry-runs the manifest, applies it, and waits for the rollout.

## One-time setup (30 seconds in the GitHub UI)

Go to **Settings → Secrets and variables → Actions**.

**Secrets** (encrypted, never shown in logs):
| Name | Value |
|------|-------|
| `OPENSHIFT_SERVER` | Your API endpoint, e.g. `https://api.your-cluster.com:6443` |
| `OPENSHIFT_TOKEN`  | Your login token (`oc whoami -t` gives you one) |

**Variables** (non-secret):
| Name | Value |
|------|-------|
| `OPENSHIFT_NAMESPACE` | The project/namespace to deploy into |
| `OPENSHIFT_INSECURE_TLS` | `true` only if your cluster uses a self-signed cert (default `false`) |

That's it. No secrets ever live in the repo or the workflow file.

## Usage

1. Edit `manifests/statefulset.yaml` (or drop in your own).
2. Commit and push to the **`deploy`** branch.
3. Open the **Actions** tab — watch it go green and your pods spin up.

To change the trigger branch, edit `branches:` at the top of
`.github/workflows/deploy.yml`.

## Files

```
.github/workflows/deploy.yml   # the pipeline
manifests/statefulset.yaml     # sample StatefulSet (replace with yours)
tests/test_statefulset.py      # unit tests (add your own checks here)
tests/requirements.txt         # pytest + PyYAML
```
