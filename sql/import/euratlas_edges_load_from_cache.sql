/************************************************************************************************/
/* IMPROT EURATLAS EDGES FROM CACHE
 *
 * This query inserts the euratlas edge data from the cache table into the properties table
 *
 *
 * params:
 *    year (integer) !!!AS IS!!! :   the year to do, !!! AS IS!!! means this won't be escaped
 */
/************************************************************************************************/

-- Insert into the properties from the temp table

SELECT  	vtm.insert_properties_helper(
				name,
				'border'::text,
				'Euratlas'::text,
				'geom'::text,
				%(year)s,
				'start',
				value
			),
			vtm.insert_properties_helper(
				name,
				'border'::text,
				'Euratlas'::text,
				'geom'::text,
				%(year)s+100,
				'start',
				NULL
			)
FROM 		temp.temp_euratlas_sovereign_states_%(year)s;


-- Insert the faces
/*
SELECT 	vtm.insert_properties_helper(
			face.short_name,
			'state'::text,
			'Euratlas',
			'geom'::text,
			%(year)s,
			'start',
			ST_AsText(ST_Transform(topology.ST_GetFaceGeometry('temp_topology', t.face_id),4326))
		),
		vtm.insert_properties_helper(
			face.short_name,
			'state'::text,
			'Euratlas',
			'geom'::text,
			%(year)s+100,
			'start',
			NULL
		)
FROM 	temp_topology.face as t

LEFT JOIN  	temp_topology.relation as rel ON rel.element_id = t.face_id
LEFT JOIN 	temp_topology.temp_euratlas_sovereign_states as face ON (face.topogeom).id = rel.topogeo_id
WHERE 	face_id > 0;
*/


