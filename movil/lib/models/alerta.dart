// Alert returned by GET /alertas.

class Alerta {
  const Alerta({
    required this.id,
    required this.tipo,
    required this.descripcion,
    required this.nivel,
    required this.resuelta,
    this.obraId,
    this.createdAt,
  });

  final String id;
  final String tipo;
  final String descripcion;
  final String nivel;
  final bool resuelta;
  final String? obraId;
  final DateTime? createdAt;

  factory Alerta.fromJson(Map<String, dynamic> json) => Alerta(
        id: json['id']?.toString() ?? '',
        tipo: json['tipo']?.toString() ?? 'seguridad',
        descripcion: json['descripcion']?.toString() ?? '',
        nivel: json['nivel']?.toString() ?? 'baja',
        resuelta: json['resuelta'] as bool? ?? false,
        obraId: json['obra_id']?.toString(),
        createdAt: DateTime.tryParse(json['created_at']?.toString() ?? ''),
      );
}
