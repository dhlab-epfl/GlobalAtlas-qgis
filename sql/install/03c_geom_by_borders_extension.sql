/************************************************************************************************/
/* INSTALL geom_by_borders_extension
 *
 * This extends the properties to be able to set an entities geometry from other geometries defining it's border.
 */
/************************************************************************************************/

/*************************************************/
/* Create the geom by border table
 *
 * This table links the prop tables to the actual border entities
 */
/*************************************************/

DROP TABLE IF EXISTS vtm.geom_by_borders CASCADE;
CREATE TABLE vtm.geom_by_borders
(
  id serial NOT NULL PRIMARY KEY,
  entity_id integer REFERENCES vtm.entities ON DELETE CASCADE,
  border_id integer REFERENCES vtm.entities ON DELETE CASCADE,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);

-- TRIGGER FOR STAMPS

CREATE TRIGGER geom_by_borders_stamps BEFORE INSERT OR UPDATE ON vtm.geom_by_borders FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();

/*************************************************/
/* Add the triggers                              */
/*************************************************/

-- TODO
