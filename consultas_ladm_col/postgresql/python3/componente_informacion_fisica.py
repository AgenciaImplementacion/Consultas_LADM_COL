valuation_model = True

schema = 'fdm'
plot_t_id = '13117'
parcel_fmi = 'NULL'
parcel_number = 'NULL'
previous_parcel_number = 'NULL'

query = """
WITH
 terrenos_seleccionados AS (
	SELECT {plot_t_id} AS ue_terreno WHERE '{plot_t_id}' <> 'NULL'
		UNION
	SELECT uebaunit.ue_terreno FROM {schema}.predio LEFT JOIN {schema}.uebaunit ON predio.t_id = uebaunit.baunit_predio  WHERE uebaunit.ue_terreno IS NOT NULL AND CASE WHEN '{parcel_fmi}' = 'NULL' THEN  1 = 2 ELSE predio.fmi = '{parcel_fmi}' END
		UNION
	SELECT uebaunit.ue_terreno FROM {schema}.predio LEFT JOIN {schema}.uebaunit ON predio.t_id = uebaunit.baunit_predio  WHERE uebaunit.ue_terreno IS NOT NULL AND CASE WHEN '{parcel_number}' = 'NULL' THEN  1 = 2 ELSE predio.numero_predial = '{parcel_number}' END
		UNION
	SELECT uebaunit.ue_terreno FROM {schema}.predio LEFT JOIN {schema}.uebaunit ON predio.t_id = uebaunit.baunit_predio  WHERE uebaunit.ue_terreno IS NOT NULL AND CASE WHEN '{previous_parcel_number}' = 'NULL' THEN  1 = 2 ELSE predio.numero_predial_anterior = '{previous_parcel_number}' END
 ),
 predios_seleccionados AS (
	SELECT uebaunit.baunit_predio as t_id FROM {schema}.uebaunit WHERE uebaunit.ue_terreno = {plot_t_id} AND '{plot_t_id}' <> 'NULL'
		UNION
	SELECT t_id FROM {schema}.predio WHERE CASE WHEN '{parcel_fmi}' = 'NULL' THEN  1 = 2 ELSE predio.fmi = '{parcel_fmi}' END
		UNION
	SELECT t_id FROM {schema}.predio WHERE CASE WHEN '{parcel_number}' = 'NULL' THEN  1 = 2 ELSE predio.numero_predial = '{parcel_number}' END
		UNION
	SELECT t_id FROM {schema}.predio WHERE CASE WHEN '{previous_parcel_number}' = 'NULL' THEN  1 = 2 ELSE predio.numero_predial_anterior = '{previous_parcel_number}' END
 ),
 construcciones_seleccionadas AS (
	 SELECT ue_construccion FROM {schema}.uebaunit WHERE uebaunit.baunit_predio IN (SELECT predios_seleccionados.t_id FROM predios_seleccionados WHERE predios_seleccionados.t_id IS NOT NULL) AND ue_construccion IS NOT NULL
 ),
 unidadesconstruccion_seleccionadas AS (
	 SELECT unidadconstruccion.t_id FROM {schema}.unidadconstruccion WHERE unidadconstruccion.construccion IN (SELECT ue_construccion FROM construcciones_seleccionadas)
 ),
 uc_fuente_espacial AS (
	SELECT uefuente.ue_unidadconstruccion,
		json_agg(
				json_build_object('id', col_fuenteespacial.t_id,
									   'attributes', json_build_object('Tipo de fuente espacial', col_fuenteespacial.Tipo,
																	   'Estado disponibilidad', col_fuenteespacial.estado_disponibilidad,
																	   'Tipo principal', col_fuenteespacial.tipo_principal,
																	   'Oficialidad', col_fuenteespacial.oficialidad,
																	   'Fecha de entrega', col_fuenteespacial.fecha_entrega,
																	   'Fecha de grabación', col_fuenteespacial.fecha_grabacion,
																	   'Enlace fuente espacial', extarchivo.datos))
		) FILTER(WHERE ueFuente.pfuente IS NOT NULL) AS col_fuenteespacial
	FROM {schema}.uefuente LEFT JOIN {schema}.col_fuenteespacial ON uefuente.pfuente = col_fuenteespacial.t_id
    LEFT JOIN {schema}.extarchivo ON extarchivo.col_fuenteespacial_ext_archivo_id = col_fuenteespacial.t_id
	WHERE uefuente.ue_unidadconstruccion IN (SELECT * FROM unidadesconstruccion_seleccionadas)
	GROUP BY ueFuente.ue_unidadconstruccion 
 ),
info_uc AS (
	 SELECT unidadconstruccion.construccion,
			json_agg(json_build_object('id', unidadconstruccion.t_id,
							  'attributes', json_build_object('Número de pisos', unidadconstruccion.numero_pisos,
"""

