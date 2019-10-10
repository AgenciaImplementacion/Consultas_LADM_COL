WITH
 unidad_area_terreno AS (
	 SELECT ' [' || setting || ']' FROM operacion.t_ili2db_column_prop WHERE tablename = 'op_terreno' AND columnname = 'area_terreno' LIMIT 1
 ),
 terrenos_seleccionados AS (
	SELECT 764 AS ue_op_terreno WHERE '764' <> 'NULL'
		UNION
	SELECT uebaunit.ue_op_terreno FROM operacion.op_predio LEFT JOIN operacion.uebaunit ON op_predio.t_id = uebaunit.baunit  WHERE uebaunit.ue_op_terreno IS NOT NULL AND CASE WHEN 'NULL' = 'NULL' THEN  1 = 2 ELSE (op_predio.codigo_orip || '-'|| op_predio.matricula_inmobiliaria) = 'NULL' END
		UNION
	SELECT uebaunit.ue_op_terreno FROM operacion.op_predio LEFT JOIN operacion.uebaunit ON op_predio.t_id = uebaunit.baunit  WHERE uebaunit.ue_op_terreno IS NOT NULL AND CASE WHEN 'NULL' = 'NULL' THEN  1 = 2 ELSE op_predio.numero_predial = 'NULL' END
		UNION
	SELECT uebaunit.ue_op_terreno FROM operacion.op_predio LEFT JOIN operacion.uebaunit ON op_predio.t_id = uebaunit.baunit  WHERE uebaunit.ue_op_terreno IS NOT NULL AND CASE WHEN 'NULL' = 'NULL' THEN  1 = 2 ELSE op_predio.numero_predial_anterior = 'NULL' END
 ),
 predios_seleccionados AS (
	SELECT uebaunit.baunit as t_id FROM operacion.uebaunit WHERE uebaunit.ue_op_terreno = 764 AND '764' <> 'NULL'
		UNION
	SELECT t_id FROM operacion.op_predio WHERE CASE WHEN 'NULL' = 'NULL' THEN  1 = 2 ELSE (op_predio.codigo_orip || '-'|| op_predio.matricula_inmobiliaria) = 'NULL' END
		UNION
	SELECT t_id FROM operacion.op_predio WHERE CASE WHEN 'NULL' = 'NULL' THEN  1 = 2 ELSE op_predio.numero_predial = 'NULL' END
		UNION
	SELECT t_id FROM operacion.op_predio WHERE CASE WHEN 'NULL' = 'NULL' THEN  1 = 2 ELSE op_predio.numero_predial_anterior = 'NULL' END
 ),
 predio_formulario_unico AS (
	 SELECT fcm_formulario_unico_cm.t_id FROM operacion.fcm_formulario_unico_cm WHERE fcm_formulario_unico_cm.op_predio IN (SELECT * FROM predios_seleccionados)
 ),
 fcm_contacto_visita AS (
	SELECT fcm_contacto_visita.formulario,
		json_agg(
				json_build_object('id', fcm_contacto_visita.t_id,
									   'attributes', json_build_object('Nombre de quien atendió', fcm_contacto_visita.nombre_quien_atendio,
																	   'Relación con el predio', fcm_contacto_visita.relacion_con_predio,
																	   'Domicilio de notificación', fcm_contacto_visita.domicilio_notificaciones,
																	   'Celular', fcm_contacto_visita.celular,
																	   'Correo electrónico', fcm_contacto_visita.correo_electronico,
																	   'Autoriza notificaciones', fcm_contacto_visita.autoriza_notificaciones))
		ORDER BY fcm_contacto_visita.t_id) FILTER(WHERE fcm_contacto_visita.t_id IS NOT NULL) AS fcm_contacto_visita
	FROM operacion.fcm_contacto_visita WHERE fcm_contacto_visita.formulario IN (SELECT * FROM predio_formulario_unico)
	GROUP BY fcm_contacto_visita.formulario
 ),
 info_predio AS (
	 SELECT uebaunit.ue_op_terreno,
			json_agg(json_build_object('id', op_predio.t_id,
							  'attributes', json_build_object('Nombre', op_predio.nombre
															  , 'Departamento', op_predio.departamento
															  , 'Municipio', op_predio.municipio
															  , 'NUPRE', op_predio.nupre
															  , 'FMI', (op_predio.codigo_orip || '-'|| op_predio.matricula_inmobiliaria)
															  , 'Número predial', op_predio.numero_predial
															  , 'Número predial anterior', op_predio.numero_predial_anterior
															  , 'Tipo', op_predio.tipo
															  , 'Corregimiento', fcm_formulario_unico_cm.corregimiento
															  , 'Localidad/Comuna', fcm_formulario_unico_cm.localidad_comuna
															  , 'Barrio/Vereda', fcm_formulario_unico_cm.barrio_vereda
															  , 'Formalidad', fcm_formulario_unico_cm.formalidad
															  , 'Destinación económica', fcm_formulario_unico_cm.destinacion_economica
															  , 'Clase suelo', fcm_formulario_unico_cm.clase_suelo
															  , 'Categoría suelo', fcm_formulario_unico_cm.categoria_suelo
															  , 'Tiene FMI', fcm_formulario_unico_cm.tiene_fmi
															  , 'Fecha de inicio de tenencia', fcm_formulario_unico_cm.fecha_inicio_tenencia
															  , 'Número predial del predio matriz', fcm_formulario_unico_cm.numero_predial_predio_matriz
															  , 'Observaciones', fcm_formulario_unico_cm.observaciones
															  , 'Fecha de visita predial', fcm_formulario_unico_cm.fecha_visita_predial
															  , 'Nombre del reconocedor', fcm_formulario_unico_cm.nombre_reconocedor
															  , 'Contacto de visita', COALESCE(fcm_contacto_visita.fcm_contacto_visita, '[]')
															 )) ORDER BY op_predio.t_id) FILTER(WHERE op_predio.t_id IS NOT NULL) as op_predio
	 FROM operacion.op_predio LEFT JOIN operacion.uebaunit ON uebaunit.baunit = op_predio.t_id
	 LEFT JOIN operacion.fcm_formulario_unico_cm ON op_predio.t_id = fcm_formulario_unico_cm.op_predio
	 LEFT JOIN fcm_contacto_visita ON fcm_contacto_visita.formulario = fcm_formulario_unico_cm.t_id
	 WHERE op_predio.t_id IN (SELECT * FROM predios_seleccionados)
	 AND uebaunit.ue_op_terreno IS NOT NULL
	 AND uebaunit.ue_op_construccion IS NULL
	 AND uebaunit.ue_op_unidadconstruccion IS NULL
	 GROUP BY uebaunit.ue_op_terreno
 ),
 info_terreno AS (
	SELECT op_terreno.t_id,
      json_build_object('id', op_terreno.t_id,
						'attributes', json_build_object(CONCAT('Área de op_terreno' , (SELECT * FROM unidad_area_terreno)), op_terreno.area_terreno,
														'op_predio', COALESCE(info_predio.op_predio, '[]')
													   )) as op_terreno
    FROM operacion.op_terreno LEFT JOIN info_predio ON info_predio.ue_op_terreno = op_terreno.t_id
	WHERE op_terreno.t_id IN (SELECT * FROM terrenos_seleccionados)
	ORDER BY op_terreno.t_id
 )
 SELECT json_agg(info_terreno.op_terreno) AS op_terreno FROM info_terreno