// Camera tab: captures a photo and queues it for later upload.

import 'dart:async';
import 'dart:io';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import '../models/foto_pendiente.dart';
import '../services/db_service.dart';
import '../services/sync_service.dart';

class CapturaScreen extends StatefulWidget {
  const CapturaScreen({super.key});

  @override
  State<CapturaScreen> createState() => _CapturaScreenState();
}

class _CapturaScreenState extends State<CapturaScreen> {
  final ImagePicker _picker = ImagePicker();
  late Future<List<FotoPendiente>> _fotos;
  late final StreamSubscription<List<ConnectivityResult>> _conexionSub;
  bool _conectado = false;
  bool _tomando = false;
  bool _sincronizando = false;

  @override
  void initState() {
    super.initState();
    _fotos = obtenerFotosPendientes();
    _verificarConexion();
    _conexionSub = Connectivity().onConnectivityChanged.listen((resultados) {
      if (!mounted) return;
      setState(() => _conectado = _hayRed(resultados));
    });
  }

  @override
  void dispose() {
    _conexionSub.cancel();
    super.dispose();
  }

  bool _hayRed(List<ConnectivityResult> resultados) =>
      resultados.any((resultado) => resultado != ConnectivityResult.none);

  Future<void> _verificarConexion() async {
    final resultados = await Connectivity().checkConnectivity();
    if (!mounted) return;
    setState(() => _conectado = _hayRed(resultados));
  }

  void _recargar() {
    if (!mounted) return;
    setState(() {
      _fotos = obtenerFotosPendientes();
    });
  }

  void _avisar(String mensaje) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(mensaje)),
    );
  }

  Future<void> _tomarFoto() async {
    setState(() => _tomando = true);
    try {
      final XFile? foto = await _picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
      );
      if (foto == null) return;

      final directorio = await getApplicationDocumentsDirectory();
      final nombre = 'foto_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final destino = File(p.join(directorio.path, nombre));
      await destino.writeAsBytes(await foto.readAsBytes());

      await insertarFoto(
        FotoPendiente(path: destino.path, timestamp: DateTime.now()),
      );
      _recargar();
      _avisar('Foto guardada localmente. Pendiente de sincronizar');
    } catch (error) {
      _avisar('No se pudo guardar la foto: $error');
    } finally {
      if (mounted) {
        setState(() => _tomando = false);
      }
    }
  }

  Future<void> _sincronizar() async {
    setState(() => _sincronizando = true);
    try {
      final enviadas = await sincronizarFotos();
      _recargar();
      if (enviadas > 0) {
        _avisar('$enviadas foto(s) sincronizada(s) correctamente.');
      } else {
        _avisar('No hay conexión o no hay fotos pendientes.');
      }
    } catch (error) {
      _avisar(
        'No se pudo sincronizar: ${error.toString().replaceFirst('StateError: ', '')}',
      );
    } finally {
      if (mounted) {
        setState(() => _sincronizando = false);
      }
    }
  }

  String _hora(DateTime value) {
    final local = value.toLocal();
    return '${local.day.toString().padLeft(2, '0')}/'
        '${local.month.toString().padLeft(2, '0')}/'
        '${local.year} ${local.hour.toString().padLeft(2, '0')}:'
        '${local.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final colorConectado = _conectado
        ? const Color(0xFF22C55E)
        : const Color(0xFFEF4444);

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              margin: EdgeInsets.zero,
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
                child: Row(
                  children: [
                    Icon(
                      _conectado ? Icons.wifi : Icons.wifi_off,
                      color: colorConectado,
                    ),
                    const SizedBox(width: 10),
                    Text(
                      _conectado ? 'Conectado' : 'Sin conexión',
                      style: TextStyle(color: colorConectado),
                    ),
                    const Spacer(),
                    IconButton(
                      onPressed: _recargar,
                      icon: const Icon(Icons.refresh),
                      tooltip: 'Actualizar lista',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _tomando ? null : _tomarFoto,
                icon: _tomando
                    ? const SizedBox(
                        height: 24,
                        width: 24,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.camera_alt, size: 32),
                label: const Text(
                  'Tomar Foto',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF3B82F6),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Fotos pendientes',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: _sincronizando ? null : _sincronizar,
                  icon: _sincronizando
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.cloud_upload_outlined),
                  label: const Text('Sincronizar Ahora'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Expanded(
              child: FutureBuilder<List<FotoPendiente>>(
                future: _fotos,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return Center(child: Text('Error: ${snapshot.error}'));
                  }
                  final fotos = snapshot.data ?? const <FotoPendiente>[];
                  if (fotos.isEmpty) {
                    return const Center(
                      child: Text('No hay fotos pendientes.'),
                    );
                  }
                  return ListView.builder(
                    itemCount: fotos.length,
                    itemBuilder: (context, index) {
                      final foto = fotos[index];
                      return Card(
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: const Color(0xFFF59E0B)
                                .withValues(alpha: 0.18),
                            child: const Icon(
                              Icons.schedule,
                              color: Color(0xFFF59E0B),
                            ),
                          ),
                          title: Text(p.basename(foto.path)),
                          subtitle: Text(_hora(foto.timestamp)),
                          trailing: const Icon(
                            Icons.cloud_off_outlined,
                            color: Colors.grey,
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
