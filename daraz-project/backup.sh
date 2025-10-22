
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "💾 Creating backup in $BACKUP_DIR..."

# Backup CSV files
cp *.csv $BACKUP_DIR/ 2>/dev/null
echo "✓ Backed up CSV files"

# Backup plots
cp -r static/plots $BACKUP_DIR/ 2>/dev/null
echo "✓ Backed up plots"

# Backup images
cp -r static/images $BACKUP_DIR/ 2>/dev/null
echo "✓ Backed up images"

# Create manifest
cat > $BACKUP_DIR/manifest.txt <<EOF
Backup created: $(date)
Files backed up:
$(ls -lh $BACKUP_DIR)
EOF

echo "✅ Backup complete: $BACKUP_DIR"
echo "📊 Total size: $(du -sh $BACKUP_DIR | cut -f1)"