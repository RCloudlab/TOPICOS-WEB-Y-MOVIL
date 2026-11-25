import 'package:flutter/material.dart';

import 'pantallas.dart';

void main() => runApp(const AppFundamentos());

/// Rutas de la práctica. En web se puede abrir cada una directo:
/// http://localhost:PUERTO/#/contador
/// `?auto=1` dispara la acción de la pantalla al abrirla (para las capturas).
/// `/carga?espera=N` cambia los segundos que tarda la consulta simulada.
final rutas = <String, Widget Function(bool auto, Map<String, String> q)>{
  '/stateless': (_, _) => const PantallaFolio(folio: 'DEP-0001'),
  '/contador': (auto, _) => PantallaContador(auto: auto),
  '/esqueleto': (_, _) => const PantallaEsqueleto(),
  '/lista': (_, _) => const PantallaLista(),
  '/fila': (_, _) => const PantallaFila(conExpanded: true),
  '/fila-sin-expanded': (_, _) => const PantallaFila(conExpanded: false),
  '/switch': (auto, _) => PantallaSwitch(auto: auto),
  '/dropdown': (auto, _) => PantallaDropdown(auto: auto),
  '/alerta': (auto, _) => PantallaAlerta(auto: auto),
  '/navegacion': (auto, _) => PantallaNavegacion(auto: auto),
  '/carga': (auto, q) => PantallaCarga(auto: auto, segundos: int.tryParse(q['espera'] ?? '') ?? 2),
};

class AppFundamentos extends StatelessWidget {
  const AppFundamentos({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tienda deportiva · Fundamentos',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: const Color(0xFF0B7A3E), useMaterial3: true),
      onGenerateRoute: (settings) {
        final uri = Uri.parse(settings.name ?? '/');
        final auto = uri.queryParameters['auto'] == '1';
        final crear = rutas[uri.path];
        return MaterialPageRoute(
          settings: settings,
          builder: (_) => crear != null ? crear(auto, uri.queryParameters) : const Menu(),
        );
      },
    );
  }
}

class Menu extends StatelessWidget {
  const Menu({super.key});

  static const titulos = {
    '/stateless': 'StatelessWidget: folio',
    '/contador': 'StatefulWidget: contador',
    '/esqueleto': 'Scaffold: esqueleto de pantalla',
    '/lista': 'ListView: lista de pedidos',
    '/fila': 'Row + Expanded',
    '/fila-sin-expanded': 'Row sin Expanded (overflow)',
    '/switch': 'Switch: envío express',
    '/dropdown': 'DropdownButton: forma de envío',
    '/alerta': 'AlertDialog + SnackBar',
    '/navegacion': 'Navigator: lista → detalle',
    '/carga': 'CircularProgressIndicator',
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fundamentos de Flutter')),
      body: ListView(
        children: [
          for (final e in titulos.entries)
            ListTile(
              title: Text(e.value),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.pushNamed(context, e.key),
            ),
        ],
      ),
    );
  }
}
