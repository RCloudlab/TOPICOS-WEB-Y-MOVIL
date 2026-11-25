/// Datos de prueba: pedidos de una tienda de artículos deportivos.
class Pedido {
  final String folio;
  final String articulo;
  final String cliente;
  final double total;
  final String estado;

  const Pedido({
    required this.folio,
    required this.articulo,
    required this.cliente,
    required this.total,
    required this.estado,
  });
}

const pedidos = <Pedido>[
  Pedido(folio: 'DEP-0001', articulo: 'Balón de fútbol No. 5', cliente: 'Ana López', total: 489.00, estado: 'En preparación'),
  Pedido(folio: 'DEP-0002', articulo: 'Raqueta de tenis grafito', cliente: 'Luis Pérez', total: 2150.00, estado: 'En camino'),
  Pedido(folio: 'DEP-0003', articulo: 'Tenis para correr talla 27', cliente: 'María Ruiz', total: 1799.90, estado: 'Entregado'),
  Pedido(folio: 'DEP-0004', articulo: 'Mancuernas 2 × 5 kg', cliente: 'Jorge Díaz', total: 899.00, estado: 'En camino'),
  Pedido(folio: 'DEP-0005', articulo: 'Guantes de box 12 oz', cliente: 'Sofía Mora', total: 749.50, estado: 'En preparación'),
  Pedido(folio: 'DEP-0006', articulo: 'Tapete de yoga 6 mm', cliente: 'Diego Ríos', total: 399.00, estado: 'Entregado'),
  Pedido(folio: 'DEP-0007', articulo: 'Bicicleta de montaña R29', cliente: 'Elena Cruz', total: 8990.00, estado: 'En preparación'),
  Pedido(folio: 'DEP-0008', articulo: 'Casco de ciclismo', cliente: 'Pablo Gil', total: 1250.00, estado: 'En camino'),
];

const formasDeEnvio = ['Paquetería estándar', 'Envío express', 'Recoger en tienda'];
