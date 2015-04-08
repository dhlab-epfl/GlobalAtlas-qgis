/************************************************************************************************/
/* CLONE COMPUTE CLONED PROPERTIES
 *
 * This query copies the property
 *
 *
 * params:
 *    entity_id  :      the entity to recompute
 */
/************************************************************************************************/

-- Step 1 : remove all properties -- todo : restrict to properties which are computed by this tool

DELETE FROM vtm.properties as p
WHERE 	entity_id=%(entity_id)s
		AND
		p.infered_by = 'clone';

-- Step 2 : generate all properties at each modification

--wip

INSERT INTO vtm.properties(entity_id, property_type_id, infered_by, date, value )
SELECT 	cloned_prop.entity_id,
		cloned_prop.property_type_id,
		'clone', 
		clone.date,
		cloned_prop.value
FROM 	vtm.properties as cloned_prop

JOIN 	(
			SELECT 	clone.date,
					clone.value
			FROM 	vtm.properties as clone
			WHERE 	clone.property_type_id = 4
					AND
					clone.entity_id=%(entity_id)s
		) as clone
		ON cloned_prop.id::text IN (clone.value);