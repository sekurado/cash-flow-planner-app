<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es_ES">
<context>
    <name>AppErrors</name>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="263"/>
        <source>Invalid data. Please check your input.</source>
        <translation>Datos no válidos. Compruebe la información introducida.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="264"/>
        <source>Live exchange-rate fetching is not enabled.</source>
        <translation>La obtención de tipos de cambio en vivo no está activada.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="265"/>
        <source>Base currency is required to fetch live exchange rates.</source>
        <translation>Se requiere la moneda base para obtener tipos de cambio en vivo.</translation>
    </message>
    <message>
        <source>No simulation result to export.</source>
        <translation type="vanished">No hay resultados de simulación para exportar.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="269"/>
        <source>Name is required</source>
        <translation>El nombre es obligatorio</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="270"/>
        <source>Currency is required</source>
        <translation>La moneda es obligatoria</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="271"/>
        <source>Exchange rate API returned invalid JSON</source>
        <translation>La API de tipos de cambio devolvió JSON no válido</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="272"/>
        <source>Exchange rate API response is missing conversion rates</source>
        <translation>La respuesta de la API de tipos de cambio no incluye tasas de conversión</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="275"/>
        <source>Exchange rate API returned a zero rate</source>
        <translation>La API de tipos de cambio devolvió una tasa cero</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="276"/>
        <source>Simulation params must include a numeric initial_balance</source>
        <translation>Los parámetros de simulación deben incluir un saldo inicial numérico</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="279"/>
        <source>Simulation params must include a non-empty base_currency</source>
        <translation>Los parámetros de simulación deben incluir una moneda base no vacía</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="282"/>
        <source>Simulation params must include ISO start_date and end_date</source>
        <translation>Los parámetros de simulación deben incluir fechas de inicio y fin en formato ISO</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="285"/>
        <source>Exchange rates must target USD, got GBP</source>
        <translation>Los tipos de cambio deben apuntar a USD, se recibió GBP</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="286"/>
        <source>Exchange rates cannot use USD as the source currency</source>
        <translation>Los tipos de cambio no pueden usar USD como moneda de origen</translation>
    </message>
    <message>
        <source>Plan not found: %1</source>
        <translation type="vanished">Plan no encontrado: %1</translation>
    </message>
    <message>
        <source>Entry not found: %1</source>
        <translation type="vanished">Entrada no encontrada: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="268"/>
        <source>No projection result to export.</source>
        <translation>No hay resultado de proyección para exportar.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="287"/>
        <source>Forecast not found: %1</source>
        <translation>Previsión no encontrada: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="288"/>
        <source>A forecast named &quot;%1&quot; already exists</source>
        <translation>Ya existe una previsión llamada «%1»</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="289"/>
        <source>Cash flow not found: %1</source>
        <translation>Flujo de caja no encontrado: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="290"/>
        <source>Invalid date pattern: %1</source>
        <translation>Patrón de fecha no válido: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="291"/>
        <source>Unsupported file type: %1</source>
        <translation>Tipo de archivo no compatible: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="292"/>
        <source>No exchange rate found for %1 → %2</source>
        <translation>No se encontró tipo de cambio para %1 → %2</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="293"/>
        <source>Simulation range of %1 days exceeds the %2-day (10-year) limit</source>
        <translation>El rango de simulación de %1 días supera el límite de %2 días (10 años)</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="296"/>
        <source>Exchange rate API returned HTTP %1</source>
        <translation>La API de tipos de cambio devolvió HTTP %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="297"/>
        <source>Mock exchange rates are not defined for base currency %1</source>
        <translation>Los tipos de cambio simulados no están definidos para la moneda base %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="300"/>
        <source>Mock exchange rates are missing symbols: %1</source>
        <translation>Faltan símbolos en los tipos de cambio simulados: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="301"/>
        <source>%1 must be a mapping</source>
        <translation>%1 debe ser un objeto</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="302"/>
        <source>Daily live rate fetch limit reached (10 per day). Try again tomorrow.</source>
        <translation>Límite diario de obtención de tipos alcanzado (10 por día). Inténtelo mañana.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="305"/>
        <source>Please wait %1 second(s) before fetching live rates again.</source>
        <translation>Espere %1 segundo(s) antes de obtener tipos en vivo de nuevo.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="308"/>
        <source>Please wait %1 minute(s) before fetching live rates again.</source>
        <translation>Espere %1 minuto(s) antes de obtener tipos en vivo de nuevo.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="311"/>
        <source>User manual is not available.</source>
        <translation>El manual de usuario no está disponible.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="312"/>
        <source>Could not open the user manual.</source>
        <translation>No se pudo abrir el manual de usuario.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="313"/>
        <source>Receipt image storage is not configured</source>
        <translation>El almacenamiento de imágenes de recibos no está configurado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="314"/>
        <source>Receipt OCR on macOS requires PyObjC Vision bindings. Install on-device scanning from Settings, or enter the expense manually.</source>
        <translation>El OCR de recibos en macOS requiere los enlaces PyObjC de Vision. Instale el escaneo en el dispositivo desde Ajustes, o introduzca el gasto manualmente.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="319"/>
        <source>On-device receipt scanning can only be installed on macOS.</source>
        <translation>El escaneo de recibos en el dispositivo solo se puede instalar en macOS.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="323"/>
        <source>On-device receipt scanning cannot be installed in this app build.</source>
        <translation>El escaneo de recibos en el dispositivo no se puede instalar en esta versión de la aplicación.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="327"/>
        <source>Could not install on-device receipt scanning. Check your network connection and try again.</source>
        <translation>No se pudo instalar el escaneo de recibos en el dispositivo. Compruebe la conexión de red e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="332"/>
        <source>Installing on-device receipt scanning timed out. Check your network and try again.</source>
        <translation>La instalación del escaneo de recibos en el dispositivo agotó el tiempo de espera. Compruebe la red e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="336"/>
        <source>Installed OCR packages but Vision is still unavailable. Restart the app and try Scan again.</source>
        <translation>Se instalaron los paquetes de OCR, pero Vision sigue no disponible. Reinicie la aplicación e intente Escanear de nuevo.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="341"/>
        <source>Could not install on-device receipt scanning: %1</source>
        <translation>No se pudo instalar el escaneo de recibos en el dispositivo: %1</translation>
    </message>
    <message>
        <source>Receipt OCR on macOS requires PyObjC Vision bindings. Install the &apos;ocr-macos&apos; extra or enter the expense manually.</source>
        <translation type="vanished">El OCR de recibos en macOS requiere los enlaces PyObjC de Vision. Instale el extra &apos;ocr-macos&apos; o introduzca el gasto manualmente.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="342"/>
        <source>Receipt scanning is not available on this platform (%1). Enter the expense manually.</source>
        <translation>El escaneo de recibos no está disponible en esta plataforma (%1). Introduzca el gasto manualmente.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="346"/>
        <source>Receipt image not found: %1</source>
        <translation>No se encontró la imagen del recibo: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="347"/>
        <source>Could not read text from receipt image: %1</source>
        <translation>No se pudo leer el texto de la imagen del recibo: %1</translation>
    </message>
    <message>
        <source>Live rates were already fetched today. Try again in %1 hour(s).</source>
        <translation type="vanished">Los tipos en vivo ya se obtuvieron hoy. Inténtelo de nuevo en %1 hora(s).</translation>
    </message>
</context>
<context>
    <name>AuditLog</name>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="129"/>
        <source>Created forecast &apos;%1&apos;</source>
        <translation>Pronóstico «%1» creado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="130"/>
        <source>Deleted forecast &apos;%1&apos;</source>
        <translation>Pronóstico «%1» eliminado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="131"/>
        <source>Renamed forecast to &apos;%1&apos;</source>
        <translation>Pronóstico renombrado a «%1»</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="132"/>
        <source>Updated opening balance to %1</source>
        <translation>Saldo inicial actualizado a %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="133"/>
        <source>Updated base currency to %1</source>
        <translation>Moneda base actualizada a %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="134"/>
        <source>Updated forecast &apos;%1&apos;</source>
        <translation>Pronóstico «%1» actualizado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="135"/>
        <source>Added cash flow &apos;%1&apos; (%2)</source>
        <translation>Flujo de caja «%1» añadido (%2)</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="136"/>
        <source>Removed cash flow &apos;%1&apos;</source>
        <translation>Flujo de caja «%1» eliminado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="137"/>
        <source>Updated cash flow &apos;%1&apos;</source>
        <translation>Flujo de caja «%1» actualizado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="138"/>
        <source>Updated cash flow &apos;%1&apos;: %2</source>
        <translation>Flujo de caja «%1» actualizado: %2</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="139"/>
        <source>amount %1 → %2</source>
        <translation>importe %1 → %2</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="140"/>
        <source>renamed to &apos;%1&apos;</source>
        <translation>renombrado a «%1»</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="141"/>
        <source>type %1 → %2</source>
        <translation>tipo %1 → %2</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="142"/>
        <source>currency %1 → %2</source>
        <translation>moneda %1 → %2</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="143"/>
        <source>schedule updated</source>
        <translation>calendario actualizado</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="144"/>
        <source>category updated</source>
        <translation>categoría actualizada</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="145"/>
        <source>marked active</source>
        <translation>marcado como activo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/audit_log_messages.py" line="146"/>
        <source>marked inactive</source>
        <translation>marcado como inactivo</translation>
    </message>
</context>
<context>
    <name>BalanceChart</name>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="84"/>
        <source>%1 %2</source>
        <translation>%1 %2</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="278"/>
        <source>Balance chart (%1)</source>
        <translation>Gráfico de saldo (%1)</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="279"/>
        <source>Balance chart</source>
        <translation>Gráfico de saldo</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="288"/>
        <source>Run a forecast to see the balance chart.</source>
        <translation>Ejecute una previsión para ver el gráfico de saldo.</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="445"/>
        <source>Shortfall</source>
        <translation>Déficit de tesorería</translation>
    </message>
    <message>
        <source>Run a simulation to see the balance chart.</source>
        <translation type="vanished">Ejecute una simulación para ver el gráfico de saldo.</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="409"/>
        <source>Balance</source>
        <translation>Saldo</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="427"/>
        <source>Surplus</source>
        <translation>Superávit</translation>
    </message>
    <message>
        <source>Deficit</source>
        <translation type="vanished">Déficit</translation>
    </message>
    <message>
        <location filename="../qml/components/BalanceChart.qml" line="462"/>
        <source>Break-even</source>
        <translation>Punto de equilibrio</translation>
    </message>
</context>
<context>
    <name>CashFlowSuggestions</name>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="37"/>
        <source>Cut recurring expenses by %1%</source>
        <translation>Reducir los gastos recurrentes un %1%</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="38"/>
        <source>A uniform %1% reduction across recurring expenses saves about %2 per month and removes the projected cash shortfall.</source>
        <translation>Una reducción uniforme del %1% en los gastos recurrentes ahorra unos %2 al mes y elimina el déficit de caja previsto.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="43"/>
        <source>Reduce %1</source>
        <translation>Reducir %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="44"/>
        <source>Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall if no other cash flows change.</source>
        <translation>Reducir %1 en %2 por ocurrencia basta para evitar el déficit de caja previsto si no cambian otros flujos.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="49"/>
        <source>Add %1 recurring income per month</source>
        <translation>Añadir %1 de ingresos recurrentes al mes</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="50"/>
        <source>Increasing recurring income by about %1 per month keeps the projection non-negative through the horizon.</source>
        <translation>Aumentar los ingresos recurrentes unos %1 al mes mantiene la proyección no negativa en todo el horizonte.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="55"/>
        <source>Increase opening balance by %1</source>
        <translation>Aumentar el saldo inicial en %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="56"/>
        <source>Raising the opening balance by %1 provides enough cushion to stay positive through the projection period.</source>
        <translation>Subir el saldo inicial en %1 aporta margen suficiente para mantenerse positivo durante el período de proyección.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="61"/>
        <source>Consider deferring %1</source>
        <translation>Considerar aplazar %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="62"/>
        <source>%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. Deferring this one-time expense may extend runway.</source>
        <translation>%1 está programado el %2, dentro de los 30 días previos al déficit de caja previsto el %3. Aplazar este gasto puntual puede ampliar el margen.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="67"/>
        <source>Review %1 spending</source>
        <translation>Revisar el gasto en %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="68"/>
        <source>%1 averages %2 per month in this projection. Trimming discretionary categories is an easy way to save more.</source>
        <translation>%1 promedia %2 al mes en esta proyección. Recortar categorías discrecionales es una forma sencilla de ahorrar más.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="73"/>
        <source>You could save %1 more per month</source>
        <translation>Podría ahorrar %1 más al mes</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="74"/>
        <source>The projection stays positive if recurring expenses rise by up to %1 per month — the same amount you could redirect to savings.</source>
        <translation>La proyección se mantiene positiva si los gastos recurrentes suben hasta %1 al mes — la misma cantidad que podría destinar al ahorro.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="79"/>
        <source>Build a %1 cash buffer</source>
        <translation>Crear un colchón de caja de %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="80"/>
        <source>Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 to absorb normal variability.</source>
        <translation>Su saldo final de %1 es escaso respecto a las salidas mensuales. Apunte al menos a %2 para absorber la variabilidad normal.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="85"/>
        <source>About %1 months of runway</source>
        <translation>Unos %1 meses de margen</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/suggestion_copy.py" line="86"/>
        <source>At the current burn rate, %1 covers roughly %2 months of net cash outflow through the projection period.</source>
        <translation>Al ritmo de consumo actual, %1 cubre aproximadamente %2 meses de salida neta de caja en el período de proyección.</translation>
    </message>
</context>
<context>
    <name>ChangeHistoryPage</name>
    <message>
        <location filename="../qml/pages/ChangeHistoryPage.qml" line="44"/>
        <source>Forecast history</source>
        <translation>Historial del pronóstico</translation>
    </message>
    <message>
        <location filename="../qml/pages/ChangeHistoryPage.qml" line="53"/>
        <source>Select a forecast to view its change history.</source>
        <translation>Seleccione un pronóstico para ver su historial de cambios.</translation>
    </message>
    <message>
        <location filename="../qml/pages/ChangeHistoryPage.qml" line="62"/>
        <source>No changes recorded yet.</source>
        <translation>Aún no se han registrado cambios.</translation>
    </message>
</context>
<context>
    <name>CurrencyRateEditor</name>
    <message>
        <source>Exchange rates</source>
        <translation type="vanished">Tipos de cambio</translation>
    </message>
    <message>
        <source>Add rate</source>
        <translation type="vanished">Añadir tipo</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="121"/>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="417"/>
        <source>Add exchange rate</source>
        <translation>Añadir tipo de cambio</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="134"/>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="397"/>
        <source>Delete all</source>
        <translation>Eliminar todo</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="137"/>
        <source>Delete all exchange rates</source>
        <translation>Eliminar todos los tipos de cambio</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="143"/>
        <source>Fetching…</source>
        <translation>Obteniendo…</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="143"/>
        <source>Fetch live rates</source>
        <translation>Obtener tasas</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="149"/>
        <source>Fetch live exchange rates</source>
        <translation>Obtener tipos de cambio en vivo</translation>
    </message>
    <message>
        <source>Next fetch available in %1 hour(s).</source>
        <translation type="vanished">Próxima obtención disponible en %1 hora(s).</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="178"/>
        <source>No exchange rates defined. Add a rate or fetch live rates.</source>
        <translation>No hay tipos de cambio definidos. Añada un tipo u obtenga tasas en vivo.</translation>
    </message>
    <message>
        <source>From</source>
        <translation type="vanished">De</translation>
    </message>
    <message>
        <source>To</source>
        <translation type="vanished">A</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="212"/>
        <source>Currency</source>
        <translation>Moneda</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="222"/>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="458"/>
        <source>Rate</source>
        <translation>Tipo</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="232"/>
        <source>Updated</source>
        <translation>Actualizado</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="302"/>
        <source>Exchange rate value</source>
        <translation>Valor del tipo de cambio</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="344"/>
        <source>Delete exchange rate</source>
        <translation>Eliminar tipo de cambio</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="119"/>
        <source>+ Add currency</source>
        <translation>+ Añadir moneda</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="164"/>
        <source>Daily fetch limit reached (10 per day). Try again tomorrow.</source>
        <translation>Límite diario de obtención alcanzado (10 por día). Inténtelo mañana.</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="166"/>
        <source>Next fetch available in %1 second(s).</source>
        <translation>Próxima obtención disponible en %1 segundo(s).</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="168"/>
        <source>Next fetch available in %1 minute(s).</source>
        <translation>Próxima obtención disponible en %1 minuto(s).</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="373"/>
        <source>Delete all exchange rates?</source>
        <translation>¿Eliminar todos los tipos de cambio?</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="401"/>
        <source>Confirm delete all exchange rates</source>
        <translation>Confirmar eliminación de todos los tipos</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="429"/>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="438"/>
        <source>From currency</source>
        <translation>Moneda origen</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="443"/>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="453"/>
        <source>To currency</source>
        <translation>Moneda destino</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="466"/>
        <source>0.00</source>
        <translation>0.00</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="469"/>
        <source>Exchange rate</source>
        <translation>Tipo de cambio</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="390"/>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="475"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="383"/>
        <source>This removes every exchange rate from the app. Forecast runs with multi-currency cash flows may fail until you add rates again.</source>
        <translation>Esto elimina todos los tipos de cambio de la aplicación. Las previsiones con flujos de caja multidivisa pueden fallar hasta que añada tipos de nuevo.</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="481"/>
        <source>Save</source>
        <translation>Guardar</translation>
    </message>
    <message>
        <location filename="../qml/components/CurrencyRateEditor.qml" line="486"/>
        <source>Save exchange rate</source>
        <translation>Guardar tipo de cambio</translation>
    </message>
