/************************************************************************************************/
/* ENTITIES INSERT BLANK
 *
 * This query creates a blank entity and returns it's id
 */
/************************************************************************************************/

INSERT INTO vtm.entities DEFAULT VALUES RETURNING id;