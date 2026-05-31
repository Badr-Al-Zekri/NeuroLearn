import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/providers/learning_session_provider.dart';
import 'package:neurolearn_ai/shared/providers/telemetry_provider.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/loading_skeleton.dart';
import 'package:neurolearn_ai/shared/widgets/primary_button.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class ProgressScreen extends ConsumerWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final snapshot = ref.watch(learnerSnapshotProvider);
    final session = ref.watch(activeStudySessionProvider);
    final telemetry = ref.watch(telemetryProvider);
    final completedSessions = telemetry.where((event) => event.name == 'session_completed').length;
    final sessionComplete = session.valueOrNull?.ended == true;
    final hasActiveSession = session.valueOrNull != null && !sessionComplete;
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 780),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionHeader(title: 'Progress', subtitle: 'Small focused sessions become lasting understanding.'),
              const SizedBox(height: 18),
              snapshot.when(
                loading: () => const GlassPanel(child: LoadingSkeleton(lines: 6)),
                error: (error, _) => ErrorBanner(
                  message: 'Your momentum summary is taking longer than expected.',
                  actionLabel: 'Try again',
                  onAction: () => ref.invalidate(learnerSnapshotProvider),
                ),
                data: (data) => Column(
                  children: [
                    GlassPanel(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(Icons.check_circle_outline, color: accent, size: 36),
                          const SizedBox(height: 12),
                          Text(
                            sessionComplete ? 'Today\'s focus session is complete.' : 'You\'re making steady progress.',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Showing up for a short, clear review is how knowledge starts to hold.',
                            style: TextStyle(color: Color(0xFFC7D1D3), height: 1.45),
                          ),
                          const SizedBox(height: 20),
                          LayoutBuilder(
                            builder: (context, constraints) {
                              final values = [
                                _ProgressValue(label: 'Streak', value: completedSessions > 0 ? '1 day' : 'Today'),
                                _ProgressValue(label: 'Sessions', value: '$completedSessions'),
                                _ProgressValue(label: 'Ideas', value: '${data.masteryCount}'),
                              ];
                              if (constraints.maxWidth < 470) {
                                return Column(
                                  children: [
                                    for (var index = 0; index < values.length; index++) ...[
                                      SizedBox(width: double.infinity, child: values[index]),
                                      if (index != values.length - 1) const SizedBox(height: 10),
                                    ],
                                  ],
                                );
                              }
                              return Row(
                                children: [
                                  for (var index = 0; index < values.length; index++) ...[
                                    Expanded(child: values[index]),
                                    if (index != values.length - 1) const SizedBox(width: 12),
                                  ],
                                ],
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),
                    GlassPanel(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Next gentle step', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900)),
                          const SizedBox(height: 9),
                          Text(
                            !sessionComplete
                                ? 'Finish today\'s quick review, then you can return tomorrow with a clean starting point.'
                                : data.weakConceptCount == 0
                                ? 'Come back tomorrow for another short session. Consistency matters more than volume.'
                                : 'Quick review before you forget this topic. A short revisit tomorrow will help it stick.',
                            style: const TextStyle(color: Color(0xFFD7E0E2), height: 1.48),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              SizedBox(
                width: double.infinity,
                child: PrimaryButton(
                  label: sessionComplete
                      ? 'Return to Today'
                      : hasActiveSession
                          ? 'Complete today\'s session'
                          : 'Start today\'s session',
                  icon: hasActiveSession ? Icons.done : Icons.arrow_forward,
                  loading: session.isLoading,
                  onPressed: hasActiveSession
                      ? () async {
                          await ref.read(activeStudySessionProvider.notifier).complete();
                          ref.invalidate(learnerSnapshotProvider);
                        }
                      : () => context.go('/'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProgressValue extends StatelessWidget {
  const _ProgressValue({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 10),
      decoration: BoxDecoration(color: surface, borderRadius: BorderRadius.circular(8)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 3),
          Text(label, style: const TextStyle(color: Color(0xFF99A6AB), fontSize: 12)),
        ],
      ),
    );
  }
}
