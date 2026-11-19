// Stores the JWT shared by login and sync, and owns the configured API client.

import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config.dart';

const String _tokenKey = 'supervisor_ia_token';

/// Render's free plan can take ~1 min to wake up after inactivity.
const Duration apiTimeout = Duration(seconds: 120);

/// Single client shared by login and sync (connection pooling + timeouts).
final http.Client apiClient = http.Client();

/// Performs POST /login with explicit JSON headers and stores the returned JWT.
Future<String> iniciarSesion(String email, String password) async {
  final response = await apiClient
      .post(
        Uri.parse('$apiUrl/login'),
        headers: const {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({'email': email, 'password': password}),
      )
      .timeout(apiTimeout);

  if (response.statusCode != 200) {
    throw StateError('No se pudo iniciar sesión (${response.statusCode}).');
  }

  final body = jsonDecode(response.body) as Map<String, dynamic>;
  final token = body['access_token'] as String?;
  if (token == null || token.isEmpty) {
    throw StateError('El servidor no devolvió un token.');
  }
  await guardarToken(token);
  return token;
}

Future<void> guardarToken(String token) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(_tokenKey, token);
}

Future<String?> obtenerToken() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(_tokenKey);
}

Future<void> limpiarToken() async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.remove(_tokenKey);
}
