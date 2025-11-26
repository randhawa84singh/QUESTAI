# QuestAI Apache + PHP Minimal Web Test on Raspberry Pi 5 (≈3 GB RAM)

This guide walks through running a minimal QuestAI web test stack on a Raspberry Pi 5 with roughly 3 GB of available RAM, using Apache2, PHP 8.2+, and SQLite. It focuses on memory-efficient settings while preserving basic observability and safety.

## Prerequisites
- Raspberry Pi OS (64-bit) with ~3 GB RAM available after boot.
- Packages: `apache2`, `php8.2` (or newer), `libapache2-mod-php8.2`, `php8.2-sqlite3`, `php8.2-opcache`, `sqlite3`, `unzip`.
- Optional helper tools: `curl`, `jq` for simple health checks.

### PHP extensions
- `pdo_sqlite` (from `php8.2-sqlite3`) for database access without external daemons.
- `fileinfo` for static asset MIME detection (commonly bundled by default).
- `opcache` for bytecode caching to reduce CPU overhead.

## PHP configuration (OPcache + memory-friendly settings)
Edit `/etc/php/8.2/apache2/php.ini` (or the versioned path matching your PHP). Key directives:
- Enable OPcache module: ensure `zend_extension=opcache` is present (usually in `/etc/php/8.2/apache2/conf.d/10-opcache.ini`).
- Recommended OPcache values for 3 GB RAM budget:
  - `opcache.enable=1`
  - `opcache.enable_cli=0`
  - `opcache.memory_consumption=64` (MB)
  - `opcache.interned_strings_buffer=8` (MB)
  - `opcache.max_accelerated_files=4000`
  - `opcache.revalidate_freq=60`
  - `opcache.validate_timestamps=1`
  - `opcache.fast_shutdown=1`
- Other memory guards:
  - `memory_limit=256M` (adjust upward only if needed for specific scripts).
  - `post_max_size=16M`, `upload_max_filesize=16M` to avoid large request buffers.

Restart Apache after changes: `sudo systemctl restart apache2`.

## Virtual host setup
Example vhost at `/etc/apache2/sites-available/questai.conf`:

```
<VirtualHost *:80>
    ServerName questai.local
    DocumentRoot /var/www/questai/public

    <Directory /var/www/questai/public>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/questai_error.log
    CustomLog ${APACHE_LOG_DIR}/questai_access.log combined
</VirtualHost>
```

Steps:
1. Create directories: `sudo mkdir -p /var/www/questai/public` and `sudo mkdir -p /var/www/questai/storage` (for SQLite and logs if desired).
2. Enable site: `sudo a2ensite questai.conf` and disable default if desired: `sudo a2dissite 000-default.conf`.
3. Enable modules: `sudo a2enmod rewrite headers expires`.
4. Reload Apache: `sudo systemctl reload apache2`.

### File permissions
- Own the app files with the deploy user; grant Apache read/execute: `sudo chown -R <user>:www-data /var/www/questai && sudo find /var/www/questai -type d -exec chmod 755 {} \; && sudo find /var/www/questai -type f -exec chmod 644 {} \;`.
- SQLite database directory should be writable by Apache: `sudo chgrp www-data /var/www/questai/storage && sudo chmod 775 /var/www/questai/storage`.

### Sample `.htaccess` (if not using per-directory config)
Place in `/var/www/questai/public/.htaccess`:
```
RewriteEngine On
# Serve existing files directly
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]

# Front controller for PHP entrypoint
RewriteRule ^ index.php [L]

# Basic caching for static assets
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 7 days"
    ExpiresByType application/javascript "access plus 7 days"
    ExpiresByType image/png "access plus 30 days"
    ExpiresByType image/jpeg "access plus 30 days"
</IfModule>
```

## Deploying the minimal QuestAI web test
1. Copy static assets (CSS/JS/images) from your build into `/var/www/questai/public/assets`.
2. Place the PHP entrypoint (e.g., `index.php`) in `/var/www/questai/public/` and ensure it routes requests to the web test UI.
3. Store configuration for SQLite in a small PHP config file, pointing to `/var/www/questai/storage/questai.sqlite`.
4. Initialize SQLite database if needed: `sqlite3 /var/www/questai/storage/questai.sqlite < schema.sql`.

### Using SQLite to conserve memory
- Prefer `sqlite:` DSN (e.g., `sqlite:/var/www/questai/storage/questai.sqlite`) to avoid running MySQL/Postgres services that consume extra RAM.
- Keep schema lean; index only necessary columns to reduce cache size.
- Periodically vacuum to reclaim space: `sqlite3 /var/www/questai/storage/questai.sqlite "VACUUM;"` (schedule sparingly).

## Caching limits and log rotation
- Keep Apache logs small: add to `/etc/logrotate.d/apache2` (or a custom file):
  - Rotate weekly or when >10M; keep 4 rotations: `size 10M`, `rotate 4`, `compress`, `delaycompress`, `missingok`.
- Avoid large PHP session storage; set `session.gc_maxlifetime` to a modest value (e.g., 3600 seconds) and store sessions in files (default) on the SD card or SSD.
- Avoid large asset caches; rely on browser caching via `Expires` headers and keep server-side caches minimal.

## Quickstart checklist
- Enable site: `sudo a2ensite questai.conf && sudo systemctl reload apache2`.
- Start/stop Apache: `sudo systemctl start|stop|restart apache2`.
- Check service status: `systemctl status apache2`.
- Validate PHP module load: `php -v` and `php -m | grep -E "sqlite|pdo_sqlite|opcache"`.
- Confirm OPcache settings: `php -i | grep opcache` (ensure values match tuning above).
- Permissions sanity: ensure `/var/www/questai/storage` is writable by `www-data`.
- Health check:
  - Local: `curl -I http://localhost/` should return `200`.
  - Application: `curl -I http://localhost/health` (if your entrypoint exposes a health route) should return `200`.
- Log review (keep short sessions): `sudo tail -n 200 /var/log/apache2/questai_error.log`.

With these steps, a Raspberry Pi 5 can run a lean QuestAI web test on Apache and PHP while keeping RAM usage within a ~3 GB envelope.