</context>
<context>
    <name>DatePatternInput</name>
    <message>
        <location filename="../qml/components/DatePatternInput.qml" line="21"/>
        <source>e.g. 10.. for monthly, ... for daily</source>
        <translation>p. ej. 10.. para mensual, ... para diario</translation>
    </message>
    <message>
        <location filename="../qml/components/DatePatternInput.qml" line="22"/>
        <source>Date pattern</source>
        <translation>Patrón de fecha</translation>
    </message>
    <message>
        <location filename="../qml/components/DatePatternInput.qml" line="26"/>
        <source>Pattern formats:
• ... — every day
• 10.. — monthly on the 10th
• 15.03. — yearly on 15 March
• 2026-06-15 — one-time on a date</source>
        <translation>Formatos de patrón:
• ... — cada día
• 10.. — mensual el día 10
• 15.03. — anual el 15 de marzo
• 2026-06-15 — puntual en una fecha</translation>
    </message>
    <message>
        <location filename="../qml/components/DatePatternInput.qml" line="48"/>
        <source>Invalid date pattern</source>
        <translation>Patrón de fecha no válido</translation>
    </message>
</context>
<context>
    <name>DatePicker</name>
    <message>
        <location filename="../qml/components/DatePicker.qml" line="278"/>
        <source>Date</source>
        <translation>Fecha</translation>
    </message>
    <message>
        <location filename="../qml/components/DatePicker.qml" line="140"/>
        <source>Previous month</source>
        <translation>Mes anterior</translation>
    </message>
    <message>
        <location filename="../qml/components/DatePicker.qml" line="163"/>
        <source>Next month</source>
        <translation>Mes siguiente</translation>
    </message>
</context>
<context>
    <name>DeficitBanner</name>
    <message>
        <source>%1 %2</source>
        <translation type="vanished">%1 %2</translation>
    </message>
    <message>
        <source>an entry</source>
        <translation type="vanished">una entrada</translation>
    </message>
    <message>
        <source>Cash deficit on %1: balance reaches %2 (%3 triggered this).</source>
        <translation type="vanished">Déficit de efectivo el %1: el saldo alcanza %2 (%3 lo provocó).</translation>
    </message>
    <message>
        <source>Cash deficit on %1 (%2 triggered this).</source>
        <translation type="vanished">Déficit de efectivo el %1 (%2 lo provocó).</translation>
    </message>
    <message>
        <source>Deficit warning</source>
        <translation type="vanished">Advertencia de déficit</translation>
    </message>
    <message>
        <source>Cash deficit detected</source>
        <translation type="vanished">Déficit de efectivo detectado</translation>
    </message>
    <message>
        <location filename="../qml/components/DeficitBanner.qml" line="79"/>
        <source>Cash shortfall warning</source>
        <translation>Aviso de déficit de tesorería</translation>
    </message>
    <message>
        <location filename="../qml/components/DeficitBanner.qml" line="90"/>
        <source>Cash shortfall detected</source>
        <translation>Déficit de tesorería detectado</translation>
    </message>
    <message>
        <location filename="../qml/components/DeficitBanner.qml" line="101"/>
        <source>First shortfall on %1</source>
        <translation>Primer déficit el %1</translation>
    </message>
    <message>
        <location filename="../qml/components/DeficitBanner.qml" line="113"/>
        <source>Dismiss cash shortfall alert</source>
        <translation>Descartar aviso de déficit de tesorería</translation>
    </message>
    <message>
        <source>Dismiss deficit alert</source>
        <translation type="vanished">Descartar alerta de déficit</translation>
    </message>
</context>
<context>
    <name>EntriesPage</name>
    <message>
        <source>%1 %2</source>
        <translation type="vanished">%1 %2</translation>
    </message>
    <message>
        <source>Entries</source>
        <translation type="vanished">Entradas</translation>
    </message>
    <message>
        <source>Add entry</source>
        <translation type="vanished">Añadir entrada</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="224"/>
        <source>Import</source>
        <translation>Importar</translation>
    </message>
    <message>
        <source>Import entries</source>
        <translation type="vanished">Importar entradas</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="250"/>
        <source>Income</source>
        <translation>Ingresos</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="251"/>
        <source>Income tab</source>
        <translation>Pestaña de ingresos</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="250"/>
        <source>Expense</source>
        <translation>Gasto</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="201"/>
        <source>Add your first cash flow using the + button</source>
        <translation>Añada su primer flujo de caja con el botón +</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="229"/>
        <source>Import cash flows</source>
        <translation>Importar flujos de caja</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="251"/>
        <source>Expense tab</source>
        <translation>Pestaña de gastos</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="283"/>
        <source>No income cash flows yet</source>
        <translation>Aún no hay flujos de ingreso</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="309"/>
        <source>No expense cash flows yet</source>
        <translation>Aún no hay flujos de gasto</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="329"/>
        <source>Add cash flow</source>
        <translation>Añadir flujo de caja</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="372"/>
        <source>Delete cash flow</source>
        <translation>Eliminar flujo de caja</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="135"/>
        <source>Active toggle for %1</source>
        <translation>Activar/desactivar %1</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="145"/>
        <source>Edit %1</source>
        <translation>Editar %1</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="154"/>
        <source>Delete %1</source>
        <translation>Eliminar %1</translation>
    </message>
    <message>
        <source>Add your first entry using the + button</source>
        <translation type="vanished">Añada su primera entrada con el botón +</translation>
    </message>
    <message>
        <source>No income entries yet</source>
        <translation type="vanished">Aún no hay entradas de ingresos</translation>
    </message>
    <message>
        <source>No expense entries yet</source>
        <translation type="vanished">Aún no hay entradas de gastos</translation>
    </message>
    <message>
        <source>Delete entry</source>
        <translation type="vanished">Eliminar entrada</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="386"/>
        <source>Delete &quot;%1&quot;?</source>
        <translation>¿Eliminar «%1»?</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="393"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/pages/EntriesPage.qml" line="400"/>
        <source>Delete</source>
        <translation>Eliminar</translation>
    </message>
</context>
<context>
    <name>EntriesViewModel</name>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="348"/>
        <source>Every day</source>
        <translation>Cada día</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="349"/>
        <source>Monthly on the %1</source>
        <translation>Mensual el %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="350"/>
        <source>Yearly on %1 %2</source>
        <translation>Anual el %1 %2</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="351"/>
        <source>Once on %1 %2 %3</source>
        <translation>Una vez el %1 %2 %3</translation>
    </message>
</context>
<context>
    <name>EntryForm</name>
    <message>
        <source>New entry</source>
        <translation type="vanished">Nueva entrada</translation>
    </message>
    <message>
        <source>Edit entry</source>
        <translation type="vanished">Editar entrada</translation>
    </message>
    <message>
        <source>Name</source>
        <translation type="vanished">Nombre</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="37"/>
        <source>Description</source>
        <translation>Descripción</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="47"/>
        <source>e.g. Salary</source>
        <translation>p. ej. Salario</translation>
    </message>
    <message>
        <source>Entry name</source>
        <translation type="vanished">Nombre de la entrada</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="48"/>
        <source>Cash flow name</source>
        <translation>Nombre del flujo de caja</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="66"/>
        <source>Type</source>
        <translation>Tipo</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="82"/>
        <location filename="../qml/components/EntryForm.qml" line="85"/>
        <source>Income</source>
        <translation>Ingresos</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="90"/>
        <location filename="../qml/components/EntryForm.qml" line="93"/>
        <source>Expense</source>
        <translation>Gasto</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="107"/>
        <source>Date pattern</source>
        <translation>Patrón de fecha</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="138"/>
        <location filename="../qml/components/EntryForm.qml" line="150"/>
        <source>Amount</source>
        <translation>Importe</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="148"/>
        <source>0.00</source>
        <translation>0.00</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="171"/>
        <location filename="../qml/components/EntryForm.qml" line="182"/>
        <source>Currency</source>
        <translation>Moneda</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="196"/>
        <source>Category (optional)</source>
        <translation>Categoría (opcional)</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryForm.qml" line="206"/>
        <location filename="../qml/components/EntryForm.qml" line="207"/>
        <source>Category</source>
        <translation>Categoría</translation>
    </message>
    <message>
        <source>Cancel</source>
        <translation type="vanished">Cancelar</translation>
    </message>
    <message>
        <source>Save</source>
        <translation type="vanished">Guardar</translation>
    </message>
    <message>
        <source>Save entry</source>
        <translation type="vanished">Guardar entrada</translation>
    </message>
</context>
<context>
    <name>EntryFormDrawer</name>
    <message>
        <source>Add Entry</source>
        <translation type="vanished">Añadir entrada</translation>
    </message>
    <message>
        <source>Edit Entry</source>
        <translation type="vanished">Editar entrada</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryFormDrawer.qml" line="98"/>
        <source>Add cash flow</source>
        <translation>Añadir flujo de caja</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryFormDrawer.qml" line="98"/>
        <source>Edit cash flow</source>
        <translation>Editar flujo de caja</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryFormDrawer.qml" line="107"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryFormDrawer.qml" line="131"/>
        <source>Save</source>
        <translation>Guardar</translation>
    </message>
    <message>
        <location filename="../qml/components/EntryFormDrawer.qml" line="135"/>
        <source>Save cash flow</source>
        <translation>Guardar flujo de caja</translation>
    </message>
    <message>
        <source>Save entry</source>
        <translation type="vanished">Guardar entrada</translation>
    </message>
</context>
<context>
    <name>ExpenseAnalyticsPanel</name>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="16"/>
        <source>Overview</source>
        <translation>Resumen</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="32"/>
        <source>Top categories</source>
        <translation>Principales categorías</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="35"/>
        <source>No category spending in this period.</source>
        <translation>No hay gastos por categoría en este período.</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="40"/>
        <source>Top places</source>
        <translation>Principales lugares</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="43"/>
        <source>No place spending in this period.</source>
        <translation>No hay gastos por lugar en este período.</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="48"/>
        <source>Top names</source>
        <translation>Principales nombres</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseAnalyticsPanel.qml" line="51"/>
        <source>No name spending in this period.</source>
        <translation>No hay gastos por nombre en este período.</translation>
    </message>
</context>
<context>
    <name>ExpenseBucketBarChart</name>
    <message>
        <location filename="../qml/components/ExpenseBucketBarChart.qml" line="16"/>
        <source>No spending in this period.</source>
        <translation>No hay gastos en este período.</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseBucketBarChart.qml" line="44"/>
        <source>Other</source>
        <translation>Otros</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseBucketBarChart.qml" line="217"/>
        <source>Amount (%1)</source>
        <translation>Importe (%1)</translation>
    </message>
</context>
<context>
    <name>ExpenseFilterBar</name>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="93"/>
        <source>Search name, category, place, or note</source>
        <translation>Buscar nombre, categoría, lugar o nota</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="94"/>
        <source>Search expenses</source>
        <translation>Buscar gastos</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="111"/>
        <source>This month</source>
        <translation>Este mes</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="112"/>
        <source>Last 30 days</source>
        <translation>Últimos 30 días</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="113"/>
        <source>Year to date</source>
        <translation>Año en curso</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="114"/>
        <source>Custom</source>
        <translation>Personalizado</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="144"/>
        <source>From</source>
        <translation type="unfinished">De</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="162"/>
        <source>To</source>
        <translation type="unfinished">A</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="176"/>
        <source>Apply</source>
        <translation>Aplicar</translation>
    </message>
    <message>
        <location filename="../qml/components/ExpenseFilterBar.qml" line="184"/>
        <source>Clear filters</source>
        <translation>Borrar filtros</translation>
    </message>
</context>
<context>
    <name>ForecastTemplates</name>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="352"/>
        <source>SaaS startup</source>
        <translation>Startup SaaS</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="353"/>
        <source>Monthly recurring revenue, cloud costs, and payroll for an early-stage SaaS company.</source>
        <translation>Ingresos recurrentes mensuales, costes en la nube y nómina para una empresa SaaS en fase inicial.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="357"/>
        <source>Consulting firm</source>
        <translation>Empresa de consultoría</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="358"/>
        <source>Client retainers, contractor costs, and operating expenses for a small professional services firm.</source>
        <translation>Cuotas de clientes, costes de contratistas y gastos operativos para una pequeña empresa de servicios profesionales.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="363"/>
        <source>Retail shop</source>
        <translation>Tienda minorista</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/user_messages.py" line="364"/>
        <source>Point-of-sale revenue, rent, inventory COGS, and seasonal patterns for a brick-and-mortar retail store.</source>
        <translation>Ingresos en punto de venta, alquiler, coste de inventario y patrones estacionales para una tienda física.</translation>
    </message>
</context>
<context>
    <name>ImportDialog</name>
    <message>
        <source>Import entries</source>
        <translation type="vanished">Importar entradas</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="27"/>
        <location filename="../qml/components/ImportDialog.qml" line="39"/>
        <source>Name</source>
        <translation>Nombre</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="28"/>
        <location filename="../qml/components/ImportDialog.qml" line="40"/>
        <source>Date pattern</source>
        <translation>Patrón de fecha</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="29"/>
        <location filename="../qml/components/ImportDialog.qml" line="41"/>
        <source>Amount</source>
        <translation>Importe</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="30"/>
        <location filename="../qml/components/ImportDialog.qml" line="42"/>
        <source>Currency</source>
        <translation>Moneda</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="31"/>
        <location filename="../qml/components/ImportDialog.qml" line="43"/>
        <source>Type</source>
        <translation>Tipo</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="35"/>
        <location filename="../qml/components/ImportDialog.qml" line="44"/>
        <source>Category</source>
        <translation>Categoría</translation>
    </message>
    <message>
        <source>Imported %1 entries with %2 errors.</source>
        <translation type="vanished">Se importaron %1 entradas con %2 error(es).</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="171"/>
        <source>Imported %1 cash flows with %2 errors.</source>
        <translation>Se importaron %1 flujos de caja con %2 errores.</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="186"/>
        <source>Import cash flows</source>
        <translation>Importar flujos de caja</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="197"/>
        <source>Select file to import</source>
        <translation>Seleccionar archivo para importar</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="198"/>
        <source>Spreadsheets (*.csv *.xlsx)</source>
        <translation>Hojas de cálculo (*.csv *.xlsx)</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="248"/>
        <source>Choose a CSV or Excel file to import.</source>
        <translation>Elija un archivo CSV o Excel para importar.</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="253"/>
        <source>Browse…</source>
        <translation>Examinar…</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="273"/>
        <source>Map each required field to a column in your file.</source>
        <translation>Asigne cada campo obligatorio a una columna de su archivo.</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="296"/>
        <source>Select column…</source>
        <translation>Seleccionar columna…</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="305"/>
        <source>Optional fields</source>
        <translation>Campos opcionales</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="328"/>
        <source>Not mapped</source>
        <translation>Sin asignar</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="341"/>
        <source>Preview of the first 5 rows with your column mapping applied.</source>
        <translation>Vista previa de las primeras 5 filas con su asignación de columnas.</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="437"/>
        <source>No preview rows available.</source>
        <translation>No hay filas de vista previa disponibles.</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="450"/>
        <source>Ready to import. Review the summary below and click Import.</source>
        <translation>Listo para importar. Revise el resumen y haga clic en Importar.</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="472"/>
        <source>Import</source>
        <translation>Importar</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="520"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="526"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="533"/>
        <source>Next</source>
        <translation>Siguiente</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="558"/>
        <source>Done</source>
        <translation>Hecho</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="608"/>
        <source>Hide import errors</source>
        <translation>Ocultar errores de importación</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="609"/>
        <source>Show import errors (%1)</source>
        <translation>Mostrar errores de importación (%1)</translation>
    </message>
    <message>
        <location filename="../qml/components/ImportDialog.qml" line="620"/>
        <source>Row %1: %2</source>
        <translation>Fila %1: %2</translation>
    </message>
