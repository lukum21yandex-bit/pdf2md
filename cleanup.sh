#!/bin/bash
# Cleanup script for LlamaCloud PDF Parser
# Removes files older than 1 day from uploads and output directories

UPLOAD_DIR="/home/user1/.openclaw/workspace/projects/parce/uploads"
OUTPUT_DIR="/home/user1/.openclaw/workspace/projects/parce/output"

# Find and delete files older than 1 day
find "$UPLOAD_DIR" -type f -mtime +1 -delete 2>/dev/null
find "$OUTPUT_DIR" -type f -mtime +1 -delete 2>/dev/null

# Log cleanup
echo "$(date): Cleanup completed" >> /home/user1/.openclaw/workspace/projects/parce/cleanup.log