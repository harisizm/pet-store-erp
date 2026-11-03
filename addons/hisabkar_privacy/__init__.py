from . import controllers
from . import egress
from . import models

# The guard goes up as soon as this package is imported: at server start when the module is in
# server_wide_modules (setup-dev.ps1 writes that), otherwise when a registry that has the module
# installed loads. Either way it precedes any cron or request in that process.
egress.install()
