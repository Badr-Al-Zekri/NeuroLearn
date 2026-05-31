import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/widgets/empty_state.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/loading_skeleton.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class SummaryScreen extends ConsumerWidget {
  const SummaryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final document = ref.watch(selectedDocumentProvider);
    if (document == null) {
      return const Center(child: EmptyState(title: 'No document loaded', message: 'Upload a PDF or text note before generating summaries.'));
    }
    final summary = ref.watch(summaryProvider(document.documentId));
    return SingleChildScrollView(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionHeader(title: 'Summary and insights', subtitle: document.title),
          const SizedBox(height: 20),
          summary.when(
            loading: () => const GlassPanel(child: LoadingSkeleton(lines: 7)),
            error: (error, _) => ErrorBanner(message: error.toString()),
            data: (data) => Column(
              children: [
                GlassPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(data.title, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
                      const SizedBox(height: 12),
                      Text(data.overview, style: const TextStyle(height: 1.6, color: Color(0xFFD7DFF3))),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                LayoutBuilder(
                  builder: (context, constraints) {
                    final wide = constraints.maxWidth > 820;
                    return Flex(
                      direction: wide ? Axis.horizontal : Axis.vertical,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: _ListCard(title: 'Key insights', icon: Icons.lightbulb_outline, items: data.keyInsights)),
                        SizedBox(width: wide ? 16 : 0, height: wide ? 0 : 16),
                        Expanded(child: _ListCard(title: 'Study actions', icon: Icons.check_circle_outline, items: data.studyActions)),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 16),
                GlassPanel(
                  child: Row(
                    children: [
                      const Icon(Icons.radar_outlined, color: accent),
                      const SizedBox(width: 12),
                      Expanded(child: Text(data.sourceCoverage, style: const TextStyle(color: Color(0xFFB8C2DD)))),
                      Text('${(data.confidence * 100).round()}%', style: const TextStyle(fontWeight: FontWeight.w900, color: accent)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ListCard extends StatelessWidget {
  const _ListCard({required this.title, required this.icon, required this.items});
  final String title;
  final IconData icon;
  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return GlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [Icon(icon, color: accent), const SizedBox(width: 10), Text(title, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18))]),
          const SizedBox(height: 14),
          for (final item in items)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.chevron_right, size: 16, color: accent),
                  const SizedBox(width: 6),
                  Expanded(child: Text(item, style: const TextStyle(color: Color(0xFFD7DFF3), height: 1.45))),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
