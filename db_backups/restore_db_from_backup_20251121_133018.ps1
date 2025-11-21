Copy-Item -Path "B:\intership-works\vts_college-main\db_backups\db_backup_20251121_133018.sqlite3" -Destination "B:\intership-works\vts_college-main\db.sqlite3" -Force
Write-Host 'Database restored from B:\intership-works\vts_college-main\db_backups\db_backup_20251121_133018.sqlite3 to B:\intership-works\vts_college-main\db.sqlite3. Restart your Django server if running.'
