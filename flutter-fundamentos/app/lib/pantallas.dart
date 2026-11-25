import 'package:flutter/material.dart';

import 'datos.dart';

/// Ejecuta [accion] después del primer frame cuando la pantalla se abrió con ?auto=1.
void alAbrir(bool auto, VoidCallback accion) {
  if (auto) WidgetsBinding.instance.addPostFrameCallback((_) => accion());
}

// ─────────────────────────────── StatelessWidget ───────────────────────────────

/// Solo dibuja el folio que recibe. No guarda nada que cambie.
class PantallaFolio extends StatelessWidget {
  final String folio;
  const PantallaFolio({super.key, required this.folio});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('StatelessWidget')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Folio del pedido'),
            Text(folio, style: Theme.of(context).textTheme.displaySmall),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────── StatefulWidget ────────────────────────────────

/// Guarda cuántos balones lleva el carrito y se redibuja con setState.
class PantallaContador extends StatefulWidget {
  final bool auto;
  const PantallaContador({super.key, this.auto = false});

  @override
  State<PantallaContador> createState() => _PantallaContadorState();
}

class _PantallaContadorState extends State<PantallaContador> {
  int balones = 0;

  void agregar() => setState(() => balones++);

  @override
  void initState() {
    super.initState();
    alAbrir(widget.auto, () {
      for (var i = 0; i < 3; i++) {
        agregar();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('StatefulWidget')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Balones en el carrito'),
            Text('$balones', style: Theme.of(context).textTheme.displayMedium),
            const SizedBox(height: 16),
            FilledButton.icon(onPressed: agregar, icon: const Icon(Icons.add), label: const Text('Agregar balón')),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────── Scaffold ──────────────────────────────────────

class PantallaEsqueleto extends StatelessWidget {
  const PantallaEsqueleto({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tienda deportiva'), actions: const [Icon(Icons.shopping_cart), SizedBox(width: 16)]),
      drawer: const Drawer(child: Center(child: Text('Menú'))),
      body: const Center(child: Text('Aquí va el contenido de la pantalla')),
      floatingActionButton: FloatingActionButton(onPressed: () {}, child: const Icon(Icons.add)),
      bottomNavigationBar: NavigationBar(
        destinations: const [
          NavigationDestination(icon: Icon(Icons.storefront), label: 'Catálogo'),
          NavigationDestination(icon: Icon(Icons.receipt_long), label: 'Pedidos'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Cuenta'),
        ],
      ),
    );
  }
}

// ─────────────────────────────── ListView ──────────────────────────────────────

class PantallaLista extends StatelessWidget {
  const PantallaLista({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pedidos')),
      body: ListView.separated(
        itemCount: pedidos.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, i) {
          final p = pedidos[i];
          return ListTile(
            leading: CircleAvatar(child: Text('${i + 1}')),
            title: Text(p.articulo),
            subtitle: Text('${p.folio} · ${p.estado}'),
            trailing: Text('\$${p.total.toStringAsFixed(2)}'),
          );
        },
      ),
    );
  }
}

// ─────────────────────────────── Row + Expanded ────────────────────────────────

class PantallaFila extends StatelessWidget {
  final bool conExpanded;
  const PantallaFila({super.key, required this.conExpanded});

  @override
  Widget build(BuildContext context) {
    const nombre = Text('Bicicleta de montaña R29 con suspensión delantera y frenos de disco hidráulicos');
    return Scaffold(
      appBar: AppBar(title: Text(conExpanded ? 'Row con Expanded' : 'Row sin Expanded')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.pedal_bike, size: 40),
            const SizedBox(width: 12),
            if (conExpanded) const Expanded(child: nombre) else nombre,
            const SizedBox(width: 12),
            const Text('\$8,990'),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────── Switch ────────────────────────────────────────

class PantallaSwitch extends StatefulWidget {
  final bool auto;
  const PantallaSwitch({super.key, this.auto = false});

  @override
  State<PantallaSwitch> createState() => _PantallaSwitchState();
}

class _PantallaSwitchState extends State<PantallaSwitch> {
  bool express = false;

  @override
  void initState() {
    super.initState();
    alAbrir(widget.auto, () => setState(() => express = true));
  }

  @override
  Widget build(BuildContext context) {
    final costo = express ? 149 : 0;
    return Scaffold(
      appBar: AppBar(title: const Text('Switch')),
      body: Column(
        children: [
          SwitchListTile(
            title: const Text('Envío express'),
            subtitle: const Text('Llega el mismo día'),
            value: express,
            onChanged: (v) => setState(() => express = v),
          ),
          ListTile(title: const Text('Costo de envío'), trailing: Text('\$$costo')),
        ],
      ),
    );
  }
}

// ─────────────────────────────── Dropdown ──────────────────────────────────────

class PantallaDropdown extends StatefulWidget {
  final bool auto;
  const PantallaDropdown({super.key, this.auto = false});

  @override
  State<PantallaDropdown> createState() => _PantallaDropdownState();
}

class _PantallaDropdownState extends State<PantallaDropdown> {
  String forma = formasDeEnvio.first;

  @override
  void initState() {
    super.initState();
    alAbrir(widget.auto, () => setState(() => forma = formasDeEnvio[2]));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('DropdownButton')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Forma de envío'),
            DropdownButton<String>(
              value: forma,
              isExpanded: true,
              items: [for (final f in formasDeEnvio) DropdownMenuItem(value: f, child: Text(f))],
              onChanged: (v) => setState(() => forma = v!),
            ),
            const SizedBox(height: 16),
            Text('Seleccionaste: $forma'),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────── AlertDialog + SnackBar ────────────────────────

class PantallaAlerta extends StatefulWidget {
  final bool auto;
  const PantallaAlerta({super.key, this.auto = false});

  @override
  State<PantallaAlerta> createState() => _PantallaAlertaState();
}

class _PantallaAlertaState extends State<PantallaAlerta> {
  @override
  void initState() {
    super.initState();
    alAbrir(widget.auto, confirmar);
  }

  Future<void> confirmar() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Confirmar pedido?'),
        content: const Text('Raqueta de tenis grafito · \$2,150.00'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Confirmar')),
        ],
      ),
    );
    if (ok == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Pedido DEP-0009 creado')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AlertDialog')),
      body: Center(child: FilledButton(onPressed: confirmar, child: const Text('Crear pedido'))),
    );
  }
}

// ─────────────────────────────── Navigator ─────────────────────────────────────

class PantallaNavegacion extends StatefulWidget {
  final bool auto;
  const PantallaNavegacion({super.key, this.auto = false});

  @override
  State<PantallaNavegacion> createState() => _PantallaNavegacionState();
}

class _PantallaNavegacionState extends State<PantallaNavegacion> {
  void abrir(Pedido p) =>
      Navigator.push(context, MaterialPageRoute(builder: (_) => DetallePedido(pedido: p)));

  @override
  void initState() {
    super.initState();
    alAbrir(widget.auto, () => abrir(pedidos[1]));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis pedidos')),
      body: ListView(
        children: [
          for (final p in pedidos.take(4))
            ListTile(title: Text(p.folio), subtitle: Text(p.articulo), trailing: const Icon(Icons.chevron_right), onTap: () => abrir(p)),
        ],
      ),
    );
  }
}

class DetallePedido extends StatelessWidget {
  final Pedido pedido;
  const DetallePedido({super.key, required this.pedido});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(pedido.folio)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(pedido.articulo, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text('Cliente: ${pedido.cliente}'),
            Text('Estado: ${pedido.estado}'),
            Text('Total: \$${pedido.total.toStringAsFixed(2)}'),
            const SizedBox(height: 24),
            OutlinedButton.icon(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.arrow_back), label: const Text('Volver')),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────── CircularProgressIndicator ─────────────────────

/// Simula pedir el estado de un folio al servidor: 2 s de espera y luego el resultado.
class PantallaCarga extends StatefulWidget {
  final bool auto;
  final int segundos;
  const PantallaCarga({super.key, this.auto = false, this.segundos = 2});

  @override
  State<PantallaCarga> createState() => _PantallaCargaState();
}

class _PantallaCargaState extends State<PantallaCarga> {
  late Future<String> consulta = consultarEstado();

  Future<String> consultarEstado() async {
    await Future.delayed(Duration(seconds: widget.auto ? 0 : widget.segundos));
    return 'DEP-0002 · En camino · llega en 35 min';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cargando')),
      body: Center(
        child: FutureBuilder<String>(
          future: consulta,
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Column(mainAxisSize: MainAxisSize.min, children: [
                CircularProgressIndicator(),
                SizedBox(height: 12),
                Text('Consultando el pedido…'),
              ]);
            }
            if (snap.hasError) return Text('Error: ${snap.error}');
            return Column(mainAxisSize: MainAxisSize.min, children: [
              Text(snap.data!),
              const SizedBox(height: 12),
              OutlinedButton(onPressed: () => setState(() => consulta = consultarEstado()), child: const Text('Volver a consultar')),
            ]);
          },
        ),
      ),
    );
  }
}
