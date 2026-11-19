// Alertas tab: lists backend alerts colour-coded by severity.

import 'package:flutter/material.dart';

import '../models/alerta.dart';
import '../services/api_service.dart';

class AlertasScreen extends StatefulWidget {
  const AlertasScreen({super.key});

  @override
  State<AlertasScreen> createState() => _AlertasScreenState();
}

class _AlertasScreenState extends State<AlertasScreen> {
  late Future<List<Alerta>> _alertas;

  @override
  void initState() {
    super.initState();
    _recargar();
  }

  void _recargar() {
    if (!mounted) return;
    setState(() {
      _alertas = fetchList('/alertas').then(
        (rows) => rows
            .whereType<Map<String, dynamic>>()
            .map(Alerta.fromJson)
            .toList(),
      );
    });
  }

  Color _colorNivel(String nivel) {
    switch (nivel.toLowerCase()) {
      case 'alta':
        return const Color(0xFFEF4444);
      case 'media':
        return const Color(0xFFF59E0B);
      default:
        return const Color(0xFF22C55E);
    }
  }

  String _fecha(DateTime? value) {
    if (value == null) return '';
    final local = value.toLocal();
    return '${local.day.toString().padLeft(2, '0')}/'
        '${local.month.toString().padLeft(2, '0')}/'
        '${local.year} ${local.hour.toString().padLeft(2, '0')}:'
        '${local.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 8, 4),
          child: Row(
            children: [
              const Expanded(
                child: Text(
                  'Alertas recientes',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                onPressed: _recargar,
                icon: const Icon(Icons.refresh),
                tooltip: 'Actualizar alertas',
              ),
            ],
          ),
        ),
        Expanded(
          child: FutureBuilder<List<Alerta>>(
            future: _alertas,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Center(child: Text('Error: ${snapshot.error}'));
              }
              final alertas = snapshot.data ?? const <Alerta>[];
              if (alertas.isEmpty) {
                return const Center(child: Text('No hay alertas registradas.'));
              }
              return ListView.builder(
                padding: const EdgeInsets.only(bottom: 16),
                itemCount: alertas.length,
                itemBuilder: (context, index) {
                  final alerta = alertas[index];
                  final color = _colorNivel(alerta.nivel);
                  return Card(
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: color.withValues(alpha: 0.18),
                        child: Icon(Icons.warning_amber_rounded, color: color),
                      ),
                      title: Text(alerta.descripcion),
                      subtitle: Text(
                        [
                          alerta.nivel.toUpperCase(),
                          alerta.tipo,
                          _fecha(alerta.createdAt),
                        ].where((part) => part.isNotEmpty).join(' · '),
                      ),
                      trailing: Icon(
                        alerta.resuelta
                            ? Icons.check_circle
                            : Icons.radio_button_unchecked,
                        color: alerta.resuelta
                            ? const Color(0xFF22C55E)
                            : Colors.grey,
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ],
    );
  }
}
