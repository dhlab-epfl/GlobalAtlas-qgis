/************************************************************************************************/
/* IMPROT EURATLAS
 *
 * This query imports data from the euratlas table
 *
 *
 * params:
 *    year (integer)  :      the year to do
 */
/************************************************************************************************/

/*******************************/
/* TOPOLOGY (geom)  
 * We will use postigs_topology to transform the polygons into borders
 */
/*******************************/

-- Create new empty topology structure

SELECT 	topology.DropTopology('temp_topology');

SELECT 	topology.CreateTopology('temp_topology',4326,0);


-- Create a copy of the euratlas data

DROP TABLE IF EXISTS temp_topology.temp_euratlas_sovereign_states CASCADE;
CREATE TABLE temp_topology.temp_euratlas_sovereign_states AS
SELECT *
FROM "data_external"."euratlas_sovereign_states"
WHERE "year"=%(year)s;


-- Add and update it's topology column

SELECT AddTopoGeometryColumn('temp_topology', 'temp_topology', 'temp_euratlas_sovereign_states', 'topogeom', 'MULTIPOLYGON');

UPDATE temp_topology.temp_euratlas_sovereign_states SET topogeom = toTopoGeom(ST_Transform(geom,4326), 'temp_topology', 1);


/*******************************/
/* INSERTION
 *
 * Insertion is a bit tricky since I didn't find the documentation of postgis's topology schemas
 */
/*******************************/


-- Insert the edges

SELECT 		vtm.insert_properties_helper(
				LEAST(COALESCE( r_face.short_name,''),COALESCE( l_face.short_name,''))||' - '||GREATEST(COALESCE( r_face.short_name,''),COALESCE( l_face.short_name,'')) || ' border',
				'border'::text,
				'Euratlas',
				'geom'::text,
				%(year)s,
				'start',
				ST_AsText(ST_Transform(t.geom,4326))
			),
			vtm.insert_properties_helper(
				LEAST(COALESCE( r_face.short_name,''),COALESCE( l_face.short_name,''))||' - '||GREATEST(COALESCE( r_face.short_name,''),COALESCE( l_face.short_name,'')) || ' border',
				'border'::text,
				'Euratlas',
				'geom'::text,
				%(year)s+100,
				'start',
				NULL
			)

FROM		temp_topology.edge_data as t

LEFT JOIN 	temp_topology.relation as l_rel ON l_rel.element_id = t.left_face
LEFT JOIN 	temp_topology.temp_euratlas_sovereign_states as l_face ON (l_face.topogeom).id = l_rel.topogeo_id

LEFT JOIN 	temp_topology.relation as r_rel ON r_rel.element_id = t.right_face
LEFT JOIN 	temp_topology.temp_euratlas_sovereign_states as r_face ON (r_face.topogeom).id = r_rel.topogeo_id;


-- Insert the faces

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



