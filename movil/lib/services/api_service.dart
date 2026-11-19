// Authenticated GET helper shared by the Alertas and Obras tabs.

import 'dart:convert';

import '../config.dart';
import 'auth_service.dart';

Future<List<dynamic>> fetchList(String path) async {
  final token = await obtenerToken();
  if (token == null) {
    throw StateError('No hay sesión activa. Ingresa nuevamente.');
  }

  final response = await apiClient
      .get(
        Uri.parse('$apiUrl$path'),
        headers: {
          'Authorization': 'Bearer $token',
          'Accept': 'application/json',
        },
      )
      .timeout(apiTimeout);

  if (response.statusCode != 200) {
    throw StateError('No se pudo cargar la información (${response.statusCode}).');
  }

  final decoded = jsonDecode(response.body);
  if (decoded is! List) {
    throw StateError('Respuesta inesperada del servidor.');
  }
  return decoded;
}
