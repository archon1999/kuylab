# Security

Do not post credentials or private learner data in public issues. Use GitHub's
**Report a vulnerability** feature for a private report.

Production configuration lives in `/etc/kuylab/production.env` (root-only), outside
the checkout. Database and media volumes survive releases. Never commit runtime
databases, backups, session exports, SSH keys, or `.env` files.

Pull requests run on GitHub-hosted runners with read-only permissions and no
production secrets. Deployment uses a separate protected `production` environment
and a restricted SSH key which can only deploy the current `main` commit. It cannot
open a shell or forward ports. Third-party Actions are pinned to commit SHAs.

HTTPS is required for public authentication. The HTTP bootstrap virtual host is
a maintenance response until DNS and a valid certificate are configured.
