# Modelo del Grafo

## Labels

### Usuario

Propiedades: `id_usuario`, `nombre`, `edad`, `verificado`, `correos_asociados`, `fecha_registro`.

### Cuenta

Propiedades: `id_cuenta`, `saldo`, `tipo`, `fecha_creacion`, `activa`, `nivel_riesgo`.

### Transaccion

Propiedades: `id_transaccion`, `monto`, `fecha`, `minuto_dia`, `tipo`, `canal`, `etiquetas_alerta`, `es_sospechosa`, `riesgo_score`.

### Dispositivo

Propiedades: `id_dispositivo`, `tipo`, `ip`, `sistema_operativo`, `confiable`, `ultimo_uso`.

### Ubicacion

Propiedades: `id_ubicacion`, `pais`, `ciudad`, `latitud`, `longitud`, `zona_riesgo`.

## Relaciones

1. `(Usuario)-[:TIENE_CUENTA]->(Cuenta)`
2. `(Cuenta)-[:EMITE]->(Transaccion)`
3. `(Transaccion)-[:TRANSFIERE_A]->(Cuenta)`
4. `(Usuario)-[:USA]->(Dispositivo)`
5. `(Usuario)-[:RESIDE_EN]->(Ubicacion)`
6. `(Transaccion)-[:SE_REALIZA_DESDE]->(Dispositivo)`
7. `(Transaccion)-[:OCURRE_EN]->(Ubicacion)`
8. `(Cuenta)-[:REGISTRADA_EN]->(Ubicacion)`
9. `(Cuenta)-[:ASOCIADA_A]->(Dispositivo)`
10. `(Dispositivo)-[:UBICADO_EN]->(Ubicacion)`

Todas las relaciones incluyen tres o más propiedades.

## Señales de fraude implementadas

- Microtransacciones: muchas transacciones menores a 100 desde una misma cuenta.
- Dispositivos compartidos: un mismo dispositivo usado por varios usuarios.
- Ubicaciones inusuales: transacciones fuera de la ubicación de residencia.
- Cuentas destino nuevas o inactivas.
- Cadenas de transferencia entre cuentas relacionadas.
