// Obras tab: lists construction sites as cards.

import 'package:flutter/material.dart';

import '../models/obra.dart';
import '../services/api_service.dart';

class ObrasScreen extends StatefulWidget {
  const ObrasScreen({super.key});

  @override
  State<ObrasScreen> createState() => _ObrasScreenState();
}

class _ObrasScreenState extends State<ObrasScreen> {
  late Future<List<Obra>> _obras;

  @override
  void initState() {
    super.initState();
    _recargar();
  }

  void _recargar() {
    if (!mounted) return;
    setState(() {
      _obras = fetchList('/obras').then(
        (rows) => rows
            .whereType<Map<String, dynamic>>()
            .map(Obra.fromJson)
            .toList(),
      );
    });
  }

  String _fecha(DateTime? value) {
    if (value == null) return '—';
    final local = value.toLocal();
    return '${local.day.toString().padLeft(2, '0')}/'
        '${local.month.toString().padLeft(2, '0')}/${local.year}';
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
                  'Obras registradas',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                onPressed: _recargar,
                icon: const Icon(Icons.refresh),
                tooltip: 'Actualizar obras',
              ),
            ],
          ),
        ),
        Expanded(
          child: FutureBuilder<List<Obra>>(
            future: _obras,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Center(child: Text('Error: ${snapshot.error}'));
              }
              final obras = snapshot.data ?? const <Obra>[];
              if (obras.isEmpty) {
                return const Center(child: Text('No hay obras registradas.'));
              }
              return ListView.builder(
                padding: const EdgeInsets.only(bottom: 16),
                itemCount: obras.length,
                itemBuilder: (context, index) {
                  final obra = obras[index];
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(
                                Icons.construction,
                                color: Color(0xFF3B82F6),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  obra.nombre,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          if (obra.ubicacion != null &&
                              obra.ubicacion!.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.place_outlined, size: 16),
                                const SizedBox(width: 8),
                                Expanded(child: Text(obra.ubicacion!)),
                              ],
                            ),
                          ],
                          const SizedBox(height: 8),
                          Text(
                            '${_fecha(obra.fechaInicio)} — ${_fecha(obra.fechaFin)}',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
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