</context>
<context>
    <name>LabelAutocompleteField</name>
    <message>
        <location filename="../qml/components/LabelAutocompleteField.qml" line="59"/>
        <source>optional</source>
        <translation>opcional</translation>
    </message>
    <message>
        <location filename="../qml/components/LabelAutocompleteField.qml" line="76"/>
        <source>Low confidence</source>
        <translation>Baja confianza</translation>
    </message>
</context>
<context>
    <name>Methodology</name>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="133"/>
        <source>Methodology</source>
        <translation type="unfinished">Metodología</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="134"/>
        <source>Methodology version: %1</source>
        <translation>Versión de la metodología: %1</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="135"/>
        <source>This page explains how Cash Flow Planner computes projections, detects cash shortfalls, and handles currencies and scenarios.</source>
        <translation type="unfinished">Esta página explica cómo Cash Flow Planner calcula proyecciones, detecta faltantes de efectivo y gestiona divisas y escenarios.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="140"/>
        <source>Cash shortfall detection</source>
        <translation type="unfinished">Detección de faltante de efectivo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="141"/>
        <source>Daily running balance</source>
        <translation type="unfinished">Saldo corriente diario</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="142"/>
        <source>Each forecast run starts from your opening cash balance. For every calendar day in the projection range, the app sums income and expenses scheduled on that day, then computes:

closing balance = previous closing balance + income − expenses

The previous day’s closing balance becomes the next day’s starting point, producing a day-by-day running balance.</source>
        <translation type="unfinished">Cada ejecución de previsión parte de su saldo de efectivo inicial. Para cada día del calendario en el rango de proyección, la aplicación suma los ingresos y gastos programados ese día y calcula:

saldo de cierre = saldo de cierre anterior + ingresos − gastos

El saldo de cierre del día anterior se convierte en el punto de partida del día siguiente, produciendo un saldo corriente día a día.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="151"/>
        <source>First cash shortfall</source>
        <translation type="unfinished">Primer faltante de efectivo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="152"/>
        <source>A cash shortfall is reported on the first day whose closing balance falls below zero. When that happens, the app records the date and highlights the expense cash flow that contributed to the shortfall on that day (or the first scheduled event if no expense occurred). Later shortfalls are not reported separately—only the earliest one is shown.</source>
        <translation type="unfinished">Se informa un faltante de efectivo el primer día cuyo saldo de cierre cae por debajo de cero. La aplicación registra la fecha y resalta el flujo de caja de gasto que contribuyó al faltante ese día (o el primer evento programado si no hubo gastos). Los faltantes posteriores no se informan por separado; solo se muestra el más temprano.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="161"/>
        <source>Date patterns</source>
        <translation type="unfinished">Patrones de fecha</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="162"/>
        <source>How cash flows are scheduled</source>
        <translation type="unfinished">Programación de flujos de caja</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="163"/>
        <source>Each cash flow uses a compact date pattern. The pattern is expanded into individual dated events across the forecast range before the running balance is calculated. Patterns are validated as you type when editing a cash flow.</source>
        <translation type="unfinished">Cada flujo de caja usa un patrón de fecha compacto. El patrón se expande en eventos fechados individuales en el rango de previsión antes de calcular el saldo corriente. Los patrones se validan mientras escribe al editar un flujo de caja.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="170"/>
        <source>Pattern examples</source>
        <translation type="unfinished">Ejemplos de patrones</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="171"/>
        <source>Every day (daily)</source>
        <translation type="unfinished">Todos los días (diario)</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="172"/>
        <source>Monthly on the 10th</source>
        <translation type="unfinished">Mensual el día 10</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="173"/>
        <source>Yearly on 15 March</source>
        <translation type="unfinished">Anual el 15 de marzo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="174"/>
        <source>One-time on 15 March 2026</source>
        <translation type="unfinished">Único el 15 de marzo de 2026</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="175"/>
        <source>Multi-currency normalization</source>
        <translation type="unfinished">Normalización multidivisa</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="176"/>
        <source>Base currency conversion</source>
        <translation type="unfinished">Conversión a divisa base</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="177"/>
        <source>Cash flows may be entered in different currencies. Before amounts are summed, each event is converted to the forecast’s base currency using stored exchange rates. Direct rates (e.g. EUR → USD) are used when available; otherwise an inverse rate is applied.</source>
        <translation type="unfinished">Los flujos de caja pueden introducirse en distintas divisas. Antes de sumar los importes, cada evento se convierte a la divisa base de la previsión usando tipos de cambio almacenados. Se usan tipos directos (p. ej. EUR → USD) cuando están disponibles; de lo contrario, se aplica un tipo inverso.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="184"/>
        <source>Exchange rate sources</source>
        <translation type="unfinished">Fuentes de tipos de cambio</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="185"/>
        <source>Rates are managed globally in Settings. You can enter rates manually or enable live fetching to download current rates from an external provider when network access is available. A forecast run fails with a clear error if a required conversion rate is missing.</source>
        <translation type="unfinished">Los tipos se gestionan globalmente en Ajustes. Puede introducirlos manualmente o activar la descarga en vivo de tipos actuales de un proveedor externo cuando haya acceso a la red. Una ejecución de previsión falla con un error claro si falta un tipo de conversión necesario.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="192"/>
        <source>Scenario planning</source>
        <translation type="unfinished">Planificación de escenarios</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="193"/>
        <source>Temporary overrides</source>
        <translation type="unfinished">Sustituciones temporales</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/methodology_content.py" line="194"/>
        <source>Scenario mode lets you adjust cash-flow amounts or deactivate line items to explore alternatives. Overrides are applied only for the current forecast run—they are not saved to your forecast and do not change stored cash flows. Clear overrides or leave the scenario panel to return to the saved baseline.</source>
        <translation type="unfinished">El modo escenario le permite ajustar importes de flujos de caja o desactivar partidas para explorar alternativas. Las sustituciones solo se aplican a la ejecución de previsión actual: no se guardan en su previsión ni cambian los flujos de caja almacenados. Borre las sustituciones o salga del panel de escenario para volver a la base guardada.</translation>
    </message>
</context>
<context>
    <name>MethodologyPage</name>
    <message>
        <location filename="../qml/pages/MethodologyPage.qml" line="13"/>
        <location filename="../qml/pages/MethodologyPage.qml" line="41"/>
        <source>Methodology</source>
        <translation type="unfinished">Metodología</translation>
    </message>
    <message>
        <location filename="../qml/pages/MethodologyPage.qml" line="31"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <source>This page explains how Cash Flow Planner computes projections, detects cash shortfalls, and handles currencies and scenarios.</source>
        <translation type="vanished">Esta página explica cómo Cash Flow Planner calcula proyecciones, detecta faltantes de efectivo y gestiona divisas y escenarios.</translation>
    </message>
    <message>
        <source>Cash shortfall detection</source>
        <translation type="vanished">Detección de faltante de efectivo</translation>
    </message>
    <message>
        <source>Daily running balance</source>
        <translation type="vanished">Saldo corriente diario</translation>
    </message>
    <message>
        <source>Each forecast run starts from your opening cash balance. For every calendar day in the projection range, the app sums income and expenses scheduled on that day, then computes:

closing balance = previous closing balance + income − expenses

The previous day’s closing balance becomes the next day’s starting point, producing a day-by-day running balance.</source>
        <translation type="vanished">Cada ejecución de previsión parte de su saldo de efectivo inicial. Para cada día del calendario en el rango de proyección, la aplicación suma los ingresos y gastos programados ese día y calcula:

saldo de cierre = saldo de cierre anterior + ingresos − gastos

El saldo de cierre del día anterior se convierte en el punto de partida del día siguiente, produciendo un saldo corriente día a día.</translation>
    </message>
    <message>
        <source>First cash shortfall</source>
        <translation type="vanished">Primer faltante de efectivo</translation>
    </message>
    <message>
        <source>A cash shortfall is reported on the first day whose closing balance falls below zero. When that happens, the app records the date and highlights the expense cash flow that contributed to the shortfall on that day (or the first scheduled event if no expense occurred). Later shortfalls are not reported separately—only the earliest one is shown.</source>
        <translation type="vanished">Se informa un faltante de efectivo el primer día cuyo saldo de cierre cae por debajo de cero. La aplicación registra la fecha y resalta el flujo de caja de gasto que contribuyó al faltante ese día (o el primer evento programado si no hubo gastos). Los faltantes posteriores no se informan por separado; solo se muestra el más temprano.</translation>
    </message>
    <message>
        <source>Date patterns</source>
        <translation type="vanished">Patrones de fecha</translation>
    </message>
    <message>
        <source>How cash flows are scheduled</source>
        <translation type="vanished">Programación de flujos de caja</translation>
    </message>
    <message>
        <source>Each cash flow uses a compact date pattern. The pattern is expanded into individual dated events across the forecast range before the running balance is calculated. Patterns are validated as you type when editing a cash flow.</source>
        <translation type="vanished">Cada flujo de caja usa un patrón de fecha compacto. El patrón se expande en eventos fechados individuales en el rango de previsión antes de calcular el saldo corriente. Los patrones se validan mientras escribe al editar un flujo de caja.</translation>
    </message>
    <message>
        <source>Pattern examples</source>
        <translation type="vanished">Ejemplos de patrones</translation>
    </message>
    <message>
        <source>Every day (daily)</source>
        <translation type="vanished">Todos los días (diario)</translation>
    </message>
    <message>
        <source>Monthly on the 10th</source>
        <translation type="vanished">Mensual el día 10</translation>
    </message>
    <message>
        <source>Yearly on 15 March</source>
        <translation type="vanished">Anual el 15 de marzo</translation>
    </message>
    <message>
        <source>One-time on 15 March 2026</source>
        <translation type="vanished">Único el 15 de marzo de 2026</translation>
    </message>
    <message>
        <source>Multi-currency normalization</source>
        <translation type="vanished">Normalización multidivisa</translation>
    </message>
    <message>
        <source>Base currency conversion</source>
        <translation type="vanished">Conversión a divisa base</translation>
    </message>
    <message>
        <source>Cash flows may be entered in different currencies. Before amounts are summed, each event is converted to the forecast’s base currency using stored exchange rates. Direct rates (e.g. EUR → USD) are used when available; otherwise an inverse rate is applied.</source>
        <translation type="vanished">Los flujos de caja pueden introducirse en distintas divisas. Antes de sumar los importes, cada evento se convierte a la divisa base de la previsión usando tipos de cambio almacenados. Se usan tipos directos (p. ej. EUR → USD) cuando están disponibles; de lo contrario, se aplica un tipo inverso.</translation>
    </message>
    <message>
        <source>Exchange rate sources</source>
        <translation type="vanished">Fuentes de tipos de cambio</translation>
    </message>
    <message>
        <source>Rates are managed globally in Settings. You can enter rates manually or enable live fetching to download current rates from an external provider when network access is available. A forecast run fails with a clear error if a required conversion rate is missing.</source>
        <translation type="vanished">Los tipos se gestionan globalmente en Ajustes. Puede introducirlos manualmente o activar la descarga en vivo de tipos actuales de un proveedor externo cuando haya acceso a la red. Una ejecución de previsión falla con un error claro si falta un tipo de conversión necesario.</translation>
    </message>
    <message>
        <source>Scenario planning</source>
        <translation type="vanished">Planificación de escenarios</translation>
    </message>
    <message>
        <source>Temporary overrides</source>
        <translation type="vanished">Sustituciones temporales</translation>
    </message>
    <message>
        <source>Scenario mode lets you adjust cash-flow amounts or deactivate line items to explore alternatives. Overrides are applied only for the current forecast run—they are not saved to your forecast and do not change stored cash flows. Clear overrides or leave the scenario panel to return to the saved baseline.</source>
        <translation type="vanished">El modo escenario le permite ajustar importes de flujos de caja o desactivar partidas para explorar alternativas. Las sustituciones solo se aplican a la ejecución de previsión actual: no se guardan en su previsión ni cambian los flujos de caja almacenados. Borre las sustituciones o salga del panel de escenario para volver a la base guardada.</translation>
    </message>
</context>
<context>
    <name>MonthlyTableView</name>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="49"/>
        <source>Month</source>
        <translation>Mes</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="50"/>
        <source>Income</source>
        <translation>Ingresos</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="51"/>
        <source>Expense</source>
        <translation>Gasto</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="52"/>
        <source>Net</source>
        <translation>Neto</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="53"/>
        <source>Balance</source>
        <translation>Saldo</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="75"/>
        <source>%1 %2</source>
        <translation>%1 %2</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="80"/>
        <source>Jan</source>
        <translation>ene.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="80"/>
        <source>Feb</source>
        <translation>feb.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="80"/>
        <source>Mar</source>
        <translation>mar.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="80"/>
        <source>Apr</source>
        <translation>abr.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="81"/>
        <source>May</source>
        <translation>may.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="81"/>
        <source>Jun</source>
        <translation>jun.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="81"/>
        <source>Jul</source>
        <translation>jul.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="81"/>
        <source>Aug</source>
        <translation>ago.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="82"/>
        <source>Sep</source>
        <translation>sep.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="82"/>
        <source>Oct</source>
        <translation>oct.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="82"/>
        <source>Nov</source>
        <translation>nov.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="82"/>
        <source>Dec</source>
        <translation>dic.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="179"/>
        <source>Monthly summary</source>
        <translation>Resumen mensual</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="187"/>
        <source>Run a forecast to see monthly snapshots.</source>
        <translation>Ejecute una previsión para ver instantáneas mensuales.</translation>
    </message>
    <message>
        <location filename="../qml/components/MonthlyTableView.qml" line="327"/>
        <source>Cash shortfall warning</source>
        <translation>Aviso de déficit de tesorería</translation>
    </message>
    <message>
        <source>Run a simulation to see monthly snapshots.</source>
        <translation type="vanished">Ejecute una simulación para ver instantáneas mensuales.</translation>
    </message>
    <message>
        <source>Deficit warning</source>
        <translation type="vanished">Advertencia de déficit</translation>
    </message>
