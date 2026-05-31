import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/providers/learning_session_provider.dart';
import 'package:neurolearn_ai/shared/widgets/empty_state.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/loading_skeleton.dart';
import 'package:neurolearn_ai/shared/widgets/primary_button.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class TodayScreen extends ConsumerWidget {
  const TodayScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final document = ref.watch(selectedDocumentProvider);
    if (document == null) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: EmptyState(
            title: 'Start with one learning source',
            message: 'Choose a PDF or paste notes. We will shape it into one clear session for today.',
            actionLabel: 'Choose material',
          ),
        ),
      );
    }

    final summary = ref.watch(summaryProvider(document.documentId));
    final session = ref.watch(activeStudySessionProvider);
    final activeSession = session.valueOrNull;
    final sessionInProgress = activeSession != null && !activeSession.ended;
    final guidance = sessionInProgress
        ? 'You are already underway. Continue with one clear question, then close with a short review.'
        : 'Begin with a guided explanation. A short review follows when the idea feels clear.';
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 780),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(
                title: 'Today',
                subtitle: 'One focused session from ${document.title}',
                trailing: TextButton(
                  onPressed: () => context.go('/upload'),
                  child: const Text('Change material'),
                ),
              ),
              const SizedBox(height: 20),
              if (session.hasError) ...[
                const ErrorBanner(message: 'We could not begin your session. Please try again.'),
                const SizedBox(height: 14),
              ],
              GlassPanel(
                padding: const EdgeInsets.all(24),
                child: summary.when(
                  loading: () => const LoadingSkeleton(lines: 6),
                  error: (error, _) => ErrorBanner(
                    message: 'We could not prepare today\'s focus. Please try again.',
                    actionLabel: 'Try again',
                    onAction: () => ref.invalidate(summaryProvider(document.documentId)),
                  ),
                  data: (data) => Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.schedule_outlined, color: accent, size: 18),
                          const SizedBox(width: 6),
                          const Text('18 minutes', style: TextStyle(color: accent, fontWeight: FontWeight.w800)),
                          const SizedBox(width: 14),
                          Text(sessionInProgress ? 'Session in progress' : 'Ready to begin', style: const TextStyle(color: Color(0xFF99A6AB))),
                        ],
                      ),
                      const SizedBox(height: 22),
                      Text('Your focus for today', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
                      const SizedBox(height: 10),
                      Text(data.overview, style: const TextStyle(color: Color(0xFFDCE3E5), height: 1.55)),
                      const SizedBox(height: 22),
                      Text('Keep these ideas close', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800)),
                      const SizedBox(height: 12),
                      for (final item in data.keyInsights.take(2))
                        Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.circle, color: accent, size: 8),
                              const SizedBox(width: 10),
                              Expanded(child: Text(item, style: const TextStyle(color: Color(0xFFE8EDED), height: 1.45))),
                            ],
                          ),
                        ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(color: surface, borderRadius: BorderRadius.circular(8)),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.lightbulb_outline, color: accent, size: 18),
                            const SizedBox(width: 10),
                            Expanded(child: Text(guidance, style: const TextStyle(color: Color(0xFFB5C1C4), height: 1.4))),
                          ],
                        ),
                      ),
                      const SizedBox(height: 22),
                      SizedBox(
                        width: double.infinity,
                        child: PrimaryButton(
                          label: sessionInProgress ? 'Continue learning' : 'Start today\'s session',
                          icon: Icons.arrow_forward,
                          loading: session.isLoading,
                          onPressed: () async {
                            if (!sessionInProgress) {
                              await ref.read(activeStudySessionProvider.notifier).start();
                            }
                            final currentSession = ref.read(activeStudySessionProvider);
                            if (context.mounted && !currentSession.hasError && currentSession.valueOrNull != null) {
                              context.go('/tutor');
                            }
                          },
                        ),
                      ),
                      const SizedBox(height: 10),
                      const Center(
                        child: Text('Next: a clear explanation, then a quick review.', style: TextStyle(color: Color(0xFF99A6AB), fontSize: 13)),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
