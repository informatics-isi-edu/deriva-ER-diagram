import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';
import { importer } from '@dbml/core';

// Get database name from command line arguments
const dbName = process.argv[2];
if (!dbName) {
  console.error('Usage: node src/index.js <database_name> [schema-names, comma-separated]');
  process.exit(1);
}
// Execute dump_catalog.sh to generate the dump file
console.log(`Dumping database schema for: ${dbName}`);

const schemaNamesArg = process.argv[3];
if (schemaNamesArg) {
  console.log(`Including only specified schemas: ${schemaNamesArg}`);
}

const dumpFile = 'dump.sql';

// generate the dump file
try {
  const schemaNames = schemaNamesArg ? schemaNamesArg.split(',').map(name => name.trim()) : [];
  execSync(`./dump_catalog.sh ${dbName} ${dumpFile} ${schemaNames.join(' ')}`, { stdio: 'inherit' });
  console.log(`Database schema dumped successfully to ${dumpFile}`);
} catch (error) {
  console.error('Error executing dump_catalog.sh:', error.message);
  process.exit(1);
}

// read PostgreSQL file script
const postgreSQL = readFileSync(`./${dumpFile}`, 'utf-8');

// generate the dbml and save to file
const dbml = importer.import(postgreSQL, 'postgres');
console.log('DBML generation completed. Writing to output.dbml...');
writeFileSync('./output.dbml', dbml);