</context>
<context>
    <name>PdfExport</name>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="139"/>
        <source>%1 — Projection report</source>
        <translation>%1 — Informe de proyección</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="140"/>
        <source>Forecast horizon:</source>
        <translation>Horizonte de previsión:</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="141"/>
        <source>Exported at:</source>
        <translation>Exportado el:</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="142"/>
        <source>App version:</source>
        <translation>Versión de la aplicación:</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="143"/>
        <source>Methodology version:</source>
        <translation>Versión de la metodología:</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="144"/>
        <source>Display currency:</source>
        <translation>Moneda de visualización:</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="145"/>
        <source>Monthly cash bridge</source>
        <translation>Puente de caja mensual</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="146"/>
        <source>Balance chart</source>
        <translation>Gráfico de saldo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="147"/>
        <source>FX footnotes</source>
        <translation>Notas de cambio</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="148"/>
        <source>Scenario comparison</source>
        <translation>Comparación de escenarios</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="149"/>
        <source>Active overrides:</source>
        <translation>Sustituciones activas:</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="150"/>
        <source>All amounts in this report are normalized to %1 using the rates above.</source>
        <translation>Todos los importes de este informe se normalizan a %1 usando los tipos anteriores.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="154"/>
        <source>Year</source>
        <translation>Año</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="155"/>
        <source>Month</source>
        <translation>Mes</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="156"/>
        <source>Opening</source>
        <translation>Apertura</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="157"/>
        <source>Inflows</source>
        <translation>Entradas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="158"/>
        <source>Outflows</source>
        <translation>Salidas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="159"/>
        <source>Net</source>
        <translation>Neto</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="160"/>
        <source>Closing</source>
        <translation>Cierre</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="161"/>
        <source>Metric</source>
        <translation>Indicador</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="162"/>
        <source>Baseline</source>
        <translation>Línea base</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="163"/>
        <source>Scenario</source>
        <translation>Escenario</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="164"/>
        <source>Delta</source>
        <translation>Diferencia</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="165"/>
        <source>From</source>
        <translation>De</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="166"/>
        <source>To</source>
        <translation>A</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="167"/>
        <source>Rate</source>
        <translation>Tipo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="168"/>
        <source>Updated at</source>
        <translation>Actualizado el</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="169"/>
        <source>Final balance</source>
        <translation>Saldo final</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="170"/>
        <source>First cash shortfall date</source>
        <translation>Fecha del primer déficit de caja</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="171"/>
        <source>Total inflows</source>
        <translation>Total de entradas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="172"/>
        <source>Total outflows</source>
        <translation>Total de salidas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="173"/>
        <source>None</source>
        <translation>Ninguno</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="174"/>
        <source>Only in scenario</source>
        <translation>Solo en escenario</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="175"/>
        <source>Only in baseline</source>
        <translation>Solo en línea base</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="176"/>
        <source>+%1 days</source>
        <translation>+%1 días</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="177"/>
        <source>%1 days</source>
        <translation>%1 días</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/pdf_messages.py" line="178"/>
        <source>—</source>
        <translation>—</translation>
    </message>
</context>
<context>
    <name>PlanDetailLayout</name>
    <message>
        <source>Plan</source>
        <translation type="vanished">Plan</translation>
    </message>
    <message>
        <source>Back to plans</source>
        <translation type="vanished">Volver a planes</translation>
    </message>
    <message>
        <source>Entries</source>
        <translation type="vanished">Entradas</translation>
    </message>
    <message>
        <source>Entries tab</source>
        <translation type="vanished">Pestaña de entradas</translation>
    </message>
    <message>
        <source>Simulation</source>
        <translation type="vanished">Simulación</translation>
    </message>
    <message>
        <source>Simulation tab</source>
        <translation type="vanished">Pestaña de simulación</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanDetailLayout.qml" line="17"/>
        <source>Change history</source>
        <translation>Historial de cambios</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanDetailLayout.qml" line="20"/>
        <source>Forecast</source>
        <translation>Previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanDetailLayout.qml" line="44"/>
        <source>Back to forecasts</source>
        <translation>Volver a previsiones</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanDetailLayout.qml" line="130"/>
        <source>tab</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanDetailLayout.qml" line="17"/>
        <source>Cash flows</source>
        <translation>Flujos de caja</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanDetailLayout.qml" line="17"/>
        <source>Projection</source>
        <translation>Proyección</translation>
    </message>
    <message>
        <source>Cash flows tab</source>
        <translation type="vanished">Pestaña Flujos de caja</translation>
    </message>
    <message>
        <source>Projection tab</source>
        <translation type="vanished">Pestaña Proyección</translation>
    </message>
</context>
<context>
    <name>PlanImportDialog</name>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="40"/>
        <source>%1 → USD: %2</source>
        <translation>%1 → USD: %2</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="59"/>
        <source>Import forecast</source>
        <translation>Importar previsión</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="70"/>
        <source>Select forecast file</source>
        <translation>Seleccionar archivo de previsión</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="71"/>
        <source>Forecast files (*.ftplan)</source>
        <translation>Archivos de previsión (*.ftplan)</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="112"/>
        <source>Choose a .ftplan file to import as a new forecast.</source>
        <translation>Elija un archivo .ftplan para importar como nueva previsión.</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="117"/>
        <source>Browse…</source>
        <translation>Examinar…</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="137"/>
        <source>Review the forecast summary below, resolve any rate conflicts, then import.</source>
        <translation>Revise el resumen de la previsión, resuelva conflictos de tipos de cambio e importe.</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="156"/>
        <source>Forecast name</source>
        <translation>Nombre de la previsión</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="161"/>
        <source>Cash flows</source>
        <translation>Flujos de caja</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="166"/>
        <source>Currencies</source>
        <translation>Divisas</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="175"/>
        <source>New rates</source>
        <translation>Tipos nuevos</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="204"/>
        <source>Rate conflicts</source>
        <translation>Conflictos de tipos</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="210"/>
        <source>Keep all mine</source>
        <translation>Mantener todos los míos</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="216"/>
        <source>Use all from file</source>
        <translation>Usar todos del archivo</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="246"/>
        <source>Importing…</source>
        <translation>Importando…</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="246"/>
        <source>Import</source>
        <translation>Importar</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="287"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="293"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="300"/>
        <source>Next</source>
        <translation>Siguiente</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="331"/>
        <source>Forecast imported successfully</source>
        <translation>Previsión importada correctamente</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="383"/>
        <source>%1 → USD</source>
        <translation>%1 → USD</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="394"/>
        <source>Local: %1</source>
        <translation>Local: %1</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="402"/>
        <source>File: %1</source>
        <translation>Archivo: %1</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="419"/>
        <source>Keep mine</source>
        <translation>Mantener el mío</translation>
    </message>
    <message>
        <location filename="../qml/components/PlanImportDialog.qml" line="427"/>
        <source>Use file&apos;s</source>
        <translation>Usar del archivo</translation>
    </message>
</context>
<context>
    <name>PlanListPage</name>
    <message>
        <source>Plans</source>
        <translation type="vanished">Planes</translation>
    </message>
    <message>
        <source>%1 %2</source>
        <translation type="vanished">%1 %2</translation>
    </message>
    <message>
        <source>New plan</source>
        <translation type="vanished">Nuevo plan</translation>
    </message>
    <message>
        <source>Create new plan</source>
        <translation type="vanished">Crear nuevo plan</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="132"/>
        <source>Created: %1</source>
        <translation>Creado: %1</translation>
    </message>
    <message>
        <source>Delete plan</source>
        <translation type="vanished">Eliminar plan</translation>
    </message>
    <message>
        <source>No plans yet</source>
        <translation type="vanished">Aún no hay planes</translation>
    </message>
    <message>
        <source>Create your first plan to start tracking income, expenses, and forecasts.</source>
        <translation type="vanished">Cree su primer plan para seguir ingresos, gastos y previsiones.</translation>
    </message>
    <message>
        <source>Create your first plan</source>
        <translation type="vanished">Crear su primer plan</translation>
    </message>
    <message>
        <source>No financial plans yet</source>
        <translation type="vanished">Aún no hay planes financieros</translation>
    </message>
    <message>
        <source>Create your first plan to start tracking</source>
        <translation type="vanished">Crea tu primer plan para empezar a hacer seguimiento</translation>
    </message>
    <message>
        <source>+ New Plan</source>
        <translation type="vanished">+ Nuevo plan</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="510"/>
        <location filename="../qml/pages/PlanListPage.qml" line="606"/>
        <source>My budget 2026</source>
        <translation>Mi presupuesto 2026</translation>
    </message>
    <message>
        <source>Plan name</source>
        <translation type="vanished">Nombre del plan</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="524"/>
        <location filename="../qml/pages/PlanListPage.qml" line="534"/>
        <source>Base currency</source>
        <translation>Moneda base</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="517"/>
        <location filename="../qml/pages/PlanListPage.qml" line="519"/>
        <location filename="../qml/pages/PlanListPage.qml" line="613"/>
        <location filename="../qml/pages/PlanListPage.qml" line="615"/>
        <source>Initial balance</source>
        <translation>Saldo inicial</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="14"/>
        <location filename="../qml/pages/PlanListPage.qml" line="36"/>
        <source>Forecasts</source>
        <translation>Previsiones</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="43"/>
        <location filename="../qml/pages/PlanListPage.qml" line="46"/>
        <location filename="../qml/pages/PlanListPage.qml" line="340"/>
        <location filename="../qml/pages/PlanListPage.qml" line="343"/>
        <source>Import forecast</source>
        <translation>Importar previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="51"/>
        <location filename="../qml/pages/PlanListPage.qml" line="332"/>
        <source>+ New forecast</source>
        <translation>+ Nueva previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="52"/>
        <location filename="../qml/pages/PlanListPage.qml" line="333"/>
        <source>Create new forecast</source>
        <translation>Crear previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="248"/>
        <location filename="../qml/pages/PlanListPage.qml" line="584"/>
        <source>Edit forecast</source>
        <translation>Editar previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="262"/>
        <location filename="../qml/pages/PlanListPage.qml" line="425"/>
        <source>Export forecast</source>
        <translation>Exportar previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="273"/>
        <location filename="../qml/pages/PlanListPage.qml" line="666"/>
        <source>Delete forecast</source>
        <translation>Eliminar previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="314"/>
        <source>No forecasts yet</source>
        <translation>Aún no hay previsiones</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="323"/>
        <source>Create your first forecast to start forecasting</source>
        <translation>Cree su primera previsión para empezar</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="382"/>
        <source>Start with a blank forecast or use a template with typical cash flows.</source>
        <translation>Empiece con una previsión en blanco o use una plantilla con flujos de caja típicos.</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="390"/>
        <source>Blank forecast</source>
        <translation>Previsión en blanco</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="393"/>
        <source>Create blank forecast</source>
        <translation>Crear previsión en blanco</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="402"/>
        <source>From template</source>
        <translation>Desde plantilla</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="404"/>
        <source>Create forecast from template</source>
        <translation>Crear previsión desde plantilla</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="427"/>
        <source>Forecast files (*.ftplan)</source>
        <translation>Archivos de previsión (*.ftplan)</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="461"/>
        <source>Forecast exported successfully</source>
        <translation>Previsión exportada correctamente</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="367"/>
        <location filename="../qml/pages/PlanListPage.qml" line="486"/>
        <source>New forecast</source>
        <translation>Nueva previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="511"/>
        <location filename="../qml/pages/PlanListPage.qml" line="607"/>
        <source>Forecast name</source>
        <translation>Nombre de la previsión</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="414"/>
        <location filename="../qml/pages/PlanListPage.qml" line="540"/>
        <location filename="../qml/pages/PlanListPage.qml" line="621"/>
        <location filename="../qml/pages/PlanListPage.qml" line="688"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="547"/>
        <source>Create</source>
        <translation>Crear</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="628"/>
        <source>Save</source>
        <translation>Guardar</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="680"/>
        <source>Delete &quot;%1&quot;? All cash flows and projection data for this forecast will be removed.</source>
        <translation>¿Eliminar «%1»? Se eliminarán todos los flujos de caja y los datos de proyección de esta previsión.</translation>
    </message>
    <message>
        <source>Delete &quot;%1&quot;? All entries and simulation data for this plan will be removed.</source>
        <translation type="vanished">¿Eliminar «%1»? Se eliminarán todas las entradas y datos de simulación de este plan.</translation>
    </message>
    <message>
        <location filename="../qml/pages/PlanListPage.qml" line="695"/>
        <source>Delete</source>
        <translation>Eliminar</translation>
    </message>
</context>
<context>
    <name>RecordedExpenseFormDrawer</name>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="123"/>
        <source>Add recorded expense</source>
        <translation>Añadir gasto registrado</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="124"/>
        <source>Edit recorded expense</source>
        <translation>Editar gasto registrado</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="132"/>
        <source>Scan</source>
        <translation>Escanear</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="135"/>
        <source>Scan receipt</source>
        <translation>Escanear recibo</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="142"/>
        <source>Close</source>
        <translation type="unfinished">Cerrar</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="285"/>
        <source>Reading receipt…</source>
        <translation>Leyendo el recibo…</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="286"/>
        <source>Review suggested fields, then save.</source>
        <translation>Revise los campos sugeridos y luego guarde.</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="294"/>
        <source>You can edit any field or enter the expense manually.</source>
        <translation>Puede editar cualquier campo o introducir el gasto manualmente.</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="303"/>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="306"/>
        <source>Enter manually</source>
        <translation>Introducir manualmente</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="327"/>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="356"/>
        <source>Amount</source>
        <translation type="unfinished">Importe</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="344"/>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="411"/>
        <source>Low confidence</source>
        <translation>Baja confianza</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="354"/>
        <source>0.00</source>
        <translation type="unfinished">0.00</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="369"/>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="379"/>
        <source>Currency</source>
        <translation type="unfinished">Moneda</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="394"/>
        <source>Date</source>
        <translation type="unfinished">Fecha</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="428"/>
        <source>Name</source>
        <translation type="unfinished">Nombre</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="429"/>
        <source>e.g. Groceries</source>
        <translation>p. ej. Comestibles</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="441"/>
        <source>Category</source>
        <translation type="unfinished">Categoría</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="442"/>
        <source>e.g. Food</source>
        <translation>p. ej. Alimentación</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="451"/>
        <source>Place</source>
        <translation>Lugar</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="452"/>
        <source>e.g. Whole Foods</source>
        <translation>p. ej. Whole Foods</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="464"/>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="474"/>
        <source>Note</source>
        <translation>Nota</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="464"/>
        <source>optional</source>
        <translation>opcional</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="473"/>
        <source>Add a note</source>
        <translation>Agregar una nota</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="484"/>
        <source>Save</source>
        <translation type="unfinished">Guardar</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="488"/>
        <source>Save recorded expense</source>
        <translation>Guardar gasto registrado</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="501"/>
        <source>Choose a receipt image</source>
        <translation>Elegir una imagen del recibo</translation>
    </message>
    <message>
        <location filename="../qml/components/RecordedExpenseFormDrawer.qml" line="502"/>
        <source>Images (*.jpg *.jpeg *.png *.webp *.heic)</source>
        <translation>Imágenes (*.jpg *.jpeg *.png *.webp *.heic)</translation>
    </message>
</context>
<context>
    <name>RecordedExpensesPage</name>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="13"/>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="47"/>
        <source>Spending</source>
        <translation>Gastos</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="144"/>
        <source>Edit %1</source>
        <translation type="unfinished">Editar %1</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="153"/>
        <source>Delete %1</source>
        <translation type="unfinished">Eliminar %1</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="208"/>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="292"/>
        <source>No matching expenses</source>
        <translation>No hay gastos coincidentes</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="222"/>
        <source>Try a different search term or clear filters.</source>
        <translation>Pruebe otro término de búsqueda o borre los filtros.</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="265"/>
        <source>No recorded expenses yet</source>
        <translation>Aún no hay gastos registrados</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="273"/>
        <source>Add your first recorded expense using the + button</source>
        <translation>Añada su primer gasto registrado con el botón +</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="300"/>
        <source>Try adjusting your search or date range, or clear filters.</source>
        <translation>Ajuste la búsqueda o el rango de fechas, o borre los filtros.</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="323"/>
        <source>Add recorded expense</source>
        <translation>Añadir gasto registrado</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="358"/>
        <source>Delete recorded expense</source>
        <translation>Eliminar gasto registrado</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="372"/>
        <source>Delete &quot;%1&quot;?</source>
        <translation type="unfinished">¿Eliminar «%1»?</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="379"/>
        <source>Cancel</source>
        <translation type="unfinished">Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/pages/RecordedExpensesPage.qml" line="386"/>
        <source>Delete</source>
        <translation type="unfinished">Eliminar</translation>
    </message>
