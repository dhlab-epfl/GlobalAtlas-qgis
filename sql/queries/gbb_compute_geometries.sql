/************************************************************************************************/
/* GEOMETRY_BY_BORDERS COMPUTE GEOMETRIES
 *
 * This query computes the computed_date_start and computed_date_end for
 * all properties of a given type for a given entity and for it's relation.
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
		p.property_type_id=3;

-- Step 2 : generate all properties at each modification

--wip

INSERT INTO vtm.properties(entity_id, property_type_id, date, geovalue)

SELECT 	%(entity_id)s as entity_id,
		3 as property_type_id,
		d.date as date,
		--array_agg(p.id) as test,
		COALESCE( ST_BuildArea(ST_Collect(ST_SnapToGrid(p.geovalue,0.00001))), ST_Centroid(ST_Collect(p.geovalue)) ) as geom
FROM 	( 
			SELECT 	date
			FROM 	vtm.properties as p
			WHERE	p.entity_id::text IN 	(
												SELECT 	gbb.value
												FROM 	vtm.properties as gbb
												WHERE 	gbb.property_type_id=2 AND gbb.entity_id = %(entity_id)s
											)
			GROUP BY p.date

		) as d
JOIN 	(
			SELECT 	prop.id,
					prop.geovalue,
					prop.value,
					prop.computed_date_start,
					prop.computed_date_end
			FROM 	vtm.properties as prop
			WHERE	prop.entity_id::text IN (
												SELECT 	gbb.value
												FROM 	vtm.properties as gbb
												WHERE 	gbb.property_type_id=2 AND gbb.entity_id = %(entity_id)s
											)

		) as p ON (computed_date_start IS NULL OR computed_date_start<=d.date) AND (computed_date_end IS NULL OR computed_date_end>d.date)

GROUP BY d.date;