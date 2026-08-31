# Patrones de diseño, paradigma y analisis de los patrones - Rodrigo Vega Espinoza
# Tipocios web y movil

## 1. Java
Paradigma: orientado a objetos, con toques funcionales agregados despues.
Patrones tipicos: Singleton, Factory Method, Abstract Factory, Builder, Observer, Decorator, Proxy, Inyeccion de Dependencias.
Java es practicamente el lenguaje de referencia para enseñar patrones de diseño clasicos, porque su sistema de clases e interfaces obliga a que todo se declare de forma explicita, entonces los patrones se ven "limpios" y faciles de identificar.

## 2. C#
Paradigma: orientado a objetos con soporte funcional bastante maduro.
Patrones tipicos: Singleton, Factory, Repository, Unit of Work, Mediator, Inyeccion de Dependencias, Observer.
Los delegados y eventos que trae el lenguaje de forma nativa simplifican mucho la implementacion del patron Observer, cosa que en otros lenguajes toma mas lineas de codigo.

## 3. Python
Paradigma: multiparadigma, mezcla objetos, funciones y dinamismo.
Patrones tipicos: Decorator (con soporte de sintaxis propio), Singleton, Factory, Context Manager, Iterator.
Python tiene la costumbre de meter patrones directo en el lenguaje, ya vienen integrados, entonces uno casi ni nota que esta usando un patron formal cuando en realidad si lo esta haciendo.

## 4. JavaScript
Paradigma: multiparadigma, basado en prototipos, con funciones de primera clase.
Patrones tipicos: Module Pattern, Observer o Pub Sub, Prototype, Singleton, Factory Function.
Como JavaScript no usa clases reales por debajo (aunque lo aparente), el patron Prototype no es opcional aqui, es literalmente el mecanismo con el que funciona la herencia del lenguaje, algo bastante distinto a lo que pasa en Java o C#.

## 5. TypeScript
Paradigma: orientado a objetos y funcional, apoyado sobre JavaScript con tipado estatico.
Patrones tipicos: Decorator, Inyeccion de Dependencias, Factory basada en genericos, Strategy basada en interfaces.
Los tipos estaticos permiten aplicar los patrones clasicos con mucha mas seguridad, cosa que en JavaScript puro es mas riesgosa porque todo se descubre en tiempo de ejecucion.

## 6. C++
Paradigma: multiparadigma, procedural, orientado a objetos y generico.
Patrones tipicos: RAII, Singleton, Factory, PIMPL, Visitor, y un patron de polimorfismo estatico basado en templates.
C++ trae patrones propios que no existen en lenguajes con recolector de basura, porque ahi uno tiene que manejar la memoria manualmente y eso obliga a inventar soluciones adicionales.

## 7. Ruby
Paradigma: orientado a objetos puro, muy dinamico, con metaprogramacion fuerte.
Patrones tipicos: Modulos o Mixins, Duck Typing en lugar de Strategy formal, Builder mediante lenguajes internos del dominio, Observer.
Ruby prefiere resolver las cosas con metaprogramacion antes que meterse en un patron rigido, muchas veces un problema que en Java requeriria un patron completo aqui se resuelve con un mixin de tres lineas.

## 8. Go
Paradigma: procedural y orientado a objetos sin herencia, todo gira en torno a composicion e interfaces implicitas.
Patrones tipicos: Composicion sobre herencia como principio central, patron de opciones funcionales, grupos de trabajo para concurrencia, Strategy via interfaces.
Go decidio, a proposito, eliminar la herencia de clases, entonces varios patrones clasicos de GoF que dependen de jerarquias simplemente no aplican aqui y se resuelven distinto.

## 9. Rust
Paradigma: multiparadigma centrado en seguridad de memoria, sin herencia clasica de clases.
Patrones tipicos: Builder (muy comun porque todo es inmutable por defecto), un patron propio llamado Newtype, Typestate, Strategy via traits, RAII.
El sistema de propiedad de Rust hace innecesarios varios patrones que en otros lenguajes sirven para controlar memoria compartida, porque el compilador ya obliga a pensar eso desde el diseño.

## 10. Kotlin
Paradigma: orientado a objetos y funcional, pensado para interoperar con Java.
Patrones tipicos: Singleton con soporte de palabra clave propia, Builder simplificado, Delegation con soporte nativo, clases selladas para Visitor o State.
Kotlin agarra varios patrones de GoF y los convierte directamente en palabras clave del lenguaje, entonces uno escribe mucho menos codigo repetitivo comparado con Java.