</context>
<context>
    <name>SettingsPage</name>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="15"/>
        <location filename="../qml/pages/SettingsPage.qml" line="64"/>
        <source>Settings</source>
        <translation>Configuración</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="54"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="192"/>
        <source>Appearance</source>
        <translation>Apariencia</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="197"/>
        <location filename="../qml/pages/SettingsPage.qml" line="207"/>
        <source>Dark mode</source>
        <translation>Modo oscuro</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="198"/>
        <source>Restart not required</source>
        <translation>No es necesario reiniciar</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="212"/>
        <location filename="../qml/pages/SettingsPage.qml" line="236"/>
        <source>Language</source>
        <translation>Idioma</translation>
    </message>
    <message>
        <source>English</source>
        <translation type="vanished">Inglés</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="250"/>
        <source>Data &amp; Currency</source>
        <translation>Datos y moneda</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="255"/>
        <source>Exchange rates</source>
        <translation>Tipos de cambio</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="263"/>
        <source>Hide</source>
        <translation>Ocultar</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="263"/>
        <source>Manage ▶</source>
        <translation>Gestionar ▶</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="265"/>
        <source>Manage exchange rates</source>
        <translation>Gestionar tipos de cambio</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="271"/>
        <location filename="../qml/pages/SettingsPage.qml" line="287"/>
        <source>Fetch live exchange rates</source>
        <translation>Obtener tipos de cambio en vivo</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="273"/>
        <source>When enabled, exchange rates are loaded from a built-in mock provider instead of the live API.</source>
        <translation>Si está activado, los tipos de cambio se cargan desde un proveedor simulado integrado en lugar de la API en vivo.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="276"/>
        <source>When enabled, the app may contact an external service to download current exchange rates. Network access is required.</source>
        <translation>Si está activado, la aplicación puede contactar un servicio externo para descargar tipos de cambio actuales. Se requiere acceso a la red.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="293"/>
        <location filename="../qml/pages/SettingsPage.qml" line="306"/>
        <source>Use mock exchange rates</source>
        <translation>Usar tipos de cambio simulados</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="294"/>
        <source>Developer option: returns prepared rates without contacting the external API. Start the app with --dev to show this toggle.</source>
        <translation>Opción de desarrollador: devuelve tasas preparadas sin contactar la API externa. Inicie la app con --dev para mostrar esta opción.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="319"/>
        <source>Rates by</source>
        <translation>Tasas por</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="325"/>
        <source>Exchange Rate API</source>
        <translation>Exchange Rate API</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="334"/>
        <source>Exchange Rate API provider website</source>
        <translation>Sitio web del proveedor Exchange Rate API</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="358"/>
        <source>Receipts</source>
        <translation>Recibos</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="364"/>
        <source>On-device receipt scanning</source>
        <translation>Escaneo de recibos en el dispositivo</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="366"/>
        <source>Ready. Uses Apple Vision on this Mac. Photos stay on this device.</source>
        <translation>Listo. Usa Apple Vision en este Mac. Las fotos permanecen en este dispositivo.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="368"/>
        <source>Required for Scan. Installs Apple Vision bindings for this app. Network access is required.</source>
        <translation>Obligatorio para Escanear. Instala los enlaces de Apple Vision para esta aplicación. Se requiere acceso a la red.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="369"/>
        <source>This app build does not include on-device scanning.</source>
        <translation>Esta versión de la aplicación no incluye el escaneo en el dispositivo.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="389"/>
        <source>Installing…</source>
        <translation>Instalando…</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="390"/>
        <source>Install</source>
        <translation>Instalar</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="392"/>
        <source>Install on-device receipt scanning</source>
        <translation>Instalar el escaneo de recibos en el dispositivo</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="398"/>
        <location filename="../qml/pages/SettingsPage.qml" line="411"/>
        <source>Cloud receipt scanning</source>
        <translation>Escaneo de recibos en la nube</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="399"/>
        <source>Off by default. Receipt photos stay on this device. Enabling this does not upload images; a cloud provider is not connected yet.</source>
        <translation>Desactivado de forma predeterminada. Las fotos de recibos permanecen en este dispositivo. Activar esto no sube imágenes; aún no hay un proveedor en la nube.</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="426"/>
        <source>About</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="431"/>
        <source>User manual</source>
        <translation>Manual de usuario</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="432"/>
        <source>Open the bundled PDF guide in your system&apos;s default viewer</source>
        <translation>Abra la guía PDF incluida en el visor predeterminado del sistema</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="441"/>
        <source>Open ▶</source>
        <translation>Abrir ▶</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="443"/>
        <source>Open user manual</source>
        <translation>Abrir manual de usuario</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="449"/>
        <source>Methodology</source>
        <translation>Metodología</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="450"/>
        <source>How cash shortfalls, date patterns, currencies, and scenarios are calculated</source>
        <translation>Cómo se calculan los faltantes de efectivo, patrones de fecha, divisas y escenarios</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="461"/>
        <source>View ▶</source>
        <translation>Ver ▶</translation>
    </message>
    <message>
        <location filename="../qml/pages/SettingsPage.qml" line="463"/>
        <source>View methodology</source>
        <translation>Ver metodología</translation>
    </message>
    <message>
        <source>Exchange rates by &lt;a href=&quot;https://www.exchangerate-api.com&quot;&gt;ExchangeRate-API&lt;/a&gt;</source>
        <translation type="vanished">Tipos de cambio de &lt;a href=&quot;https://www.exchangerate-api.com&quot;&gt;ExchangeRate-API&lt;/a&gt;</translation>
    </message>
</context>
<context>
    <name>SimulationControls</name>
    <message>
        <source>Simulation</source>
        <translation type="vanished">Simulación</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="131"/>
        <source>Start date</source>
        <translation>Fecha de inicio</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="149"/>
        <source>End date</source>
        <translation>Fecha de fin</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="167"/>
        <location filename="../qml/components/SimulationControls.qml" line="197"/>
        <source>Initial balance</source>
        <translation>Saldo inicial</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="218"/>
        <location filename="../qml/components/SimulationControls.qml" line="228"/>
        <source>Display currency</source>
        <translation>Moneda de visualización</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="279"/>
        <location filename="../qml/components/SimulationControls.qml" line="283"/>
        <source>Run forecast</source>
        <translation>Ejecutar previsión</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="344"/>
        <location filename="../qml/components/SimulationControls.qml" line="348"/>
        <source>Export executive report</source>
        <translation>Exportar informe ejecutivo</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="206"/>
        <source>0.00</source>
        <translation>0.00</translation>
    </message>
    <message>
        <source>Run Simulation</source>
        <translation type="vanished">Ejecutar simulación</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="322"/>
        <location filename="../qml/components/SimulationControls.qml" line="326"/>
        <source>Export CSV</source>
        <translation>Exportar CSV</translation>
    </message>
    <message>
        <source>Export PDF</source>
        <translation type="vanished">Exportar PDF</translation>
    </message>
    <message>
        <location filename="../qml/components/SimulationControls.qml" line="370"/>
        <source>End date must be on or after the start date.</source>
        <translation>La fecha de fin debe ser igual o posterior a la de inicio.</translation>
    </message>
</context>
<context>
    <name>SimulationPage</name>
    <message>
        <source>Export CSV</source>
        <translation type="vanished">Exportar CSV</translation>
    </message>
    <message>
        <source>Export PDF</source>
        <translation type="vanished">Exportar PDF</translation>
    </message>
    <message>
        <source>Export simulation as CSV</source>
        <translation type="vanished">Exportar simulación como CSV</translation>
    </message>
    <message>
        <location filename="../qml/pages/SimulationPage.qml" line="98"/>
        <source>Export projection as CSV</source>
        <translation>Exportar proyección como CSV</translation>
    </message>
    <message>
        <location filename="../qml/pages/SimulationPage.qml" line="100"/>
        <source>CSV files (*.csv)</source>
        <translation>Archivos CSV (*.csv)</translation>
    </message>
    <message>
        <location filename="../qml/pages/SimulationPage.qml" line="109"/>
        <source>Export executive report</source>
        <translation>Exportar informe ejecutivo</translation>
    </message>
    <message>
        <source>Export projection as PDF</source>
        <translation type="vanished">Exportar proyección como PDF</translation>
    </message>
    <message>
        <location filename="../qml/pages/SimulationPage.qml" line="114"/>
        <source>Forecast</source>
        <translation>Previsión</translation>
    </message>
    <message>
        <source>Export simulation as PDF</source>
        <translation type="vanished">Exportar simulación como PDF</translation>
    </message>
    <message>
        <location filename="../qml/pages/SimulationPage.qml" line="111"/>
        <source>PDF files (*.pdf)</source>
        <translation>Archivos PDF (*.pdf)</translation>
    </message>
    <message>
        <source>Plan</source>
        <translation type="vanished">Plan</translation>
    </message>
    <message>
        <location filename="../qml/pages/SimulationPage.qml" line="149"/>
        <source>Exported successfully</source>
        <translation>Exportación correcta</translation>
    </message>
</context>
<context>
    <name>SuggestionsPanel</name>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="65"/>
        <source>%1 %2</source>
        <translation>%1 %2</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="85"/>
        <source>Suggestions</source>
        <translation>Sugerencias</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="104"/>
        <source>Based on the saved forecast — the chart above reflects your scenario.</source>
        <translation>Según el pronóstico guardado — el gráfico anterior refleja su escenario.</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="115"/>
        <source>No suggestions for this projection.</source>
        <translation>No hay sugerencias para esta proyección.</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="227"/>
        <source>Try in scenario</source>
        <translation>Probar en escenario</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="230"/>
        <source>Try in scenario: %1</source>
        <translation>Probar en escenario: %1</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="256"/>
        <location filename="../qml/components/SuggestionsPanel.qml" line="259"/>
        <source>Show less</source>
        <translation>Mostrar menos</translation>
    </message>
    <message>
        <location filename="../qml/components/SuggestionsPanel.qml" line="256"/>
        <location filename="../qml/components/SuggestionsPanel.qml" line="259"/>
        <source>Show more</source>
        <translation>Mostrar más</translation>
    </message>
</context>
<context>
    <name>TemplatePickerDialog</name>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="54"/>
        <source>Choose a template</source>
        <translation>Elija una plantilla</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="54"/>
        <source>Name your forecast</source>
        <translation>Nombre su previsión</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="77"/>
        <source>Start from a pre-built cash-flow template. You can edit every line item after creation.</source>
        <translation>Empiece desde una plantilla de flujos de caja predefinida. Puede editar cada línea después de la creación.</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="157"/>
        <source>%1 template: %2</source>
        <translation>Plantilla %1: %2</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="177"/>
        <source>Template: %1</source>
        <translation>Plantilla: %1</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="186"/>
        <source>My budget 2026</source>
        <translation>Mi presupuesto 2026</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="187"/>
        <source>Forecast name</source>
        <translation>Nombre de la previsión</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="196"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="204"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="214"/>
        <source>Use template</source>
        <translation>Usar plantilla</translation>
    </message>
    <message>
        <location filename="../qml/components/TemplatePickerDialog.qml" line="227"/>
        <source>Create</source>
        <translation>Crear</translation>
    </message>
