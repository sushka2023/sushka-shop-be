#!/usr/bin/env bash

alembic upgrade head

cd src

ENTRYPOINT ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
