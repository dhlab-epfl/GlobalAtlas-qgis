/************************************************************************************************/
/* CREATE OR GET PROPERTY TYPE
 *
 * This query creates or gets a property_type_id from a string.
 *
 *
 * params:
 *    property_name  :      the name of the property
 * returns:
 * 	  int : 				the property type id
 */
/************************************************************************************************/

INSERT INTO vtm.properties_types ( name )
SELECT %(property_name)s
WHERE NOT EXISTS ( SELECT * FROM vtm.properties_types WHERE name = %(property_name)s  );

SELECT  id
FROM 	vtm.properties_types
WHERE   name = %(property_name)s;