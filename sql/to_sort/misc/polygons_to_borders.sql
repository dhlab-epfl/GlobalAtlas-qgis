-- SAVE THE SEGMENTS

DROP TABLE IF EXISTS temp.euratlas_line;
CREATE TABLE temp.euratlas_line AS
SELECT 	id,
		year,
		long_name as name_a,
		NULL::text as name_b,
		ST_Boundary(geom) as geom
FROM 	"data_external"."euratlas_sovereign_states"
WHERE 	"year"=2000;

-- SPLIT THE SEGMENTS

-- we use grass' v.split function, is there an equivalent postgis function ?


UPDATE 	temp.euratlas_line as t1
SET 	geom=ST_Split( geom, (	SELECT ST_Union(geom)
								FROM temp.euratlas_line as t2
								WHERE t1.id!=t2.id AND ST_Intersects(t1.geom,t2.geom)
								GROUP BY TRUE ));


-- COPY NAMES

UPDATE 	temp.euratlas_line as t1
SET 	name_b = (SELECT name_a FROM temp.euratlas_line as t2 WHERE ST_Equals(t1.geom,t2.geom) AND t1.id!=t2.id);

-- REMOVE DUPLICATES

DELETE FROM temp.euratlas_line as t1
WHERE (
SELECT id FROM temp.euratlas_line as t2
WHERE ST_Equals(t1.geom,t2.geom) AND t1.id<t2.id
) IS NOT NULL;


-- create new empty topology structure
SELECT 	topology.DropTopology('temp_topology');
SELECT 	topology.CreateTopology('temp_topology',4326,0);

-- add the borders to the topology structure
SELECT 	topology.ST_CreateTopoGeo('temp_topology',ST_Collect(ST_Transform(geom,4326)))
FROM 	"data_external"."euratlas_sovereign_states"
WHERE 	"year"=2000;

-- select the polygons
SELECT 	face_id, topology.ST_GetFaceGeometry('temp_topology', face_id) as geom
FROM 	temp_topology.face
WHERE 	face_id > 0;

-- select the edges
SELECT 	edge_id, topology.ST_GetFaceGeometry('temp_topology', edge_id) as geom
FROM 	temp_topology.edge_data
WHERE 	edge_id > 0;