if valuation_model:
    query += """
															  'Uso', unidad_construccion.uso,
															  'Puntuación', unidad_construccion.puntuacion,
															  'Tipología', unidad_construccion.tipologia,
															  'Puntuación', unidad_construccion.puntuacion,
															  'Destino económico', unidad_construccion.destino_econo,
															  'Tipo de construcción', unidad_construccion.construccion_tipo,
    """
else:
    query += """
															  'Uso', NULL,
															  'Puntuación', NULL,
															  'Tipología', NULL,
															  'Puntuación', NULL,
															  'Destino económico', NULL,
															  'Tipo de construcción', NULL,
    """

query += """
															  'Área privada construida', unidadconstruccion.area_privada_construida,
															  'Área construida', unidadconstruccion.area_construida,
															  'col_fuenteespacial', COALESCE(uc_fuente_espacial.col_fuenteespacial, '[]')
															 ))) as unidadconstruccion
	 FROM {schema}.unidadconstruccion LEFT JOIN uc_fuente_espacial ON unidadconstruccion.t_id = uc_fuente_espacial.ue_unidadconstruccion
"""

if valuation_model:
    query += """
	 LEFT JOIN {schema}.avaluounidadconstruccion ON unidadconstruccion.t_id = avaluounidadconstruccion.ucons
	 LEFT JOIN {schema}.unidad_construccion ON avaluounidadconstruccion.aucons = unidad_construccion.t_id
    """

query += """
	 WHERE unidadconstruccion.t_id IN (SELECT * FROM unidadesconstruccion_seleccionadas)
     GROUP BY unidadconstruccion.construccion
 ),
 c_fuente_espacial AS (
	SELECT uefuente.ue_construccion,
		json_agg(
				json_build_object('id', col_fuenteespacial.t_id,
									   'attributes', json_build_object('Tipo de fuente espacial', col_fuenteespacial.Tipo,
																	   'Estado disponibilidad', col_fuenteespacial.estado_disponibilidad,
																	   'Tipo principal', col_fuenteespacial.tipo_principal,
																	   'Oficialidad', col_fuenteespacial.oficialidad,
																	   'Fecha de entrega', col_fuenteespacial.fecha_entrega,
																	   'Fecha de grabación', col_fuenteespacial.fecha_grabacion,
																	   'Enlace fuente espacial', extarchivo.datos))														   
		) FILTER(WHERE ueFuente.pfuente IS NOT NULL) AS col_fuenteespacial
	FROM {schema}.uefuente LEFT JOIN {schema}.col_fuenteespacial ON uefuente.pfuente = col_fuenteespacial.t_id
	LEFT JOIN {schema}.extarchivo ON extarchivo.col_fuenteespacial_ext_archivo_id = col_fuenteespacial.t_id
	WHERE uefuente.ue_construccion IN (SELECT * FROM construcciones_seleccionadas)
	GROUP BY uefuente.ue_construccion 
 ),
 info_construccion as (
  SELECT uebaunit.baunit_predio,
		json_agg(json_build_object('id', construccion.t_id,
						  'attributes', json_build_object('Área construcción', construccion.area_construccion,
"""

