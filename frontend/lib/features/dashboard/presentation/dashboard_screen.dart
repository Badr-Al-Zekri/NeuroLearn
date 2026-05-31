import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/metric_card.dart';
import 'package:neurolearn_ai/shared/widgets/primary_button.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final document = ref.watch(selectedDocumentProvider);
    return SingleChildScrollView(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionHeader(
            title: 'AI study workspace',
            subtitle: 'Upload learning material, generate a focused brief, practice with quizzes, then chat with the source.',
            trailing: PrimaryButton(label: 'Upload', icon: Icons.upload_file, onPressed: () => context.go('/upload')),
          ),
          const SizedBox(height: 24),
          LayoutBuilder(
            builder: (context, constraints) {
              final columns = constraints.maxWidth > 860 ? 3 : 1;
              return GridView.count(
                crossAxisCount: columns,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                childAspectRatio: columns == 3 ? 2.8 : 4.5,
                mainAxisSpacing: 14,
                crossAxisSpacing: 14,
                children: [
                  MetricCard(label: 'Current document', value: document == null ? 'None' : document.kind.toUpperCase(), icon: Icons.description_outlined, color: accent),
                  MetricCard(label: 'Words ready for AI', value: '${document?.wordCount ?? 0}', icon: Icons.data_object_outlined, color: accentBlue),
                  const MetricCard(label: 'Study modes', value: '4', icon: Icons.school_outlined, color: Color(0xFFA78BFA)),
                ],
              );
            },
          ),
          const SizedBox(height: 18),
          GlassPanel(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  document == null ? 'Start with an upload' : document.title,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 8),
                Text(
                  document == null
                      ? 'NeuroLearn AI is ready for PDFs or pasted notes. Once content is uploaded, every feature lights up from the same document context.'
                      : 'This document is loaded into the workspace. Summary, quiz, insights, and chat are ready.',
                  style: const TextStyle(color: Color(0xFFB8C2DD), height: 1.55),
                ),
                const SizedBox(height: 18),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _ActionChip(label: 'Generate summary', icon: Icons.auto_awesome, path: '/summary', enabled: document != null),
                    _ActionChip(label: 'Build quiz', icon: Icons.quiz, path: '/quiz', enabled: document != null),
                    _ActionChip(label: 'Ask AI', icon: Icons.forum, path: '/chat', enabled: document != null),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionChip extends StatelessWidget {
  const _ActionChip({required this.label, required this.icon, required this.path, required this.enabled});
  final String label;
  final IconData icon;
  final String path;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      avatar: Icon(icon, size: 18, color: enabled ? accent : const Color(0xFF6B7280)),
      label: Text(label),
      onPressed: enabled ? () => context.go(path) : null,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8), side: const BorderSide(color: border)),
      backgroundColor: const Color(0xFF111827),
    );
  }
}

