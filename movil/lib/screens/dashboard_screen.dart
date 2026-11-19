// Dashboard shell: three tabs with a shared AppBar and logout action.

import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import 'alertas_screen.dart';
import 'captura_screen.dart';
import 'login_screen.dart';
import 'obras_screen.dart';

const List<String> _titulos = ['Captura', 'Alertas', 'Obras'];

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _indice = 0;

  Future<void> _cerrarSesion() async {
    await limpiarToken();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil<void>(
      MaterialPageRoute<void>(builder: (_) => const LoginScreen()),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titulos[_indice]),
        actions: [
          IconButton(
            onPressed: _cerrarSesion,
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
          ),
        ],
      ),
      body: IndexedStack(
        index: _indice,
        children: const [
          CapturaScreen(),
          AlertasScreen(),
          ObrasScreen(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _indice,
        onTap: (indice) => setState(() => _indice = indice),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.camera_alt_outlined),
            activeIcon: Icon(Icons.camera_alt),
            label: 'Captura',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.notifications_none_outlined),
            activeIcon: Icon(Icons.notifications),
            label: 'Alertas',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.construction_outlined),
            activeIcon: Icon(Icons.construction),
            label: 'Obras',
          ),
        ],
      ),
    );
  }
}
