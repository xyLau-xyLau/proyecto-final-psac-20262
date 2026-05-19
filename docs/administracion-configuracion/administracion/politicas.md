# Políticas para la Administración y Desarrollo de Software

## Información

### Aprobación

| Rol | Nombre | Fecha |
| --- | --- | --- |
| Desarrollador | Sofía Alatorre | 17/Mayo/2026 |
| QA | Sebastián Solano | 17/Mayo/2026 |
| QA | Ernesto Cárdenas | 17/Mayo/2026 |

### Control de Versiones

| Version | Fecha | Responsable | Breve descripción |
| --- | --- | --- | --- |
| 0.1 | 17/Mayo/2026 | Ernesto Cárdenas | Versión inicial |

### Tabla de Revisiones

| Periodo de revisión | Fecha de la última revisión | Fecha para la siguiente revisión |
| --- | --- | --- |
| Semanal | 17/Mayo/2026 | 24/Mayo/2026 |

## Propósito

Las políticas aquí descritas tienen como propósito definir e implementar prácticas estandarizadas a través del ciclo de vida del Software(SBAC),
incluyendo el diseño, desarrollo, pruebas, despliegue y mantenimiento.

Mediante el cumplimiento de estas políticas ampliamos nuestro compromiso para entregar un producto de Software de alta calidad, que cumpla con
estándares de seguridad y provea valor para nuestros clientes y usuarios.

## Alcance

Las políticas de este documento aplican a todas las actividades de desarrollo de software que ejecuta el equipo de trabajo y abarcan todas las etapas del ciclo de desarrollo de software.

## Políticas

- PD-001. Para el manejo del entorno de desarrollo se hará uso de contenedores mediante Docker. El archivo de Docker se encuentra en: <link>.
- PD-002. Para realizar cambios al Dockerfile se requerirá avisar al equipo de trabajo.
- PD-003. Para asegurar consistencia se usará el estándar de estilo PEP8.
- PD-004. Todo módulo será documentado siguiendo el estándar de documentación mediante Docstrings PEP257
- PD-005. Todo desarrollador es responsable del trabajo que se le asigna y deberá informar cualquier incidente o complicación al equipo para no retrasar la producción.
- PD-006. Se usará un repositorio centralizado en Github con 3 tipos de ramas: Main, Developmental y Features.
- PD-007. Antes de integrar una rama a main se solicitará hacer pruebas de integración en los módulos que puedan verse afectados por los cambios.
- PD-008. Si el desarrollador usa LLM's para generar partes o la totalidad de cualquier módulo deberá especificar en el commit los archivos involucrados, así como incluir en la documentación de dichos módulos el modelo usado, el prompt y que funciones fueron generadas.
- PD-009. Para aceptar Pull Request se requiere la aprobación de otro desarrollador.
