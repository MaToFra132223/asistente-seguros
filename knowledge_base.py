# Base de Conocimiento para Respuestas Estandarizadas
# Estas respuestas seran inyectadas en el prompt del sistema.

STANDARD_PROCEDURES = {
    "CHOQUE_SIN_LESIONADOS": """
    Procedimiento para Choque SIN Lesionados:
    1. Tomar fotos de los daños de ambos vehículos y las patentes.
    2. Pedir foto de: registro de conducir y tarjeta verde/azul del otro conductor.
    3. Pedir foto del comprobante de seguro del otro conductor.
    4. NO asumir culpas verbalmente, solo intercambiar datos.
    """,
    
    "CHOQUE_CON_LESIONADOS": """
    Procedimiento para Choque CON Lesionados:
    1. PRIORIDAD: Llamar al servicio de emergencias (107) y Policia (911).
    2. No mover a los heridos salvo peligro inminente.
    3. Realizar la denuncia policial correspondiente.
    4. Contactar urgente a nuestra oficina para asistencia legal inmediata.
    """,
    
    "DOCUMENTACION_CIRCULAR": """
    Documentación obligatoria para circular:
    - Licencia de conducir vigente.
    - Cédula Verde (o Azul si no es titular).
    - Comprobante de seguro en vigencia (físico o digital en app Mi Argentina).
    - VTV (Verificación Técnica Vehicular) o RTO vigente.
    - Patentes legibles.
    """,
    
    "PEDIDO_GRUA": """
    Para pedir Auxilio Mecánico, primero consultá qué compañía tiene el cliente y bríndale el número directo:
    
    *   **Rivadavia Seguros**: 0800-666-6789 (o SMS "SOS" + Patente al 70703)
    *   **Federación Patronal**: 0800-222-0022 (o SMS al 70703)
    *   **La Caja**: 0810-888-2894
    *   **Mercantil Andina**: 0800-777-2634 (WhatsApp: +54 9 11 2808-0012)
    *   **Mapfre**: 0800-999-7424 (WhatsApp: +54 9 11 6299-6922)

    Datos necesarios que le van a pedir:
    - Ubicación exacta (calle, altura, localidad o ruta y km).
    - Patente del vehículo.
    - Marca, Modelo y Color.
    - Motivo: (Mecánica, Batería, Neumático, Siniestro).
    - Cantidad de personas a trasladar.
    - Teléfono de contacto del conductor.
    - Teléfono de contacto del conductor.
    """,
    "AGENDA_EQUIPO": """
    **Directorio de Contactos Internos (Mirabet Seguros)**
    
    *Úsalo solo si el cliente necesita derivación específica o hablar con una persona.*
    *   **Cobranzas**: Carla Algarbe Cobranzas - 3406 643414
    *   **Ventas y Administración**: Yanina Morero Administracion - 3406 514262
    *   **Siniestros**: Flor SINIESTROS - 3406 518866
    *   **Gerencia / Casos Extremos**: Pablo - [Derivar solo si es crítico]

    ⚠️ **REGLA IMPORTANTE DE HORARIO**:
    - **Lunes a Jueves**: 08:00 a 12:30 y 15:00 a 18:30.
    - **Viernes**: 08:00 a 16:00 (Corrido).
    - **Sábados, Domingos y Fuera de Hora**: LA OFICINA ESTÁ CERRADA. NO compartas números personales. Indica el horario de atención y brinda solo los 0800 de Auxilio Mecánico o Emergencias.
    """
}