## 11. Swift
Paradigma: orientado a protocolos, con soporte funcional.
Patrones tipicos: diseño orientado a protocolos en lugar de Strategy clasico, patron Delegate muy usado en el ecosistema de Apple, Singleton, Observer mediante el framework reactivo del lenguaje.
Swift empuja fuerte hacia diseñar con protocolos y extensiones en vez de jerarquias de clases, lo cual cambia bastante el enfoque tradicional de los patrones GoF.

## 12. PHP
Paradigma: orientado a objetos desde hace ya varias versiones, y tambien procedural.
Patrones tipicos: modelo vista controlador, Active Record, Singleton, Factory, Repository, contenedor de servicios para inyeccion de dependencias.
Los frameworks modernos de PHP institucionalizan patrones arquitectonicos completos, ya vienen armados desde que uno crea el proyecto, no hay que pensarlos desde cero.

## 13. Scala
Paradigma: hibrido, mezcla objetos y funcional puro.
Patrones tipicos: coincidencia de patrones que sustituye a Visitor, patrones tipo Monad y Functor, Type Class, objeto compañero para Factory o Singleton.
Scala combina los dos mundos, entonces muchos patrones estructurales clasicos terminan reescritos como combinadores funcionales en lugar de clases con herencia.

## 14. Haskell
Paradigma: funcional puro, evaluacion perezosa, tipado muy fuerte.
Patrones tipicos: Monad como patron central para manejar efectos, Functor, Applicative, Type Class en lugar de interfaces tradicionales.
Haskell es probablemente el ejemplo mas extremo de un lenguaje que reemplaza casi todo el catalogo GoF por construcciones matematicas, aqui ya ni se piensa en "aplicar un patron" de la forma clasica.

## 15. Elixir
Paradigma: funcional, concurrente, basado en el modelo de actores.
Patrones tipicos: modelo de actores que sustituye a Observer con estado, arbol de supervision propio para tolerancia a fallos, patron de tuberia para encadenar funciones, coincidencia de patrones.
El modelo de actores resuelve de forma nativa cosas que en objetos requeririan Observer o Mediator, y de paso evita el dolor de cabeza de los locks manuales.

## 16. Clojure
Paradigma: funcional, dialecto de Lisp, inmutable por defecto.
Patrones tipicos: multimetodos en lugar de Visitor o Strategy, protocolos como interfaces livianas, memoria transaccional en lugar de sincronizacion manual.
La inmutabilidad de Clojure, junto con su forma tan particular de tratar el codigo como datos, elimina de raiz varios patrones pensados para controlar estado mutable compartido.

## 17. React
Paradigma: declarativo, basado en componentes, con flujo de datos en una sola direccion.
Patrones tipicos: Composite para armar componentes, Observer para el manejo de estado, un patron propio llamado Hooks que reemplazo a soluciones anteriores, Provider para inyeccion de contexto.
Es interesante ver como React primero popularizo ciertos patrones y despues, con el tiempo, los reemplazo por otros propios, mostrando que hasta los frameworks generan y luego abandonan sus propios patrones.

## 18. Angular
Paradigma: orientado a objetos, arquitectura basada en componentes con vista y modelo separados.
Patrones tipicos: Inyeccion de Dependencias como nucleo del framework, Singleton para servicios, Observer mediante programacion reactiva, Decorator.
Angular convierte la inyeccion de dependencias en algo obligatorio, no opcional, cosa que en otros frameworks queda a criterio del desarrollador.

## 19. Spring
Paradigma: orientado a objetos, con inversion de control como filosofia central.
Patrones tipicos: contenedor de inversion de control, Proxy para manejar transacciones, Template Method para plantillas de acceso a datos, Factory, Singleton por defecto en sus componentes.
Spring es casi un catalogo viviente de patrones aplicados a nivel de framework empresarial, es dificil encontrar un patron clasico que no este presente de alguna forma.

## 20. Django
Paradigma: orientado a objetos, arquitectura de modelo vista plantilla, variante del clasico modelo vista controlador.
Patrones tipicos: Active Record para el manejo de la base de datos, Factory para los administradores de modelos, Template Method para vistas basadas en clases, cadena de responsabilidad para el sistema de middleware, Singleton para la configuracion global.
Django aplica el patron de cadena de responsabilidad de forma bastante explicita en su sistema de middleware, cada solicitud pasa por una fila de procesos antes de llegar a su destino.