</context>
<context>
    <name>UserManual</name>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="700"/>
        <source>Cash Flow Planner</source>
        <translation>Cash Flow Planner</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="731"/>
        <source>Cash Flow Planner is an offline-first cash-flow forecasting application forindividuals and small businesses. You define income and expense cash flows, runprojections over a chosen horizon, and review a running balance that shows when acash shortfall may occur.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="738"/>
        <source>All forecasts, cash flows, and exchange rates are stored locally in a SQLitedatabase on your computer. The app does not require an account, sign-in, orcontinuous internet connection to build and run forecasts.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="744"/>
        <source>Your data never leaves your device unless you explicitly export a file or share abackup.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="749"/>
        <source>Cash Flow Planner does not provide automatic cloud backup. Use Export forecast tosave a .ftplan file if you need a portable copy of your work.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="754"/>
        <source>This manual is written for freelancers, business operators, fractional CFOs, andadvisors who need a practical cash-flow forecast without enterprise complexity.Whether you manage personal income swings or a small company&apos;s payroll and vendorpayments, the same workflow applies.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="761"/>
        <source>Build a forecast from scratch or start from a bundled template</source>
        <translation>Cree una previsión desde cero o comience desde una plantilla integrada</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="764"/>
        <source>Model recurring and one-time cash flows with compact date patterns</source>
        <translation>Modele flujos de caja recurrentes y puntuales con patrones de fecha compactos</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="767"/>
        <source>Run projections and spot the first cash shortfall before it happens</source>
        <translation>Ejecute proyecciones y detecte el primer déficit de tesorería antes de que ocurra</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="770"/>
        <source>Explore scenarios without overwriting saved cash flows</source>
        <translation>Explore escenarios sin sobrescribir los flujos de caja guardados</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="773"/>
        <source>Throughout the app, user-facing text uses professional forecastingvocabulary—Forecast, Cash flow, Cash shortfall, and Scenario—rather thanpersonal-finance jargon.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="779"/>
        <source>When you launch Cash Flow Planner for the first time, the Forecasts page is empty.The app creates a local database automatically in your platform application-datafolder, so you can start working immediately.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="785"/>
        <source>The main navigation shell keeps Forecasts as your home view. Open Settings fromthe gear icon in the app header to adjust appearance and language before youcreate your first forecast.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="791"/>
        <source>Switch Dark mode and Language in Settings without restarting the application—theinterface updates live.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="796"/>
        <source>If you reinstall the app on the same machine, your existing database is preservedin the application-data location.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="801"/>
        <source>Select New forecast on the Forecasts page. A dialog asks whether to start with ablank forecast or use a template. For a blank forecast, enter a descriptive name,choose the forecast base currency, and set the opening cash balance.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="807"/>
        <source>After creation, the forecast detail view opens with three tabs: Cash flows,Projection, and Change history. Add cash flows on the first tab, then move toProjection when you are ready to run a forecast.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="813"/>
        <source>Pick the base currency carefully—it is the currency used to sum cash flows duringa projection run. Other currencies convert using exchange rates from Settings.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="818"/>
        <source>Each forecast is independent. Deleting a forecast removes its cash flows andprojection history for that forecast only.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="823"/>
        <source>When you choose From template in the New forecast dialog, the template pickerlists bundled starting points such as freelancer, small business, and householdcash-flow examples. Each card shows a short description of what the templateincludes.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="830"/>
        <source>After you select a template and confirm a forecast name, Cash Flow Planner createsthe forecast and pre-fills typical income and expense cash flows. Every line itemremains fully editable—templates are a shortcut, not a constraint.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="836"/>
        <source>Templates are ideal for onboarding: review each pre-filled cash flow, adjustamounts to match your situation, and delete lines you do not need.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="841"/>
        <source>Choosing a template does not lock currency or patterns. You can change any fieldimmediately after creation.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="846"/>
        <source>Open a forecast and select the Cash flows tab. Income and expense cash flows arelisted separately so you can scan inflows and outflows at a glance. Use the Addcash flow floating action button to open the cash flow drawer.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="852"/>
        <source>In the drawer, choose whether the line is income or expense, enter a name andamount, pick a currency, and type a date pattern. The pattern preview label belowthe field updates as you type so you can confirm the schedule before saving.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="858"/>
        <source>Income cash flows increase your balance on scheduled dates</source>
        <translation>Los flujos de caja de ingresos aumentan su saldo en las fechas programadas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="861"/>
        <source>Expense cash flows decrease your balance on scheduled dates</source>
        <translation>Los flujos de caja de gastos disminuyen su saldo en las fechas programadas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="864"/>
        <source>Use Import on the Cash flows page to load rows from CSV or Excel</source>
        <translation>Use Importar en la página Flujos de caja para cargar filas desde CSV o Excel</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="867"/>
        <source>Give each cash flow a clear name—projection results and the cash shortfall bannerreference these names when highlighting contributing line items.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="872"/>
        <source>Every cash flow is scheduled with a compact date pattern instead of pickingindividual calendar dates. Patterns can represent daily, monthly, yearly, orone-time events. The syntax is validated while you edit, and invalid patterns showan error before you save.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="879"/>
        <source>Examples include ... for every day, 10.. for monthly on the 10th, 15.03. foryearly on 15 March, and 15.03.2026 for a single occurrence. The live descriptionunder the pattern field restates the schedule in plain language.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="885"/>
        <source>If a pattern looks wrong, check the preview label before saving—a small typo canshift every occurrence in the projection range.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="890"/>
        <source>The Quick reference chapter at the end of this manual lists common patterns in acheat sheet table.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="895"/>
        <source>Tap or click a cash flow in the list to reopen the drawer in Edit cash flow mode.Changes save to the forecast immediately when you confirm. Amount, currency,pattern, and active state can all be updated.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="901"/>
        <source>Use delete inside the drawer to remove a cash flow you no longer need. After anyedit, return to the Projection tab and run the forecast again so monthly summariesand the balance chart reflect your latest data.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="907"/>
        <source>Deactivate a line item temporarily using the Scenario panel on the Projection tabif you only want to test removing it.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="912"/>
        <source>Edits on the Cash flows tab are saved permanently to your forecast. Scenariooverrides on the Projection tab are not.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="917"/>
        <source>Select the Projection tab to configure and run a forecast. Choose the projectionstart date, end date (horizon), and confirm the opening cash balance. The controlsat the top of the page apply to the current forecast run.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="923"/>
        <source>Press Run forecast to expand every active cash flow across the date range, convertforeign currencies to the forecast base currency, and compute a day-by-day runningbalance. While the run is in progress, the button shows a busy state.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="929"/>
        <source>Re-run the forecast after you change cash flows, exchange rates, or the horizon sotables and charts stay current.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="934"/>
        <source>If a required exchange rate is missing, the run stops with a clear error—add therate in Settings and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="939"/>
        <source>Below the controls, the monthly table aggregates each month in the projectionrange. Columns typically include opening balance, inflows, outflows, net flow, andclosing balance. Amounts use semantic coloring—inflows in green and outflows inred—so trends are easy to scan.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="946"/>
        <source>Months where the closing balance falls below zero are treated as a cash shortfall.Those rows receive an amber highlight so you can spot problem periods withoutreading every number.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="952"/>
        <source>Compare consecutive months to see whether a shortfall is a one-month timing gap ora sustained cash-flow problem.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="957"/>
        <source>The table shows monthly snapshots. The cash shortfall banner reports the first daythe daily balance drops below zero, which may fall mid-month.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="962"/>
        <source>The balance chart plots your running balance across the projection horizon. Thearea above zero uses the primary brand color; when the balance drops below zero,the chart fills the deficit region in red so shortfalls stand out visually.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="968"/>
        <source>Move the pointer over the chart to show a vertical guide line, the nearest datapoint, and a tooltip with the date and balance for that day. This is useful forpinpointing when a decline begins.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="974"/>
        <source>Use the chart together with the monthly table—the chart shows timing within amonth; the table summarizes totals.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="979"/>
        <source>When a projection finds a day with a negative closing balance, a dismissible cashshortfall banner appears at the top of the Projection tab. It names the firstshortfall date and the expense cash flow that contributed on that day.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="985"/>
        <source>Address a shortfall by adjusting timing or amounts on the Cash flows tab, addingincome, or opening the Scenario panel to test changes before you commit them.Dismiss the banner when you have noted the date—it reappears on the next run ifthe shortfall still exists.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="992"/>
        <source>Only the earliest cash shortfall in a run is reported. Later shortfalls during thesame projection are not listed separately.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="997"/>
        <source>Export an executive report after a run to share projection results, including thebalance chart, with stakeholders.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1002"/>
        <source>The Scenario panel on the Projection tab lets you explore what-if changes withoutaltering saved cash flows. Expand the panel to see each active line item withoverride controls for amount and whether the line is active in the current run.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1008"/>
        <source>Adjust an amount or deactivate a line, then run the forecast again. The projectionengine applies overrides only for that run, leaving your stored forecast unchangedon the Cash flows tab.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1014"/>
        <source>Use scenarios to test hiring, deferring a payment, or pausing a subscriptionbefore you edit the baseline forecast.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1019"/>
        <source>Scenario overrides are never saved to your forecast. Clear overrides or close thepanel to return to the saved baseline.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1024"/>
        <source>After you enable overrides, run the forecast to see updated monthly balances,chart shape, and cash shortfall timing. Compare the results mentally with yourlast baseline run, or note which line items you changed in the Scenario panel.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1030"/>
        <source>When you export an executive report while overrides are active, the PDF caninclude a scenario comparison section that contrasts key metrics between thebaseline and the current scenario run.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1036"/>
        <source>Toggle overrides off line by line to isolate which change moved the first cashshortfall date.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1041"/>
        <source>Change history on the forecast detail tab records edits to saved cash flows, nottemporary scenario overrides.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1046"/>
        <source>On the Cash flows tab, select Import to open the import dialog. Choose a CSV orExcel file from your computer and map file columns to name, amount, type (incomeor expense), currency, and date pattern.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1052"/>
        <source>Preview the mapped rows before confirming. Rows with invalid patterns or missingrequired fields are reported so you can fix the source file or adjust mappings.Successful rows are added to the open forecast immediately.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1058"/>
        <source>Prepare spreadsheets with consistent column headers to speed up mapping—you canre-use the same layout for monthly updates.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1063"/>
        <source>Import adds cash flows to the current forecast. It does not replace existing linesunless you delete them first.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1068"/>
        <source>After you run a projection, use Export executive report on the Projection tab togenerate a polished PDF for sharing. The report includes a monthly cash-bridgetable, a balance chart, foreign-exchange footnotes when applicable, and amethodology appendix.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1075"/>
        <source>If scenario overrides are active, the export may also include a scenariocomparison table summarizing how the scenario run differs from the saved baseline.Export CSV is available on the same page for spreadsheet analysis.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1081"/>
        <source>Run the forecast immediately before exporting so the report reflects your latestcash flows and horizon.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1086"/>
        <source>The executive report describes one forecast run. Re-export after material changesrather than editing the PDF by hand.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1091"/>
        <source>On the Forecasts page, each forecast card offers Export forecast to save aversioned .ftplan bundle. The file contains the forecast metadata, cash flows, andany exchange rates embedded in the bundle for portability.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1097"/>
        <source>Use Import forecast on the Forecasts page to create a new forecast from a .ftplanfile. This is the recommended way to back up work, move between computers, orshare a starting point with a colleague.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1103"/>
        <source>Keep dated .ftplan backups before large restructuring so you can recover anearlier forecast if needed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1108"/>
        <source>The .ftplan extension is unchanged for compatibility—user-facing labels say Importforecast and Export forecast.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1113"/>
        <source>Open Settings from the gear icon in the app header. Under Appearance, toggle Darkmode to switch between light and dark themes. The change applies immediately withno restart required.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1119"/>
        <source>The Language control lists English, French, Russian, Spanish, and German.Selecting a language retranslates the entire interface, including menus, dialogs,and export headers, in the same session.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1125"/>
        <source>Set language before generating shared PDF exports if recipients expect aparticular locale.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1134"/>
        <source>Exchange rates are managed globally under Data &amp; Currency in Settings. ExpandManage exchange rates to add or edit pairs relative to your forecasts&apos; basecurrencies. During a projection run, each cash flow in a foreign currency convertsusing the stored rate before amounts are summed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1141"/>
        <source>Enable Fetch live exchange rates to download current values when network access isavailable. Attribution for the rate provider appears on the Settings page. If arequired rate is missing, the forecast run fails with an error rather thanguessing a value.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1148"/>
        <source>Refresh live rates before an important projection if markets have movedsignificantly since your last update.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1153"/>
        <source>Exchange rates apply app-wide. Updating a rate affects every forecast that usesthe affected currency pair.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1158"/>
        <source>The Methodology page—linked from Settings under About—explains how Cash FlowPlanner computes daily balances, detects the first cash shortfall, expands datepatterns, and normalizes currencies. It is aimed at readers who want technicaltransparency.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1165"/>
        <source>This user manual focuses on day-to-day workflows; the Methodology page complementsit with calculation detail. Executive PDF exports also include a methodologyappendix for stakeholders who receive reports.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1171"/>
        <source>Share the Methodology page with clients or partners who ask how projection numbersare produced.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1176"/>
        <source>Type patterns exactly as shown in the Pattern column. Trailing dots matter. Theapp validates syntax and shows a plain-language description under the field whileyou edit.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1183"/>
        <source>Monthly patterns use day-of-month before the two dots; yearly patterns useday.month.; one-time patterns add the full year.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1188"/>
        <source>The app shell keeps Forecasts as the home view and Settings one click away in theheader. Inside a forecast, switch between Cash flows, Projection, and Changehistory using the tabs at the top of the detail view.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1194"/>
        <source>Forecasts page — create, import, export, and open forecasts</source>
        <translation>Página Previsiones — crear, importar, exportar y abrir previsiones</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1197"/>
        <source>Cash flows tab — add, edit, import, and organize line items</source>
        <translation>Pestaña Flujos de caja — añadir, editar, importar y organizar partidas</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1200"/>
        <source>Projection tab — set horizon, run forecast, scenarios, exports</source>
        <translation>Pestaña Proyección — definir horizonte, ejecutar previsión, escenarios, exportaciones</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1203"/>
        <source>Settings — theme, language, exchange rates, methodology, user manual</source>
        <translation>Configuración — tema, idioma, tipos de cambio, metodología, manual de usuario</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1206"/>
        <source>Run a projection after every meaningful edit to cash flows or rates so shortfallalerts and charts stay accurate.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1211"/>
        <source>Scenario overrides live only on the Projection tab and are cleared when you resetthe Scenario panel—they never replace saved cash flows.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="701"/>
        <source>Welcome</source>
        <translation>Bienvenida</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="709"/>
        <source>About Cash Flow Planner</source>
        <translation>Acerca de Cash Flow Planner</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="710"/>
        <source>Who this manual is for</source>
        <translation>A quién va dirigido este manual</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="702"/>
        <source>Getting started</source>
        <translation>Primeros pasos</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="711"/>
        <source>First launch</source>
        <translation>Primer inicio</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="712"/>
        <source>Create a forecast</source>
        <translation>Crear una previsión</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="713"/>
        <source>Start from a template</source>
        <translation>Empezar desde una plantilla</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="703"/>
        <source>Cash flows</source>
        <translation>Flujos de caja</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="714"/>
        <source>Add income and expenses</source>
        <translation>Añadir ingresos y gastos</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="715"/>
        <source>Date patterns</source>
        <translation>Patrones de fecha</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="716"/>
        <source>Edit and delete</source>
        <translation>Editar y eliminar</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="704"/>
        <source>Running a projection</source>
        <translation>Ejecutar una proyección</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="717"/>
        <source>Set horizon and opening balance</source>
        <translation>Definir horizonte y saldo inicial</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="718"/>
        <source>Read the monthly table</source>
        <translation>Leer la tabla mensual</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="719"/>
        <source>Balance chart</source>
        <translation>Gráfico del saldo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="720"/>
        <source>Cash shortfall alert</source>
        <translation>Alerta de déficit de tesorería</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="705"/>
        <source>What-if scenarios</source>
        <translation>Escenarios</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="721"/>
        <source>Enable overrides</source>
        <translation>Activar sustituciones</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="722"/>
        <source>Compare with baseline</source>
        <translation>Comparar con la base de referencia</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="706"/>
        <source>Import &amp; export</source>
        <translation>Importación y exportación</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="723"/>
        <source>Import CSV/Excel</source>
        <translation>Importar CSV/Excel</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="724"/>
        <source>Export executive PDF</source>
        <translation>Exportar PDF ejecutivo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="725"/>
        <source>Share .ftplan files</source>
        <translation>Compartir archivos .ftplan</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="707"/>
        <source>Settings &amp; preferences</source>
        <translation>Configuración y preferencias</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="726"/>
        <source>Theme and language</source>
        <translation>Tema e idioma</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="727"/>
        <source>Exchange rates</source>
        <translation>Tipos de cambio</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="728"/>
        <source>Methodology</source>
        <translation>Metodología</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="708"/>
        <source>Quick reference</source>
        <translation>Referencia rápida</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="699"/>
        <source>User Manual</source>
        <translation>Manual de usuario</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="729"/>
        <source>Date pattern cheat sheet</source>
        <translation>Hoja de referencia de patrones de fecha</translation>
    </message>
    <message>
        <source>Cash Flow Planner is an offline-first cash-flow forecasting application for individuals and small businesses. You define income and expense cash flows, run projections over a chosen horizon, and review a running balance that shows when a cash shortfall may occur.</source>
        <translation type="vanished">Cash Flow Planner es una aplicación de previsión de flujos de caja sin conexión para particulares y pequeñas empresas. Define flujos de caja de ingresos y gastos, ejecuta proyecciones en un horizonte elegido y revisa un saldo acumulado que muestra cuándo puede producirse un déficit de tesorería.</translation>
    </message>
    <message>
        <source>All forecasts, cash flows, and exchange rates are stored locally in a SQLite database on your computer. The app does not require an account, sign-in, or continuous internet connection to build and run forecasts.</source>
        <translation type="vanished">Todas las previsiones, flujos de caja y tipos de cambio se almacenan localmente en una base SQLite en su equipo. La aplicación no requiere cuenta, inicio de sesión ni conexión continua a Internet para crear y ejecutar previsiones.</translation>
    </message>
    <message>
        <source>Your data never leaves your device unless you explicitly export a file or share a backup.</source>
        <translation type="vanished">Sus datos nunca abandonan su dispositivo a menos que exporte explícitamente un archivo o comparta una copia de seguridad.</translation>
    </message>
    <message>
        <source>Cash Flow Planner does not provide automatic cloud backup. Use Export forecast to save a .ftplan file if you need a portable copy of your work.</source>
        <translation type="vanished">Cash Flow Planner no ofrece copia de seguridad automática en la nube. Use Exportar previsión para guardar un archivo .ftplan si necesita una copia portable de su trabajo.</translation>
    </message>
    <message>
        <source>This manual is written for freelancers, business operators, fractional CFOs, and advisors who need a practical cash-flow forecast without enterprise complexity. Whether you manage personal income swings or a small company&apos;s payroll and vendor payments, the same workflow applies.</source>
        <translation type="vanished">Este manual está dirigido a autónomos, operadores de negocio, CFO fraccionales y asesores que necesitan una previsión práctica de flujos de caja sin la complejidad empresarial. Ya gestione variaciones de ingresos personales o la nómina y pagos a proveedores de una pequeña empresa, el mismo flujo de trabajo se aplica.</translation>
    </message>
    <message>
        <source>Throughout the app, user-facing text uses professional forecasting vocabulary—Forecast, Cash flow, Cash shortfall, and Scenario—rather than personal-finance jargon.</source>
        <translation type="vanished">En toda la aplicación, el texto visible usa vocabulario profesional de previsión — Previsión, Flujo de caja, Déficit de tesorería y Escenario — en lugar de jerga de finanzas personales.</translation>
    </message>
    <message>
        <source>When you launch Cash Flow Planner for the first time, the Forecasts page is empty. The app creates a local database automatically in your platform application-data folder, so you can start working immediately.</source>
        <translation type="vanished">Al iniciar Cash Flow Planner por primera vez, la página Previsiones está vacía. La aplicación crea automáticamente una base local en la carpeta de datos de la aplicación de su plataforma, para que pueda empezar de inmediato.</translation>
    </message>
    <message>
        <source>The main navigation shell keeps Forecasts as your home view. Open Settings from the gear icon in the app header to adjust appearance and language before you create your first forecast.</source>
        <translation type="vanished">La navegación principal mantiene Previsiones como vista de inicio. Abra Configuración desde el icono de engranaje en la cabecera para ajustar apariencia e idioma antes de crear su primera previsión.</translation>
    </message>
    <message>
        <source>Switch Dark mode and Language in Settings without restarting the application—the interface updates live.</source>
        <translation type="vanished">Cambie Modo oscuro e Idioma en Configuración sin reiniciar la aplicación — la interfaz se actualiza en vivo.</translation>
    </message>
    <message>
        <source>If you reinstall the app on the same machine, your existing database is preserved in the application-data location.</source>
        <translation type="vanished">Si reinstala la aplicación en el mismo equipo, su base existente se conserva en la ubicación de datos de la aplicación.</translation>
    </message>
    <message>
        <source>Select New forecast on the Forecasts page. A dialog asks whether to start with a blank forecast or use a template. For a blank forecast, enter a descriptive name, choose the forecast base currency, and set the opening cash balance.</source>
        <translation type="vanished">Seleccione Nueva previsión en la página Previsiones. Un diálogo pregunta si desea empezar con una previsión en blanco o usar una plantilla. Para una previsión en blanco, introduzca un nombre descriptivo, elija la divisa base de la previsión y establezca el saldo de caja inicial.</translation>
    </message>
    <message>
        <source>After creation, the forecast detail view opens with three tabs: Cash flows, Projection, and Change history. Add cash flows on the first tab, then move to Projection when you are ready to run a forecast.</source>
        <translation type="vanished">Tras la creación, se abre la vista detallada de la previsión con tres pestañas: Flujos de caja, Proyección e Historial de cambios. Añada flujos de caja en la primera pestaña y pase a Proyección cuando esté listo para ejecutar una previsión.</translation>
    </message>
    <message>
        <source>Pick the base currency carefully—it is the currency used to sum cash flows during a projection run. Other currencies convert using exchange rates from Settings.</source>
        <translation type="vanished">Elija la divisa base con cuidado — es la divisa usada para sumar flujos de caja durante una ejecución de proyección. Otras divisas se convierten con los tipos de cambio de Configuración.</translation>
    </message>
    <message>
        <source>Each forecast is independent. Deleting a forecast removes its cash flows and projection history for that forecast only.</source>
        <translation type="vanished">Cada previsión es independiente. Eliminar una previsión quita sus flujos de caja e historial de proyección solo para esa previsión.</translation>
    </message>
    <message>
        <source>When you choose From template in the New forecast dialog, the template picker lists bundled starting points such as freelancer, small business, and household cash-flow examples. Each card shows a short description of what the template includes.</source>
        <translation type="vanished">Cuando elige Desde plantilla en el diálogo Nueva previsión, el selector de plantillas enumera puntos de partida integrados como ejemplos de flujos de caja para autónomos, pequeñas empresas y hogares. Cada tarjeta muestra una breve descripción de lo que incluye la plantilla.</translation>
    </message>
    <message>
        <source>After you select a template and confirm a forecast name, Cash Flow Planner creates the forecast and pre-fills typical income and expense cash flows. Every line item remains fully editable—templates are a shortcut, not a constraint.</source>
        <translation type="vanished">Tras seleccionar una plantilla y confirmar un nombre de previsión, Cash Flow Planner crea la previsión y rellena previamente flujos de caja típicos de ingresos y gastos. Cada partida sigue siendo totalmente editable — las plantillas son un atajo, no una restricción.</translation>
    </message>
    <message>
        <source>Templates are ideal for onboarding: review each pre-filled cash flow, adjust amounts to match your situation, and delete lines you do not need.</source>
        <translation type="vanished">Las plantillas son ideales para la incorporación: revise cada flujo de caja prerrellenado, ajuste importes a su situación y elimine líneas que no necesite.</translation>
    </message>
    <message>
        <source>Choosing a template does not lock currency or patterns. You can change any field immediately after creation.</source>
        <translation type="vanished">Elegir una plantilla no bloquea la divisa ni los patrones. Puede cambiar cualquier campo inmediatamente después de la creación.</translation>
    </message>
    <message>
        <source>Open a forecast and select the Cash flows tab. Income and expense cash flows are listed separately so you can scan inflows and outflows at a glance. Use the Add cash flow floating action button to open the cash flow drawer.</source>
        <translation type="vanished">Abra una previsión y seleccione la pestaña Flujos de caja. Los flujos de caja de ingresos y gastos se listan por separado para que pueda revisar entradas y salidas de un vistazo. Use el botón de acción flotante Añadir flujo de caja para abrir el panel lateral.</translation>
    </message>
    <message>
        <source>In the drawer, choose whether the line is income or expense, enter a name and amount, pick a currency, and type a date pattern. The pattern preview label below the field updates as you type so you can confirm the schedule before saving.</source>
        <translation type="vanished">En el panel, indique si la línea es ingreso o gasto, introduzca nombre e importe, elija una divisa y escriba un patrón de fecha. La etiqueta de vista previa bajo el campo se actualiza mientras escribe para confirmar el calendario antes de guardar.</translation>
    </message>
    <message>
        <source>Give each cash flow a clear name—projection results and the cash shortfall banner reference these names when highlighting contributing line items.</source>
        <translation type="vanished">Asigne a cada flujo de caja un nombre claro — los resultados de proyección y el banner de déficit de tesorería citan estos nombres al resaltar las partidas contribuyentes.</translation>
    </message>
    <message>
        <source>Every cash flow is scheduled with a compact date pattern instead of picking individual calendar dates. Patterns can represent daily, monthly, yearly, or one-time events. The syntax is validated while you edit, and invalid patterns show an error before you save.</source>
        <translation type="vanished">Cada flujo de caja se programa con un patrón de fecha compacto en lugar de elegir fechas individuales. Los patrones pueden representar eventos diarios, mensuales, anuales o puntuales. La sintaxis se valida mientras edita, y los patrones no válidos muestran un error antes de guardar.</translation>
    </message>
    <message>
        <source>Examples include ... for every day, 10.. for monthly on the 10th, 15.03. for yearly on 15 March, and 15.03.2026 for a single occurrence. The live description under the pattern field restates the schedule in plain language.</source>
        <translation type="vanished">Los ejemplos incluyen ... para cada día, 10.. para mensual el día 10, 15.03. para anual el 15 de marzo y 15.03.2026 para una sola ocurrencia. La descripción en vivo bajo el campo de patrón reformula el calendario en lenguaje claro.</translation>
    </message>
    <message>
        <source>If a pattern looks wrong, check the preview label before saving—a small typo can shift every occurrence in the projection range.</source>
        <translation type="vanished">Si un patrón parece incorrecto, compruebe la etiqueta de vista previa antes de guardar — un pequeño error puede desplazar cada ocurrencia en el rango de proyección.</translation>
    </message>
    <message>
        <source>The Quick reference chapter at the end of this manual lists common patterns in a cheat sheet table.</source>
        <translation type="vanished">El capítulo Referencia rápida al final de este manual enumera patrones comunes en una tabla de referencia.</translation>
    </message>
    <message>
        <source>Tap or click a cash flow in the list to reopen the drawer in Edit cash flow mode. Changes save to the forecast immediately when you confirm. Amount, currency, pattern, and active state can all be updated.</source>
        <translation type="vanished">Toque o haga clic en un flujo de caja de la lista para reabrir el panel en modo Editar flujo de caja. Los cambios se guardan en la previsión inmediatamente al confirmar. Se pueden actualizar importe, divisa, patrón y estado activo.</translation>
    </message>
    <message>
        <source>Use delete inside the drawer to remove a cash flow you no longer need. After any edit, return to the Projection tab and run the forecast again so monthly summaries and the balance chart reflect your latest data.</source>
        <translation type="vanished">Use eliminar dentro del panel para quitar un flujo de caja que ya no necesite. Tras cualquier edición, vuelva a la pestaña Proyección y ejecute la previsión de nuevo para que los resúmenes mensuales y el gráfico del saldo reflejen sus últimos datos.</translation>
    </message>
    <message>
        <source>Deactivate a line item temporarily using the Scenario panel on the Projection tab if you only want to test removing it.</source>
        <translation type="vanished">Desactive temporalmente una partida con el panel Escenario en la pestaña Proyección si solo desea probar su eliminación.</translation>
    </message>
    <message>
        <source>Edits on the Cash flows tab are saved permanently to your forecast. Scenario overrides on the Projection tab are not.</source>
        <translation type="vanished">Las ediciones en la pestaña Flujos de caja se guardan permanentemente en su previsión. Las sustituciones de escenario en la pestaña Proyección no.</translation>
    </message>
    <message>
        <source>Select the Projection tab to configure and run a forecast. Choose the projection start date, end date (horizon), and confirm the opening cash balance. The controls at the top of the page apply to the current forecast run.</source>
        <translation type="vanished">Seleccione la pestaña Proyección para configurar y ejecutar una previsión. Elija la fecha de inicio de proyección, la fecha de fin (horizonte) y confirme el saldo de caja inicial. Los controles en la parte superior de la página se aplican a la ejecución de previsión actual.</translation>
    </message>
    <message>
        <source>Press Run forecast to expand every active cash flow across the date range, convert foreign currencies to the forecast base currency, and compute a day-by-day running balance. While the run is in progress, the button shows a busy state.</source>
        <translation type="vanished">Pulse Ejecutar previsión para expandir cada flujo de caja activo en el rango de fechas, convertir divisas extranjeras a la divisa base de la previsión y calcular un saldo acumulado día a día. Mientras la ejecución está en curso, el botón muestra un estado ocupado.</translation>
    </message>
    <message>
        <source>Re-run the forecast after you change cash flows, exchange rates, or the horizon so tables and charts stay current.</source>
        <translation type="vanished">Ejecute la previsión de nuevo tras cambiar flujos de caja, tipos de cambio u horizonte para que tablas y gráficos sigan actualizados.</translation>
    </message>
    <message>
        <source>If a required exchange rate is missing, the run stops with a clear error—add the rate in Settings and try again.</source>
        <translation type="vanished">Si falta un tipo de cambio requerido, la ejecución se detiene con un error claro — añada el tipo en Configuración e inténtelo de nuevo.</translation>
    </message>
    <message>
        <source>Below the controls, the monthly table aggregates each month in the projection range. Columns typically include opening balance, inflows, outflows, net flow, and closing balance. Amounts use semantic coloring—inflows in green and outflows in red—so trends are easy to scan.</source>
        <translation type="vanished">Debajo de los controles, la tabla mensual agrega cada mes del rango de proyección. Las columnas suelen incluir saldo inicial, entradas, salidas, flujo neto y saldo final. Los importes usan color semántico — entradas en verde y salidas en rojo — para facilitar la lectura de tendencias.</translation>
    </message>
    <message>
        <source>Months where the closing balance falls below zero are treated as a cash shortfall. Those rows receive an amber highlight so you can spot problem periods without reading every number.</source>
        <translation type="vanished">Los meses en que el saldo final cae por debajo de cero se tratan como déficit de tesorería. Esas filas reciben un resaltado ámbar para detectar periodos problemáticos sin leer cada cifra.</translation>
    </message>
    <message>
        <source>Compare consecutive months to see whether a shortfall is a one-month timing gap or a sustained cash-flow problem.</source>
        <translation type="vanished">Compare meses consecutivos para ver si un déficit es un desfase de un mes o un problema sostenido de flujo de caja.</translation>
    </message>
    <message>
        <source>The table shows monthly snapshots. The cash shortfall banner reports the first day the daily balance drops below zero, which may fall mid-month.</source>
        <translation type="vanished">La tabla muestra instantáneas mensuales. El banner de déficit de tesorería informa del primer día en que el saldo diario cae por debajo de cero, lo que puede ocurrir a mitad de mes.</translation>
    </message>
    <message>
        <source>The balance chart plots your running balance across the projection horizon. The area above zero uses the primary brand color; when the balance drops below zero, the chart fills the deficit region in red so shortfalls stand out visually.</source>
        <translation type="vanished">El gráfico del saldo traza su saldo acumulado a lo largo del horizonte de proyección. El área por encima de cero usa el color principal de la marca; cuando el saldo cae por debajo de cero, el gráfico rellena la región deficitaria en rojo para que los déficits destaquen visualmente.</translation>
    </message>
    <message>
        <source>Move the pointer over the chart to show a vertical guide line, the nearest data point, and a tooltip with the date and balance for that day. This is useful for pinpointing when a decline begins.</source>
        <translation type="vanished">Mueva el puntero sobre el gráfico para mostrar una línea guía vertical, el punto de datos más cercano y una información emergente con la fecha y el saldo de ese día. Es útil para identificar cuándo comienza un descenso.</translation>
    </message>
    <message>
        <source>Use the chart together with the monthly table—the chart shows timing within a month; the table summarizes totals.</source>
        <translation type="vanished">Use el gráfico junto con la tabla mensual — el gráfico muestra el calendario dentro de un mes; la tabla resume totales.</translation>
    </message>
    <message>
        <source>When a projection finds a day with a negative closing balance, a dismissible cash shortfall banner appears at the top of the Projection tab. It names the first shortfall date and the expense cash flow that contributed on that day.</source>
        <translation type="vanished">Cuando una proyección encuentra un día con saldo final negativo, aparece un banner de déficit de tesorería descartable en la parte superior de la pestaña Proyección. Indica la primera fecha de déficit y el flujo de caja de gasto que contribuyó ese día.</translation>
    </message>
    <message>
        <source>Address a shortfall by adjusting timing or amounts on the Cash flows tab, adding income, or opening the Scenario panel to test changes before you commit them. Dismiss the banner when you have noted the date—it reappears on the next run if the shortfall still exists.</source>
        <translation type="vanished">Aborde un déficit ajustando plazos o importes en la pestaña Flujos de caja, añadiendo ingresos o abriendo el panel Escenario para probar cambios antes de confirmarlos. Cierre el banner cuando haya anotado la fecha — reaparecerá en la siguiente ejecución si el déficit persiste.</translation>
    </message>
    <message>
        <source>Only the earliest cash shortfall in a run is reported. Later shortfalls during the same projection are not listed separately.</source>
        <translation type="vanished">Solo se informa del déficit de tesorería más temprano en una ejecución. Los déficits posteriores en la misma proyección no se listan por separado.</translation>
    </message>
    <message>
        <source>Export an executive report after a run to share projection results, including the balance chart, with stakeholders.</source>
        <translation type="vanished">Exporte un informe ejecutivo tras una ejecución para compartir resultados de proyección, incluido el gráfico del saldo, con las partes interesadas.</translation>
    </message>
    <message>
        <source>The Scenario panel on the Projection tab lets you explore what-if changes without altering saved cash flows. Expand the panel to see each active line item with override controls for amount and whether the line is active in the current run.</source>
        <translation type="vanished">El panel Escenario en la pestaña Proyección le permite explorar cambios hipotéticos sin alterar los flujos de caja guardados. Expanda el panel para ver cada partida activa con controles de sustitución de importe y de si la línea está activa en la ejecución actual.</translation>
    </message>
    <message>
        <source>Adjust an amount or deactivate a line, then run the forecast again. The projection engine applies overrides only for that run, leaving your stored forecast unchanged on the Cash flows tab.</source>
        <translation type="vanished">Ajuste un importe o desactive una línea, luego ejecute la previsión de nuevo. El motor de proyección aplica sustituciones solo para esa ejecución, dejando su previsión almacenada sin cambios en la pestaña Flujos de caja.</translation>
    </message>
    <message>
        <source>Use scenarios to test hiring, deferring a payment, or pausing a subscription before you edit the baseline forecast.</source>
        <translation type="vanished">Use escenarios para probar contrataciones, aplazar un pago o pausar una suscripción antes de editar la previsión base.</translation>
    </message>
    <message>
        <source>Scenario overrides are never saved to your forecast. Clear overrides or close the panel to return to the saved baseline.</source>
        <translation type="vanished">Las sustituciones de escenario nunca se guardan en su previsión. Borre las sustituciones o cierre el panel para volver a la base guardada.</translation>
    </message>
    <message>
        <source>After you enable overrides, run the forecast to see updated monthly balances, chart shape, and cash shortfall timing. Compare the results mentally with your last baseline run, or note which line items you changed in the Scenario panel.</source>
        <translation type="vanished">Tras activar sustituciones, ejecute la previsión para ver saldos mensuales, forma del gráfico y calendario de déficit de tesorería actualizados. Compare mentalmente los resultados con su última ejecución base, o anote qué partidas cambió en el panel Escenario.</translation>
    </message>
    <message>
        <source>When you export an executive report while overrides are active, the PDF can include a scenario comparison section that contrasts key metrics between the baseline and the current scenario run.</source>
        <translation type="vanished">Al exportar un informe ejecutivo con sustituciones activas, el PDF puede incluir una sección de comparación de escenarios que contrasta métricas clave entre la base y la ejecución de escenario actual.</translation>
    </message>
    <message>
        <source>Toggle overrides off line by line to isolate which change moved the first cash shortfall date.</source>
        <translation type="vanished">Desactive sustituciones línea por línea para aislar qué cambio movió la primera fecha de déficit de tesorería.</translation>
    </message>
    <message>
        <source>Change history on the forecast detail tab records edits to saved cash flows, not temporary scenario overrides.</source>
        <translation type="vanished">El historial de cambios en la pestaña de detalle de la previsión registra ediciones de flujos de caja guardados, no sustituciones temporales de escenario.</translation>
    </message>
    <message>
        <source>On the Cash flows tab, select Import to open the import dialog. Choose a CSV or Excel file from your computer and map file columns to name, amount, type (income or expense), currency, and date pattern.</source>
        <translation type="vanished">En la pestaña Flujos de caja, seleccione Importar para abrir el diálogo de importación. Elija un archivo CSV o Excel de su equipo y asigne columnas del archivo a nombre, importe, tipo (ingreso o gasto), divisa y patrón de fecha.</translation>
    </message>
    <message>
        <source>Preview the mapped rows before confirming. Rows with invalid patterns or missing required fields are reported so you can fix the source file or adjust mappings. Successful rows are added to the open forecast immediately.</source>
        <translation type="vanished">Vista previa de las filas asignadas antes de confirmar. Las filas con patrones no válidos o campos obligatorios faltantes se informan para que pueda corregir el archivo fuente o ajustar asignaciones. Las filas correctas se añaden de inmediato a la previsión abierta.</translation>
    </message>
    <message>
        <source>Prepare spreadsheets with consistent column headers to speed up mapping—you can re-use the same layout for monthly updates.</source>
        <translation type="vanished">Prepare hojas de cálculo con encabezados de columna coherentes para acelerar la asignación — puede reutilizar el mismo diseño para actualizaciones mensuales.</translation>
    </message>
    <message>
        <source>Import adds cash flows to the current forecast. It does not replace existing lines unless you delete them first.</source>
        <translation type="vanished">La importación añade flujos de caja a la previsión actual. No reemplaza líneas existentes a menos que las elimine primero.</translation>
    </message>
    <message>
        <source>After you run a projection, use Export executive report on the Projection tab to generate a polished PDF for sharing. The report includes a monthly cash-bridge table, a balance chart, foreign-exchange footnotes when applicable, and a methodology appendix.</source>
        <translation type="vanished">Tras ejecutar una proyección, use Exportar informe ejecutivo en la pestaña Proyección para generar un PDF pulido para compartir. El informe incluye una tabla puente de caja mensual, un gráfico del saldo, notas de cambio cuando corresponda y un apéndice de metodología.</translation>
    </message>
    <message>
        <source>If scenario overrides are active, the export may also include a scenario comparison table summarizing how the scenario run differs from the saved baseline. Export CSV is available on the same page for spreadsheet analysis.</source>
        <translation type="vanished">Si hay sustituciones de escenario activas, la exportación puede incluir también una tabla de comparación de escenarios que resume cómo difiere la ejecución de escenario de la base guardada. Exportar CSV está disponible en la misma página para análisis en hoja de cálculo.</translation>
    </message>
    <message>
        <source>Run the forecast immediately before exporting so the report reflects your latest cash flows and horizon.</source>
        <translation type="vanished">Ejecute la previsión inmediatamente antes de exportar para que el informe refleje sus últimos flujos de caja y horizonte.</translation>
    </message>
    <message>
        <source>The executive report describes one forecast run. Re-export after material changes rather than editing the PDF by hand.</source>
        <translation type="vanished">El informe ejecutivo describe una ejecución de previsión. Vuelva a exportar tras cambios materiales en lugar de editar el PDF a mano.</translation>
    </message>
    <message>
        <source>On the Forecasts page, each forecast card offers Export forecast to save a versioned .ftplan bundle. The file contains the forecast metadata, cash flows, and any exchange rates embedded in the bundle for portability.</source>
        <translation type="vanished">En la página Previsiones, cada tarjeta de previsión ofrece Exportar previsión para guardar un paquete .ftplan versionado. El archivo contiene metadatos de la previsión, flujos de caja y tipos de cambio integrados en el paquete para portabilidad.</translation>
    </message>
    <message>
        <source>Use Import forecast on the Forecasts page to create a new forecast from a .ftplan file. This is the recommended way to back up work, move between computers, or share a starting point with a colleague.</source>
        <translation type="vanished">Use Importar previsión en la página Previsiones para crear una nueva previsión desde un archivo .ftplan. Es la forma recomendada de respaldar trabajo, moverse entre equipos o compartir un punto de partida con un colega.</translation>
    </message>
    <message>
        <source>Keep dated .ftplan backups before large restructuring so you can recover an earlier forecast if needed.</source>
        <translation type="vanished">Mantenga copias de seguridad .ftplan fechadas antes de una reestructuración grande para recuperar una previsión anterior si es necesario.</translation>
    </message>
    <message>
        <source>The .ftplan extension is unchanged for compatibility—user-facing labels say Import forecast and Export forecast.</source>
        <translation type="vanished">La extensión .ftplan permanece sin cambios por compatibilidad — las etiquetas visibles dicen Importar previsión y Exportar previsión.</translation>
    </message>
    <message>
        <source>Open Settings from the gear icon in the app header. Under Appearance, toggle Dark mode to switch between light and dark themes. The change applies immediately with no restart required.</source>
        <translation type="vanished">Abra Configuración desde el icono de engranaje en la cabecera. En Apariencia, active Modo oscuro para alternar entre temas claro y oscuro. El cambio se aplica de inmediato sin reinicio.</translation>
    </message>
    <message>
        <source>The Language control lists English, French, Russian, Spanish, and German. Selecting a language retranslates the entire interface, including menus, dialogs, and export headers, in the same session.</source>
        <translation type="vanished">El control Idioma enumera inglés, francés, ruso, español y alemán. Seleccionar un idioma retraduce toda la interfaz, incluidos menús, diálogos y encabezados de exportación, en la misma sesión.</translation>
    </message>
    <message>
        <source>Set language before generating shared PDF exports if recipients expect a particular locale.</source>
        <translation type="vanished">Establezca el idioma antes de generar exportaciones PDF compartidas si los destinatarios esperan una configuración regional concreta.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1130"/>
        <source>Language preference is stored locally in application settings on your device.</source>
        <translation>La preferencia de idioma se almacena localmente en la configuración de la aplicación en su dispositivo.</translation>
    </message>
    <message>
        <source>Exchange rates are managed globally under Data &amp; Currency in Settings. Expand Manage exchange rates to add or edit pairs relative to your forecasts&apos; base currencies. During a projection run, each cash flow in a foreign currency converts using the stored rate before amounts are summed.</source>
        <translation type="vanished">Los tipos de cambio se gestionan globalmente en Datos y divisas en Configuración. Expanda Gestionar tipos de cambio para añadir o editar pares respecto a las divisas base de sus previsiones. Durante una ejecución de proyección, cada flujo de caja en divisa extranjera se convierte con el tipo almacenado antes de sumar importes.</translation>
    </message>
    <message>
        <source>Enable Fetch live exchange rates to download current values when network access is available. Attribution for the rate provider appears on the Settings page. If a required rate is missing, the forecast run fails with an error rather than guessing a value.</source>
        <translation type="vanished">Active Obtener tipos de cambio en vivo para descargar valores actuales cuando haya acceso a red. La atribución del proveedor de tipos aparece en la página Configuración. Si falta un tipo requerido, la ejecución de previsión falla con un error en lugar de estimar un valor.</translation>
    </message>
    <message>
        <source>Refresh live rates before an important projection if markets have moved significantly since your last update.</source>
        <translation type="vanished">Actualice tipos en vivo antes de una proyección importante si los mercados se han movido significativamente desde su última actualización.</translation>
    </message>
    <message>
        <source>Exchange rates apply app-wide. Updating a rate affects every forecast that uses the affected currency pair.</source>
        <translation type="vanished">Los tipos de cambio se aplican en toda la aplicación. Actualizar un tipo afecta a cada previsión que use el par de divisas afectado.</translation>
    </message>
    <message>
        <source>The Methodology page—linked from Settings under About—explains how Cash Flow Planner computes daily balances, detects the first cash shortfall, expands date patterns, and normalizes currencies. It is aimed at readers who want technical transparency.</source>
        <translation type="vanished">La página Metodología — enlazada desde Configuración en Acerca de — explica cómo Cash Flow Planner calcula saldos diarios, detecta el primer déficit de tesorería, expande patrones de fecha y normaliza divisas. Está dirigida a lectores que desean transparencia técnica.</translation>
    </message>
    <message>
        <source>This user manual focuses on day-to-day workflows; the Methodology page complements it with calculation detail. Executive PDF exports also include a methodology appendix for stakeholders who receive reports.</source>
        <translation type="vanished">Este manual de usuario se centra en flujos de trabajo diarios; la página Metodología lo complementa con detalle de cálculo. Las exportaciones PDF ejecutivas también incluyen un apéndice de metodología para las partes interesadas que reciben informes.</translation>
    </message>
    <message>
        <source>Share the Methodology page with clients or partners who ask how projection numbers are produced.</source>
        <translation type="vanished">Comparta la página Metodología con clientes o socios que pregunten cómo se producen las cifras de proyección.</translation>
    </message>
    <message>
        <source>Type patterns exactly as shown in the Pattern column. Trailing dots matter. The app validates syntax and shows a plain-language description under the field while you edit.</source>
        <translation type="vanished">Escriba patrones exactamente como se muestran en la columna Patrón. Los puntos finales importan. La aplicación valida la sintaxis y muestra una descripción en lenguaje claro bajo el campo mientras edita.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1182"/>
        <source>Common date patterns</source>
        <translation>Patrones de fecha comunes</translation>
    </message>
    <message>
        <source>Monthly patterns use day-of-month before the two dots; yearly patterns use day.month.; one-time patterns add the full year.</source>
        <translation type="vanished">Los patrones mensuales usan el día del mes antes de los dos puntos; los anuales usan día.mes.; los puntuales añaden el año completo.</translation>
    </message>
    <message>
        <source>The app shell keeps Forecasts as the home view and Settings one click away in the header. Inside a forecast, switch between Cash flows, Projection, and Change history using the tabs at the top of the detail view.</source>
        <translation type="vanished">La interfaz mantiene Previsiones como vista de inicio y Configuración a un clic en la cabecera. Dentro de una previsión, cambie entre Flujos de caja, Proyección e Historial de cambios con las pestañas en la parte superior de la vista detallada.</translation>
    </message>
    <message>
        <source>Run a projection after every meaningful edit to cash flows or rates so shortfall alerts and charts stay accurate.</source>
        <translation type="vanished">Ejecute una proyección tras cada edición significativa de flujos de caja o tipos para que las alertas de déficit y los gráficos sigan siendo precisos.</translation>
    </message>
    <message>
        <source>Scenario overrides live only on the Projection tab and are cleared when you reset the Scenario panel—they never replace saved cash flows.</source>
        <translation type="vanished">Las sustituciones de escenario viven solo en la pestaña Proyección y se borran al restablecer el panel Escenario — nunca reemplazan los flujos de caja guardados.</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1216"/>
        <source>Every day (daily)</source>
        <translation>Cada día (diario)</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1217"/>
        <source>Monthly on the 10th</source>
        <translation>Mensual el día 10</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1218"/>
        <source>Yearly on 15 March</source>
        <translation>Anual el 15 de marzo</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="1219"/>
        <source>One-time on 15 March 2026</source>
        <translation>Puntual el 15 de marzo de 2026</translation>
    </message>
    <message>
        <location filename="../src/app/i18n/manual_content.py" line="730"/>
        <source>Tips and shortcuts</source>
        <translation>Consejos y atajos</translation>
    </message>
