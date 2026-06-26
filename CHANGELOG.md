# Changelog

## [5.8.2] - 2026-06-26

### Fixed
- **API BNA — parseo de valores en formato argentino**: los valores devueltos por el BNA (`"1.451,00"`) no se convertían correctamente a float, causando que `valor_dolar` y `valor_euro` se almacenaran como 0 y rompiendo todos los cálculos del cotizador.
- **Bug `activar_coef` — modificación in-place de campos del order**: al activar "Modificar porcentajes manualmente", el código dividía `coef_dexport` y `coef_utilidad` directamente sobre los campos del order antes de calcular. Si el cálculo fallaba, los campos quedaban corruptos. Ahora se usan variables locales para la conversión a fracción.
- **Todos los valores se reseteaban a 0 al activar modo manual**: consecuencia directa de los dos bugs anteriores combinados. Al calcular con `valor_dolar = 0`, se producía una división por cero silenciosa en `calcular_coeficiente` que devolvía todo en 0.
- **Timeout y manejo de errores en API BNA**: se agregó `timeout=10` y captura de excepciones para que una falla de red no corte el flujo de cotización.

### Added
- **Fallback manual de dólar y euro**: cuando "Modificar porcentajes manualmente" está activo, los campos `Valor Dólar BNA` y `Valor Euro BNA` se vuelven editables. Si el usuario carga los valores manualmente, no se pisan con la API al recalcular. Útil cuando el BNA no está disponible.

---

## [5.8.1] - (versión anterior)
