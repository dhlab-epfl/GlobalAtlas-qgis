/************************************************************************************************/
/* SELECT ALL PROPERTIES TYPE BY ENTITY
 *
 * This query returns all property types ids for all entities ids. It's useful for global postprocessing.
 */
/************************************************************************************************/

SELECT DISTINCT entity_id, property_type_id FROM vtm.properties;