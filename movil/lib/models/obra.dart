// Construction site returned by GET /obras.

class Obra {
  const Obra({
    required this.id,
    required this.nombre,
    this.ubicacion,
    this.fechaInicio,
    this.fechaFin,
  });

  final String id;
  final String nombre;
  final String? ubicacion;
  final DateTime? fechaInicio;
  final DateTime? fechaFin;

  factory Obra.fromJson(Map<String, dynamic> json) => Obra(
        id: json['id']?.toString() ?? '',
        nombre: json['nombre']?.toString() ?? 'Obra sin nombre',
        ubicacion: json['ubicacion']?.toString(),
        fechaInicio: DateTime.tryParse(json['fecha_inicio']?.toString() ?? ''),
        fechaFin: DateTime.tryParse(json['fecha_fin']?.toString() ?? ''),
      );
}