if valuation_model:
    query += """
														  'Ńúmero de pisos', avaluos_v2_2_1avaluos_construccion.numero_pisos,
    """
else:
    query += """
    														  'Ńúmero de pisos', NULL,
        """

query += """
														  'col_fuenteespacial', COALESCE(c_fuente_espacial.col_fuenteespacial, '[]'),
														  'unidadconstruccion', COALESCE(info_uc.unidadconstruccion, '[]')
														 ))) FILTER(WHERE construccion.t_id IS NOT NULL) as construccion
  FROM {schema}.construccion LEFT JOIN c_fuente_espacial ON construccion.t_id = c_fuente_espacial.ue_construccion
  LEFT JOIN info_uc ON construccion.t_id = info_uc.construccion
  LEFT JOIN {schema}.uebaunit ON uebaunit.ue_construccion = info_uc.construccion
"""

if valuation_model:
    query += """
    LEFT JOIN {schema}.avaluoconstruccion ON avaluoconstruccion.cons = construccion.t_id
    LEFT JOIN {schema}.avaluos_v2_2_1avaluos_construccion  ON avaluos_v2_2_1avaluos_construccion.t_id = avaluoconstruccion.cons
    """

query += """
  WHERE construccion.t_id IN (SELECT * FROM construcciones_seleccionadas)
  GROUP BY uebaunit.baunit_predio
 ),
 info_predio AS (
	 SELECT uebaunit.ue_terreno,
			json_agg(json_build_object('id', predio.t_id,
							  'attributes', json_build_object('NUPRE', predio.nupre,
															  'FMI', predio.fmi,
															  'Número predial', predio.numero_predial,
															  'Número predial anterior', predio.numero_predial_anterior,
															  'construccion', COALESCE(info_construccion.construccion, '[]')
															 ))) FILTER(WHERE predio.t_id IS NOT NULL) as predio
	 FROM {schema}.predio LEFT JOIN {schema}.uebaunit ON uebaunit.baunit_predio = predio.t_id
     LEFT JOIN info_construccion ON info_construccion.baunit_predio = predio.t_id
	 WHERE predio.t_id IN (SELECT * FROM predios_seleccionados)
		AND uebaunit.ue_terreno IS NOT NULL
		AND uebaunit.ue_construccion IS NULL
		AND uebaunit.ue_unidadconstruccion IS NULL
     GROUP BY uebaunit.ue_terreno
 ),
 t_fuente_espacial AS (
	SELECT uefuente.ue_terreno,
		json_agg(
				json_build_object('id', col_fuenteespacial.t_id,
									   'attributes', json_build_object('Tipo de fuente espacial', col_fuenteespacial.Tipo,
																	   'Estado disponibilidad', col_fuenteespacial.estado_disponibilidad,
																	   'Tipo principal', col_fuenteespacial.tipo_principal,
																	   'Oficialidad', col_fuenteespacial.oficialidad,
																	   'Fecha de entrega', col_fuenteespacial.fecha_entrega,
																	   'Fecha de grabación', col_fuenteespacial.fecha_grabacion,
																	   'Enlace fuente espacial', extarchivo.datos))														   
		) FILTER(WHERE ueFuente.pfuente IS NOT NULL) AS col_fuenteespacial
	FROM {schema}.uefuente LEFT JOIN {schema}.col_fuenteespacial ON uefuente.pfuente = col_fuenteespacial.t_id
    LEFT JOIN {schema}.extarchivo ON extarchivo.col_fuenteespacial_ext_archivo_id = col_fuenteespacial.t_id
	WHERE uefuente.ue_terreno IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY uefuente.ue_terreno 
 ),
 info_linderos_externos AS (
	SELECT masccl.uep_terreno,
		json_agg(
				json_build_object('id', lindero.t_id,
									   'attributes', json_build_object('Longitud', lindero.longitud))
		) FILTER(WHERE lindero.t_id IS NOT NULL) AS lindero
	FROM {schema}.lindero LEFT JOIN {schema}.masccl ON lindero.t_id = masccl.cclp_lindero
    WHERE masccl.uep_terreno IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY masccl.uep_terreno
 ),
 info_linderos_internos AS (
	SELECT menos.eu_terreno,
		json_agg(
				json_build_object('id', lindero.t_id,
									   'attributes', json_build_object('Longitud', lindero.longitud))
		) FILTER(WHERE lindero.t_id IS NOT NULL) AS lindero
	FROM {schema}.lindero LEFT JOIN {schema}.menos ON lindero.t_id = menos.ccl_lindero
	WHERE menos.eu_terreno IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY menos.eu_terreno
 ),
 info_punto_lindero_externos AS (
	 SELECT masccl.uep_terreno,
	 		json_agg(
				json_build_object('id', puntoccl.t_id,
									   'attributes', json_build_object('Nombre', puntolindero.nombre_punto,
																	   'x', st_x(puntolindero.localizacion_original),
																	   'y', st_y(puntolindero.localizacion_original),
																	   'z', st_z(puntolindero.localizacion_original))
			)) FILTER(WHERE puntoccl.t_id IS NOT NULL) AS puntolindero
	 FROM {schema}.puntolindero LEFT JOIN {schema}.puntoccl ON puntolindero.t_id = puntoccl.punto_puntolindero
	 LEFT JOIN {schema}.lindero ON puntoccl.ccl_lindero = lindero.t_id
	 LEFT JOIN {schema}.masccl ON lindero.t_id = masccl.cclp_lindero
     WHERE masccl.uep_terreno IN (SELECT * FROM terrenos_seleccionados)
	 GROUP BY masccl.uep_terreno
 ),
 info_punto_lindero_internos AS (
	 SELECT menos.eu_terreno,
	 		json_agg(
				json_build_object('id', puntoccl.t_id,
									   'attributes', json_build_object('Nombre', puntolindero.nombre_punto,
																	   'x', st_x(puntolindero.localizacion_original),
																	   'y', st_y(puntolindero.localizacion_original),
																	   'z', st_z(puntolindero.localizacion_original))
			)) FILTER(WHERE puntoccl.t_id IS NOT NULL) AS puntolindero
	 FROM {schema}.puntolindero LEFT JOIN {schema}.puntoccl ON puntolindero.t_id = puntoccl.punto_puntolindero
	 LEFT JOIN {schema}.lindero ON puntoccl.ccl_lindero = lindero.t_id
	 LEFT JOIN {schema}.menos ON lindero.t_id = menos.ccl_lindero
     WHERE menos.eu_terreno IN (SELECT * FROM terrenos_seleccionados)
	 GROUP BY menos.eu_terreno
 ),
col_bosqueareasemi_terreno_bosque_area_seminaturale AS (
	SELECT terreno_bosque_area_seminaturale,
		json_agg(
				json_build_object('id', t_id,
									   'attributes', json_build_object('avalue', avalue))
		) FILTER(WHERE t_id IS NOT NULL) AS col_bosqueareasemi_terreno_bosque_area_seminaturale
	FROM {schema}.col_bosqueareasemi_terreno_bosque_area_seminaturale 
    WHERE terreno_bosque_area_seminaturale IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY terreno_bosque_area_seminaturale
 ),
col_territorioagricola_terreno_territorio_agricola AS (
	SELECT terreno_territorio_agricola,
		json_agg(
				json_build_object('id', t_id,
									   'attributes', json_build_object('avalue', avalue))
		) FILTER(WHERE t_id IS NOT NULL) AS col_territorioagricola_terreno_territorio_agricola
	FROM {schema}.col_territorioagricola_terreno_territorio_agricola 
    WHERE terreno_territorio_agricola IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY terreno_territorio_agricola
 ),
col_cuerpoagua_terreno_evidencia_cuerpo_agua AS (
	SELECT terreno_evidencia_cuerpo_agua,
		json_agg(
				json_build_object('id', t_id,
									   'attributes', json_build_object('avalue', avalue))
		) FILTER(WHERE t_id IS NOT NULL) AS col_cuerpoagua_terreno_evidencia_cuerpo_agua
	FROM {schema}.col_cuerpoagua_terreno_evidencia_cuerpo_agua 
    WHERE terreno_evidencia_cuerpo_agua IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY terreno_evidencia_cuerpo_agua
 ),
col_explotaciontipo_terreno_explotacion AS (
	SELECT terreno_explotacion,
		json_agg(
				json_build_object('id', t_id,
									   'attributes', json_build_object('avalue', avalue))
		) FILTER(WHERE t_id IS NOT NULL) AS col_explotaciontipo_terreno_explotacion
	FROM {schema}.col_explotaciontipo_terreno_explotacion 
    WHERE terreno_explotacion IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY terreno_explotacion
 ),
col_afectacion_terreno_afectacion AS (
	SELECT terreno_afectacion,
		json_agg(
				json_build_object('id', t_id,
									   'attributes', json_build_object('avalue', avalue))
		) FILTER(WHERE t_id IS NOT NULL) AS col_afectacion_terreno_afectacion
	FROM {schema}.col_afectacion_terreno_afectacion 
    WHERE terreno_afectacion IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY terreno_afectacion
 ),
col_servidumbretipo_terreno_servidumbre AS (
	SELECT terreno_servidumbre,
		json_agg(
				json_build_object('id', t_id,
									   'attributes', json_build_object('avalue', avalue))
		) FILTER(WHERE t_id IS NOT NULL) AS col_servidumbretipo_terreno_servidumbre
	FROM {schema}.col_servidumbretipo_terreno_servidumbre 
    WHERE terreno_servidumbre IN (SELECT * FROM terrenos_seleccionados)
	GROUP BY terreno_servidumbre
 ),
info_puntolevantamiento AS (
	SELECT uebaunit_predio.ue_terreno,
			json_agg(
					json_build_object('id', puntoslevantamiento_seleccionados.t_id_puntolevantamiento,
										   'attributes', json_build_object('x', st_x(puntoslevantamiento_seleccionados.localizacion_original),
																		   'y', st_y(puntoslevantamiento_seleccionados.localizacion_original),
																		   'z', st_z(puntoslevantamiento_seleccionados.localizacion_original)))
			) FILTER(WHERE puntoslevantamiento_seleccionados.t_id_puntolevantamiento IS NOT NULL) AS puntolevantamiento
	FROM
	(
		SELECT puntolevantamiento.t_id AS t_id_puntolevantamiento, puntolevantamiento.localizacion_original, construccion.t_id AS t_id_construccion  FROM fdm.construccion, fdm.puntolevantamiento
		WHERE ST_Intersects(construccion.poligono_creado, puntolevantamiento.localizacion_original) = True AND construccion.t_id IN (1179, 1180, 1181)
	) AS puntoslevantamiento_seleccionados
	LEFT JOIN fdm.uebaunit AS uebaunit_construccion  ON uebaunit_construccion.ue_construccion = puntoslevantamiento_seleccionados.t_id_construccion
	LEFT JOIN fdm.uebaunit AS uebaunit_predio ON uebaunit_predio.baunit_predio = uebaunit_construccion.baunit_predio
	WHERE uebaunit_predio.ue_terreno IS NOT NULL AND 
		  uebaunit_predio.ue_construccion IS NULL AND 
		  uebaunit_predio.ue_unidadconstruccion IS NULL
	GROUP BY uebaunit_predio.ue_terreno
),
 info_terreno AS (
	SELECT terreno.t_id,
      json_build_object('id', terreno.t_id,
						'attributes', json_build_object('Área registral', terreno.area_registral, 
														'Área calculada', terreno.area_calculada,
														'col_territorioagricola_terreno_territorio_agricola', COALESCE(col_territorioagricola_terreno_territorio_agricola.col_territorioagricola_terreno_territorio_agricola, '[]'),
														'col_bosqueareasemi_terreno_bosque_area_seminaturale', COALESCE(col_bosqueareasemi_terreno_bosque_area_seminaturale.col_bosqueareasemi_terreno_bosque_area_seminaturale, '[]'),
														'col_cuerpoagua_terreno_evidencia_cuerpo_agua', COALESCE(col_cuerpoagua_terreno_evidencia_cuerpo_agua.col_cuerpoagua_terreno_evidencia_cuerpo_agua, '[]'),
														'col_explotaciontipo_terreno_explotacion', COALESCE(col_explotaciontipo_terreno_explotacion.col_explotaciontipo_terreno_explotacion, '[]'),
														'col_afectacion_terreno_afectacion', COALESCE(col_afectacion_terreno_afectacion.col_afectacion_terreno_afectacion, '[]'),
														'col_servidumbretipo_terreno_servidumbre', COALESCE(col_servidumbretipo_terreno_servidumbre.col_servidumbretipo_terreno_servidumbre, '[]'),
														'Linderos externos', COALESCE(info_linderos_externos.lindero, '[]'),
														'Puntos linderos externos', COALESCE(info_punto_lindero_externos.puntolindero, '[]'),
														'Linderos internos', COALESCE(info_linderos_internos.lindero, '[]'),
														'Puntos linderos internos', COALESCE(info_punto_lindero_internos.puntolindero, '[]'),
														'puntolevantamiento', COALESCE(info_puntolevantamiento.puntolevantamiento, '[]'),
														'col_fuenteespacial', COALESCE(t_fuente_espacial.col_fuenteespacial, '[]'),
														'predio', COALESCE(info_predio.predio, '[]')
													   )) as terreno
    FROM {schema}.terreno LEFT JOIN info_predio ON info_predio.ue_terreno = terreno.t_id
	LEFT JOIN t_fuente_espacial ON terreno.t_id = t_fuente_espacial.ue_terreno
	LEFT JOIN info_linderos_externos ON terreno.t_id = info_linderos_externos.uep_terreno
	LEFT JOIN info_linderos_internos ON terreno.t_id = info_linderos_internos.eu_terreno
    LEFT JOIN info_punto_lindero_externos ON terreno.t_id = info_punto_lindero_externos.uep_terreno
	LEFT JOIN info_punto_lindero_internos ON terreno.t_id = info_punto_lindero_internos.eu_terreno
	LEFT JOIN col_territorioagricola_terreno_territorio_agricola ON terreno.t_id = col_territorioagricola_terreno_territorio_agricola.terreno_territorio_agricola
	LEFT JOIN col_bosqueareasemi_terreno_bosque_area_seminaturale ON terreno.t_id = col_bosqueareasemi_terreno_bosque_area_seminaturale.terreno_bosque_area_seminaturale
	LEFT JOIN col_cuerpoagua_terreno_evidencia_cuerpo_agua ON terreno.t_id = col_cuerpoagua_terreno_evidencia_cuerpo_agua.terreno_evidencia_cuerpo_agua
	LEFT JOIN col_explotaciontipo_terreno_explotacion ON terreno.t_id = col_explotaciontipo_terreno_explotacion.terreno_explotacion
	LEFT JOIN col_afectacion_terreno_afectacion ON terreno.t_id = col_afectacion_terreno_afectacion.terreno_afectacion
	LEFT JOIN col_servidumbretipo_terreno_servidumbre ON terreno.t_id = col_servidumbretipo_terreno_servidumbre.terreno_servidumbre
    LEFT JOIN info_puntolevantamiento ON terreno.t_id = info_puntolevantamiento.ue_terreno
	WHERE terreno.t_id IN (SELECT * FROM terrenos_seleccionados)
 )				
SELECT json_agg(info_terreno.terreno) AS terreno FROM info_terreno
"""

query = query.format(schema= schema, plot_t_id=plot_t_id, parcel_fmi=parcel_fmi, parcel_number=parcel_number, previous_parcel_number=previous_parcel_number)

print(query)