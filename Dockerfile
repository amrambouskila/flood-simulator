FROM python:3.13-slim

# Base-image security patches. The Debian slim bases currently ship a util-linux that Trivy
# flags HIGH (CVE-2026-53612..53615, fixed upstream in 2.41.5). These packages come from the
# base layer, so this is required even though nothing below installs them.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY models.py app.py ./

ENV PORT=5250

EXPOSE 5250

# local-dev container, not a public-facing service,
# so non-root is exempt per global CLAUDE.md section 9. A non-root USER would also break the
# bind-mounted host directories this image reads and writes at runtime. Revisit before any
# deployment beyond localhost.
# nosemgrep: dockerfile.security.missing-user.missing-user
CMD ["streamlit", "run", "app.py", "--server.port=5250", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
