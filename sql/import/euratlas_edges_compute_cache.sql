/************************************************************************************************/
/* IMPROT EURATLAS IN CACHE
 *
 * This query generates topological data from the euratlas data, and stores it in a cache table to be inserted afterwards.
 *
 *
 * params:
 *    year (integer) !!!AS IS!!! :   the year to do, !!! AS IS!!! means this won't be escaped
 */
/************************************************************************************************/

/*******************************/
/* TOPOLOGY (geom)  
 * We will use postigs_topology to transform the polygons into borders
 */
/*******************************/

-- START COMMENT OUT TO LOAD FROM CACHE


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


-- Insert the edges in the temp table

CREATE SCHEMA IF NOT EXISTS temp;

DROP TABLE IF EXISTS temp.temp_euratlas_sovereign_states_%(year)s;
CREATE TABLE temp.temp_euratlas_sovereign_states_%(year)s AS
SELECT 		LEAST(COALESCE( r_face.short_name,''),COALESCE( l_face.short_name,''))||' - '||GREATEST(COALESCE( r_face.short_name,''),COALESCE( l_face.short_name,'')) || ' border' as name,
			ST_AsText(ST_Transform(t.geom,4326)) as value

FROM		temp_topology.edge_data as t

LEFT JOIN 	temp_topology.relation as l_rel ON l_rel.element_id = t.left_face
LEFT JOIN 	temp_topology.temp_euratlas_sovereign_states as l_face ON (l_face.topogeom).id = l_rel.topogeo_id

LEFT JOIN 	temp_topology.relation as r_rel ON r_rel.element_id = t.right_face
LEFT JOIN 	temp_topology.temp_euratlas_sovereign_states as r_face ON (r_face.topogeom).id = r_rel.topogeo_id;

