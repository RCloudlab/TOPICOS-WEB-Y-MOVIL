# Notas del día 3

Lo primero que resolví fue el tema de cómo planear cada medio sin llenar `registrar_pedido` de ifs. Eso es Strategy: cada medio (camioneta, moto, bici, dron) tiene su propio `planear()` y el servicio nomás llama `medio.planear(...)` sin saber cuál le tocó. No es Factory porque no estoy creando el objeto, ya lo tengo, solo varía cómo calcula el plan. Tampoco es Adapter, porque aquí no traduzco nada ajeno, todos hablan el mismo idioma. Y no es State porque el medio no va cambiando solo con el tiempo, se elige una vez y ya.

Lo otro era la IA: cada proveedor regresa su formato raro (uno JSON con route_hint y score, el otro XML con <vehicle>) y yo no quiero que eso se me riegue por todo el código. Por eso el Adapter: cada proveedor tiene su adaptador que traduce a Sugerencia(medio, motivo), que es lo único que entiende mi dominio. route_hint, score, vehicle y el parseo de XML solo existen dentro de esos dos adaptadores. No es Facade porque Facade es para simplificar algo mío, aquí el otro lado ni siquiera lo controlo, solo lo traduzco.

Y para pasar del string de la sugerencia ("dron", "moto"...) a la clase que toca, hice una fábrica simple, un diccionario y un if no existe. No metí Factory Method porque ese patrón es para cuando hay familias que redefinen un método distinto cada una, y aquí no hay tal cosa, sería inventar clases de más nomás por poner un patrón con nombre bonito.

Si mañana meten un quinto medio: nueva clase en medios.py y una línea en el diccionario de fabrica.py, nada más.

Si el proveedor de IA cambia route_hint por vehicle: solo se toca su adaptador en ia.py, todo lo demás ni se entera.