## Analisis ¿Que determina el patron dominante de cada lenguaje?

Viendo los veinte casos juntos, se nota un patron (valga la redundancia) bastante claro, y es que la eleccion de patrones no depende tanto del gusto del programador sino de decisiones de diseño que ya vienen tomadas desde que se creo el lenguaje. Los lenguajes que nacieron pensando en clases y jerarquias, como Java, C# o PHP en su version moderna, terminan gravitando hacia el catalogo clasico casi por default, porque su sintaxis fue pensada para eso desde el principio.

En cambio los lenguajes que aparecieron despues, con otras prioridades, empezaron a absorber patrones dentro de su propia sintaxis, en vez de dejarlos como algo que el programador tiene que armar a mano. Python con sus decoradores y sus manejadores de contexto es el ejemplo mas claro, Kotlin igual, convirtiendo Singleton o Delegation en palabras reservadas. Esto no es casualidad, es una tendencia, entre mas joven es el lenguaje, mas tiende a integrar el patron como caracteristica nativa en lugar de dejarlo como un ejercicio de diseño manual.

Tambien hay algo curioso con los frameworks, porque a diferencia de los lenguajes, los frameworks no solo usan patrones, los imponen. Spring y Angular por ejemplo casi obligan a trabajar con inyeccion de dependencias, no es opcional, es la forma en que el framework espera que uno construya las cosas. Esto genera una diferencia importante, un lenguaje te ofrece herramientas y tu decides, un framework ya viene con una filosofia de diseño incrustada y hay que adaptarse a ella si o si.

Otra cosa que vale la pena mencionar, entre mas dinamico es un lenguaje (Ruby, Python, JavaScript) menos necesidad hay de patrones formales rigidos, porque el propio dinamismo del lenguaje resuelve el problema de otra manera, casi siempre con metaprogramacion o con tipado flexible. Mientras que entre mas estatico y estricto es el lenguaje (C++, Rust, Java) mas se recurre a patrones explicitos, porque el compilador exige que todo este declarado de antemano.

## Analisis ¿Por que ciertos paradigmas terminan rompiendo patrones clasicos?

Aqui hay algo importante que se suele pasar por alto, y es que "romper" un patron no siempre significa que el patron este mal, sino que el paradigma resuelve el problema original de raiz, entonces el patron simplemente deja de tener sentido, se vuelve innecesario en ese contexto.

El caso mas contundente es el de los lenguajes funcionales puros, Haskell, Elixir y Clojure entran aqui. El patron Singleton, por ejemplo, existe historicamente para controlar una sola instancia de estado mutable compartido, pero si el lenguaje ya es inmutable por diseño, ese problema de origen simplemente no existe, entonces no hace falta el patron para resolverlo, es una solucion para un problema que ya fue eliminado desde la raiz del lenguaje.

Algo parecido pasa con Observer en los entornos reactivos, como Angular o Swift con su framework reactivo. El patron sigue existiendo conceptualmente, pero ya no se escribe a mano, queda envuelto dentro de operadores reactivos, entonces el programador deja de pensar en terminos de "sujeto y observador" y empieza a pensar en flujos de datos que se transforman, es el mismo problema resuelto desde otro angulo.

Con los lenguajes basados en composicion como Go, o basados en prototipos como JavaScript, lo que se rompe son los patrones que dependen de jerarquias de herencia, cosas como Template Method clasico o Abstract Factory con herencia profunda. Si el lenguaje no tiene herencia de implementacion, esos patrones no se pueden aplicar tal cual estan descritos en el catalogo original, hay que rediseñarlos usando composicion o interfaces implicitas, que terminan siendo soluciones distintas al mismo problema.

Y despues esta el caso de Rust, que es interesante porque no es que el paradigma haga innecesario al patron, sino que el compilador directamente impide ciertos usos descuidados de patrones como Singleton mutable global, obligando al programador a modelar la propiedad de los datos de forma explicita desde el principio, entonces el patron termina transformado en algo mas seguro, no eliminado del todo pero si forzado a evolucionar.

En resumen, se podria decir que un patron de diseño desaparece o se transforma cuando el paradigma del lenguaje resuelve el problema original desde una capa mas profunda, ya sea por inmutabilidad, por composicion, por tipado o por control de memoria, y eso es justamente lo que hace que el estudio de patrones no pueda separarse nunca del estudio del paradigma que hay detras.

