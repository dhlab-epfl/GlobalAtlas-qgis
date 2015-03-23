/*******************************/
/* SOURCES                     */
/*******************************/

INSERT INTO vtm.sources(name)
SELECT 'Euratlas'
WHERE NOT EXISTS ( SELECT id FROM vtm.sources WHERE name = 'Euratlas' );



/*******************************/
/* EVENTS (geom)               */
/*******************************/

-- We will use postigs_topology to get the borders from the polygons

-- Create new empty topology structure
SELECT 	topology.DropTopology('temp_topology');
SELECT 	topology.CreateTopology('temp_topology',4326,0);

-- Add the borders to the topology structure - /!\/!\/!\ 98000 ms /!\/!\/!\
SELECT 	topology.ST_CreateTopoGeo('temp_topology',ST_Collect(ST_Transform(geom,4326)))
FROM 	"data_external"."euratlas_sovereign_states"
WHERE 	"year"=2000;

-- select the polygons
/*SELECT 	face_id, topology.ST_GetFaceGeometry('temp_topology', face_id) as geom
FROM 	temp_topology.face
WHERE 	face_id > 0;*/

-- Insert the edges
INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	NULL as entity_id,
		0 as property_type_id,
		ST_Transform(topology.geom,4326) as geovalue,
		2000 as date,
		(SELECT id FROM vtm.sources WHERE name='Euratlas') as source_id
FROM 	(
			SELECT 	edge_id, geom
			FROM 	temp_topology.edge_data
		) as topology;

-- Insert the faces
INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	NULL as entity_id,
		0 as property_type_id,
		ST_Transform(topology.geom,4326) as geovalue,
		2000 as date,
		(SELECT id FROM vtm.sources WHERE name='Euratlas') as source_id
FROM 	(
			SELECT 	face_id, topology.ST_GetFaceGeometry('temp_topology', face_id) as geom
			FROM 	temp_topology.face
			WHERE 	face_id > 0
		) as topology;


-- Clean up
SELECT 	topology.DropTopology('temp_topology');

