import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:neurolearn_ai/app/theme.dart';

class AppShell extends StatelessWidget {
  const AppShell({super.key, required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width >= 900;
    final currentPath = GoRouterState.of(context).uri.path;
    final choosingMaterial = currentPath == '/upload';
    return Scaffold(
      backgroundColor: const Color(0xFF0B0E10),
      bottomNavigationBar: wide || choosingMaterial ? null : _MobileNavigation(currentPath: currentPath),
      body: ColoredBox(
        color: const Color(0xFF0B0E10),
        child: Row(
          children: [
            if (wide) SizedBox(width: 268, child: _Sidebar()),
            Expanded(
              child: Column(
                children: [
                  if (!wide)
                    AppBar(
                      backgroundColor: const Color(0xFF0B0E10),
                      elevation: 0,
                      leading: choosingMaterial
                          ? IconButton(
                              tooltip: 'Back to Today',
                              onPressed: () => context.go('/'),
                              icon: const Icon(Icons.arrow_back),
                            )
                          : null,
                      title: const Text('NeuroLearn', style: TextStyle(fontWeight: FontWeight.w800)),
                    ),
                  Expanded(
                    child: AnimatedSwitcher(
                      duration: const Duration(milliseconds: 260),
                      child: child,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Sidebar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: const BoxDecoration(
          color: surface,
          border: Border(right: BorderSide(color: border)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(color: accent.withValues(alpha: 0.16), borderRadius: BorderRadius.circular(8)),
                  child: const Icon(LucideIcons.brainCircuit, color: accent),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text('NeuroLearn AI', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                ),
              ],
            ),
            const SizedBox(height: 28),
            _NavItem(path: '/', icon: Icons.today_outlined, label: 'Today'),
            _NavItem(path: '/tutor', icon: Icons.forum_outlined, label: 'Tutor'),
            _NavItem(path: '/practice', icon: Icons.quiz_outlined, label: 'Practice'),
            _NavItem(path: '/progress', icon: Icons.trending_up_outlined, label: 'Progress'),
            const Spacer(),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF111827),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: border),
              ),
              child: const Text(
                'A quiet daily study companion. Start small, learn clearly, return tomorrow.',
                style: TextStyle(color: Color(0xFF99A6AB), height: 1.4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MobileNavigation extends StatelessWidget {
  const _MobileNavigation({required this.currentPath});
  final String currentPath;

  @override
  Widget build(BuildContext context) {
    const paths = ['/', '/tutor', '/practice', '/progress'];
    final index = paths.contains(currentPath) ? paths.indexOf(currentPath) : 0;
    return NavigationBar(
      selectedIndex: index,
      onDestinationSelected: (selectedIndex) => context.go(paths[selectedIndex]),
      destinations: const [
        NavigationDestination(icon: Icon(Icons.today_outlined), selectedIcon: Icon(Icons.today), label: 'Today'),
        NavigationDestination(icon: Icon(Icons.forum_outlined), selectedIcon: Icon(Icons.forum), label: 'Tutor'),
        NavigationDestination(icon: Icon(Icons.quiz_outlined), selectedIcon: Icon(Icons.quiz), label: 'Practice'),
        NavigationDestination(icon: Icon(Icons.trending_up_outlined), selectedIcon: Icon(Icons.trending_up), label: 'Progress'),
      ],
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({required this.path, required this.icon, required this.label});
  final String path;
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final selected = GoRouterState.of(context).uri.path == path;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        selected: selected,
        selectedTileColor: accent.withValues(alpha: 0.12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        leading: Icon(icon, color: selected ? accent : const Color(0xFF9CA8C7)),
        title: Text(label, style: TextStyle(color: selected ? Colors.white : const Color(0xFFB8C2DD), fontWeight: FontWeight.w700)),
        onTap: () {
          if (Scaffold.maybeOf(context)?.hasDrawer ?? false) {
            Navigator.of(context).pop();
          }
          context.go(path);
        },
      ),
    );
  }
}
