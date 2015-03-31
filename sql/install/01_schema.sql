/************************************************************************************************/
/* INSTALL schema
 *
 * This drops and creates the whole schema for a clean reset
 */
/************************************************************************************************/

DROP SCHEMA IF EXISTS vtm CASCADE;

CREATE SCHEMA IF NOT EXISTS vtm;

GRANT ALL PRIVILEGES ON SCHEMA vtm TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA vtm GRANT ALL ON TABLES TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA vtm GRANT ALL ON FUNCTIONS TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA vtm GRANT ALL ON SEQUENCES TO public;