</context>
<context>
    <name>WhatIfPanel</name>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="246"/>
        <source>Collapse</source>
        <translation>Contraer</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="246"/>
        <location filename="../qml/components/WhatIfPanel.qml" line="275"/>
        <source>Scenario</source>
        <translation>Escenario</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="252"/>
        <source>Collapse scenario panel</source>
        <translation>Contraer panel de escenario</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="253"/>
        <source>Expand scenario panel</source>
        <translation>Expandir panel de escenario</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="283"/>
        <source>Override cash flow amounts or active state temporarily without changing saved data.</source>
        <translation>Sustituya temporalmente importes o el estado activo de los flujos de caja sin cambiar los datos guardados.</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="383"/>
        <source>Scenario amount for %1</source>
        <translation>Importe de escenario para %1</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="466"/>
        <source>Scenario active state for %1</source>
        <translation>Estado activo de escenario para %1</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="477"/>
        <source>No cash flows in this forecast.</source>
        <translation>No hay flujos de caja en esta previsión.</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="498"/>
        <location filename="../qml/components/WhatIfPanel.qml" line="510"/>
        <source>Apply scenario</source>
        <translation>Aplicar escenario</translation>
    </message>
    <message>
        <source>What-If</source>
        <translation type="vanished">¿Y si?</translation>
    </message>
    <message>
        <source>Collapse what-if panel</source>
        <translation type="vanished">Contraer panel de escenarios</translation>
    </message>
    <message>
        <source>Expand what-if panel</source>
        <translation type="vanished">Expandir panel de escenarios</translation>
    </message>
    <message>
        <source>What-If Mode</source>
        <translation type="vanished">Modo de escenarios</translation>
    </message>
    <message>
        <source>Override entry amounts or active state temporarily without changing saved data.</source>
        <translation type="vanished">Sustituya temporalmente importes o estado activo de entradas sin cambiar los datos guardados.</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="365"/>
        <source>overridden</source>
        <translation>sustituido</translation>
    </message>
    <message>
        <source>Apply What-If</source>
        <translation type="vanished">Aplicar «¿y si?»</translation>
    </message>
    <message>
        <source>Amount</source>
        <translation type="vanished">Importe</translation>
    </message>
    <message>
        <source>What-if amount for %1</source>
        <translation type="vanished">Importe de escenario para %1</translation>
    </message>
    <message>
        <source>Active</source>
        <translation type="vanished">Activo</translation>
    </message>
    <message>
        <source>What-if active state for %1</source>
        <translation type="vanished">Estado activo de escenario para %1</translation>
    </message>
    <message>
        <source>No entries in this plan.</source>
        <translation type="vanished">No hay entradas en este plan.</translation>
    </message>
    <message>
        <location filename="../qml/components/WhatIfPanel.qml" line="487"/>
        <location filename="../qml/components/WhatIfPanel.qml" line="490"/>
        <source>Clear overrides</source>
        <translation>Borrar sustituciones</translation>
    </message>
    <message>
        <source>Run what-if</source>
        <translation type="vanished">Ejecutar escenario</translation>
    </message>
</context>
<context>
    <name>main</name>
    <message>
        <source>Financial Tracker</source>
        <translation type="vanished">Seguimiento financiero</translation>
    </message>
    <message>
        <location filename="../qml/main.qml" line="15"/>
        <location filename="../qml/main.qml" line="79"/>
        <source>Cash Flow Planner</source>
        <translation>Cash Flow Planner</translation>
    </message>
    <message>
        <location filename="../qml/main.qml" line="89"/>
        <source>Settings</source>
        <translation>Configuración</translation>
    </message>
    <message>
        <location filename="../qml/main.qml" line="123"/>
        <location filename="../qml/main.qml" line="124"/>
        <source>Forecasts</source>
        <translation type="unfinished">Previsiones</translation>
    </message>
    <message>
        <location filename="../qml/main.qml" line="128"/>
        <location filename="../qml/main.qml" line="129"/>
        <source>Spending</source>
        <translation>Gastos</translation>
    </message>
    <message>
        <location filename="../qml/main.qml" line="202"/>
        <source>Dismiss error</source>
        <translation>Descartar error</translation>
    </message>
</context>
</TS>
