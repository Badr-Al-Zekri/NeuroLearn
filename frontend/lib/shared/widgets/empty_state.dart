import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/primary_button.dart';

class EmptyState extends StatelessWidget {
  const EmptyState({super.key, required this.title, required this.message, this.actionLabel = 'Choose material'});
  final String title;
  final String message;
  final String actionLabel;

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 440),
      child: GlassPanel(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.menu_book_outlined, size: 40, color: Color(0xFF6DDEC9)),
            const SizedBox(height: 14),
            Text(title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            Text(message, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF9DA9AD), height: 1.45)),
            const SizedBox(height: 20),
            PrimaryButton(label: actionLabel, icon: Icons.upload_file, onPressed: () => context.go('/upload')),
          ],
        ),
      ),
    );
  }
}
