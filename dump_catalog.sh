#!/bin/bash

# Usage: dump_catalog.sh <dbname> [outfile] [schemas...]
# Dumps the specified PostgreSQL database schema(s) to an SQL file,
# excluding functions/procedures and cross-schema foreign keys that
# may cause parsing issues.

if [ -z "$1" ]; then
    echo "Usage: $0 <dbname> [outfile] [schemas...]"
    echo "Example: $0 mydb output.sql bio vocab"
    echo "Example: $0 mydb output.sql bio"
    exit 1
fi

DBNAME=$1
OUTFILE=${2:-db-dump.sql}

# Get schemas from remaining arguments
shift 2
SCHEMAS=("$@")

# Create a temporary file that ermrest user can write to
TEMP_FILE="/tmp/pg_dump_$$_$(date +%s).sql"

# Build schema arguments for pg_dump only if schemas are provided
SCHEMA_ARGS=""
if [ ${#SCHEMAS[@]} -gt 0 ]; then
    for schema in "${SCHEMAS[@]}"; do
        SCHEMA_ARGS="${SCHEMA_ARGS} --schema='${schema}'"
    done
fi

# Run pg_dump as ermrest user to temporary file
# Use schema-only dump and filter out functions/procedures that cause parsing issues
eval "sudo -u ermrest pg_dump -d \"${DBNAME}\" -s -F p -E UTF-8 \
  --exclude-schema='_ermrest*' \
  --exclude-schema='information_schema' \
  --exclude-schema='pg_catalog' \
  --exclude-schema='pg_toast*' \
  --exclude-schema='pg_temp*' \
  --exclude-schema='public' \
  ${SCHEMA_ARGS} \
  -f \"${TEMP_FILE}\""

# Filter out functions and cross-schema foreign keys
if [ -f "${TEMP_FILE}" ]; then
    # Create filtered version excluding function definitions and cross-schema FKs
    FILTERED_FILE="/tmp/filtered_$$_$(date +%s).sql"
    
    # Apply different filtering based on whether schemas were specified
    if [ ${#SCHEMAS[@]} -gt 0 ]; then
        # Build regex pattern for included schemas
        SCHEMA_PATTERN=""
        for i in "${!SCHEMAS[@]}"; do
            if [ $i -eq 0 ]; then
                SCHEMA_PATTERN="${SCHEMAS[i]}"
            else
                SCHEMA_PATTERN="${SCHEMA_PATTERN}\|${SCHEMAS[i]}"
            fi
        done
        
        # Remove CREATE FUNCTION blocks
        sed '/^CREATE FUNCTION/,/^[[:space:]]*\$[^$]*\$[[:space:]]*;[[:space:]]*$/d; /^CREATE OR REPLACE FUNCTION/,/^[[:space:]]*\$[^$]*\$[[:space:]]*;[[:space:]]*$/d' "${TEMP_FILE}" | \
        # Remove public schema foreign keys (both ALTER TABLE and ADD CONSTRAINT lines)
        sed '/^ALTER TABLE.*$/N; /ADD CONSTRAINT.*REFERENCES public\./d' | \
        # Remove foreign keys to any schema not in our included list (both ALTER TABLE and ADD CONSTRAINT lines)
        sed "/^ALTER TABLE.*$/N; /ADD CONSTRAINT.*REFERENCES \(${SCHEMA_PATTERN}\)\./!{/ADD CONSTRAINT.*REFERENCES /d;}" > "${FILTERED_FILE}"
    else
        # No specific schemas requested, so only remove functions and public schema FKs
        sed '/^CREATE FUNCTION/,/^[[:space:]]*\$[^$]*\$[[:space:]]*;[[:space:]]*$/d; /^CREATE OR REPLACE FUNCTION/,/^[[:space:]]*\$[^$]*\$[[:space:]]*;[[:space:]]*$/d' "${TEMP_FILE}" | \
        # Remove public schema foreign keys (both ALTER TABLE and ADD CONSTRAINT lines)
        sed '/^ALTER TABLE.*$/N; /ADD CONSTRAINT.*REFERENCES public\./d' > "${FILTERED_FILE}"
    fi
    
    # Move the filtered file to the desired location
    sudo mv "${FILTERED_FILE}" "${OUTFILE}"
    sudo chown $(whoami):$(whoami) "${OUTFILE}"
    
    # Clean up
    sudo rm -f "${TEMP_FILE}"
    
    echo "Database dump created: ${OUTFILE}"
    if [ ${#SCHEMAS[@]} -gt 0 ]; then
        echo "Included schemas: ${SCHEMAS[*]}"
    else
        echo "Included schemas: all (no specific schemas specified)"
    fi
else
    echo "Error: pg_dump failed to create output file"
    exit 1
fi